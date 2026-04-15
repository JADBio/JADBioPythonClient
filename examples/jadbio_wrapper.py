import os
import subprocess
import pandas as pd
import numpy as np
import uuid
import tempfile
from pathlib import Path
from typing import List, Union, Optional

class JADBioWrapper:
    """
    A Python wrapper for the JADBio Java model.
    Mimics the scikit-learn 'predict' interface for compatibility with SHAP.
    """
    
    def __init__(
        self, 
        model_path: str, 
        jar_path: str, 
        feature_names: List[str],
        temp_dir: Optional[str] = None
    ):
        """
        Initialize the wrapper.
        
        Args:
            model_path: Path to the JADBio model (.json)
            jar_path: Path to the jadbio-model-exe.jar
            feature_names: List of feature names in the correct order
            temp_dir: Directory for temporary CSV files
        """
        self.model_path = Path(model_path).resolve()
        self.jar_path = Path(jar_path).resolve()
        self.feature_names = feature_names
        self.temp_dir = Path(temp_dir) if temp_dir else Path(tempfile.gettempdir())
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found: {self.model_path}")
        if not self.jar_path.exists():
            raise FileNotFoundError(f"JAR file not found: {self.jar_path}")
        if not self._looks_like_jar(self.jar_path):
            raise ValueError(f"Downloaded file is not a valid JAR/ZIP archive: {self.jar_path}")
        
        # Scikit-learn compatibility (for permutation_importance and PartialDependenceDisplay)
        self._estimator_type = "regressor" # JADBio models are usually regressor-like (returning values)
        self.fitted_ = True

    def fit(self, X, y=None):
        """Dummy fit method to satisfy scikit-learn validation."""
        self.fitted_ = True
        return self

    def score(self, X, y):
        """Score method for scikit-learn compatibility."""
        from sklearn.metrics import r2_score, accuracy_score,roc_auc_score
        preds = self.predict(X)
        
        # Determine if it's classification or regression based on target
        # JADBio predictions are often continuous even for classification (probabilities)
        # or discrete. 
        unique_y = np.unique(y)
        if len(unique_y) <= 10: # Heuristic for classification
            # If preds are continuous, convert to classes for accuracy if needed
            # But JADBio's 'Prediction' column usually contains labels.
            if False:
                pass
            else:
                try:
                    if preds.dtype.kind in 'fc': # float or complex
                        # Check if they look like probabilities or classes
                        if np.all((preds >= 0) & (preds <= 1)) and not np.all(np.isin(preds, [0, 1])):
                            preds_labeled = (preds > 0.44).astype(int)
                            acc_score =accuracy_score(y, preds_labeled)
                            return acc_score
                        acc_score = accuracy_score(y, preds)
                        return acc_score
                except:
                    acc_score = accuracy_score(y, (preds > 0.5).astype(int))
                    return acc_score
        else:
            return r2_score(y, preds)

    @staticmethod
    def _extract_predictions(df_output: pd.DataFrame) -> np.ndarray:
        """Extract the prediction vector from a JADBio output CSV."""
        preferred_columns = ["Prediction", "Predicted Value"]
        for column in preferred_columns:
            if column in df_output.columns:
                return df_output[column].to_numpy()

        ignored_columns = {
            "Sample name",
            "Samples",
            "Sample",
            "Row ID",
            "RowID",
            "ID",
        }
        candidate_columns = [col for col in df_output.columns if col not in ignored_columns]
        if not candidate_columns:
            raise RuntimeError(
                f"Could not find a prediction column in JADBio output: {list(df_output.columns)}"
            )

        return df_output[candidate_columns[-1]].to_numpy()

    @staticmethod
    def _looks_like_jar(path: Path) -> bool:
        """Basic JAR validation based on the ZIP file signature."""
        try:
            with path.open("rb") as handle:
                return handle.read(2) == b"PK"
        except OSError:
            return False

    def predict(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """
        Predict method for SHAP compatibility.
        
        Args:
            X: Feature matrix (NumPy array or Pandas DataFrame)
            
        Returns:
            NumPy array of predictions
        """
        # Convert X to DataFrame to ensure correct column order and headers
        if isinstance(X, np.ndarray):
            if X.shape[1] != len(self.feature_names):
                raise ValueError(
                    f"Number of features in X ({X.shape[1]}) does not match "
                    f"number of feature names ({len(self.feature_names)})"
                )
            df_input = pd.DataFrame(X, columns=self.feature_names)
        elif isinstance(X, pd.DataFrame):
            # Reorder columns to match expected feature names
            df_input = X[self.feature_names]
        else:
            raise TypeError("Input must be a NumPy array or a Pandas DataFrame")
            
        # Create a unique ID for this execution to avoid collisions
        exec_id = str(uuid.uuid4())
        input_csv = self.temp_dir / f"input-{exec_id}.csv"
        output_csv = self.temp_dir / f"output-{exec_id}.csv"
        
        try:
            # Add 'Sample name' as the first column (required by JADBio executable)
            df_input_with_index = df_input.copy()
            sample_names = [f"row{i}" for i in range(len(df_input_with_index))]
            df_input_with_index.insert(0, "Samples", sample_names)
            
            # Save input to CSV
            df_input_with_index.to_csv(input_csv, index=False)
            
            # Construct the Java command
            # Template: java --enable-preview -jar jadbio-model-exe.jar -m jad-model.json -i iris.csv -o pred-iris.csv
            cmd = [
                "java",
                "--enable-preview",
                "-jar", str(self.jar_path),
                "-m", str(self.model_path),
                "-i", str(input_csv),
                "-o", str(output_csv)
            ]
            
            # Execute the command
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                check=True
            )
            
            # Check if output CSV was created
            if not output_csv.exists():
                raise RuntimeError(
                    f"Java execution failed to produce output. Stdout: {result.stdout}\nStderr: {result.stderr}"
                )
            
            # Read predictions
            df_output = pd.read_csv(output_csv)
            return self._extract_predictions(df_output)
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Java execution failed (exit code {e.returncode}): {e.stderr}") from e
        except Exception as e:
            raise RuntimeError(f"Error during JADBio prediction: {e}") from e
        finally:
            # Cleanup temporary files
            if input_csv.exists():
                os.remove(input_csv)
            if output_csv.exists():
                os.remove(output_csv)

    def predict_proba(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """
        Optional: predict_proba for classification if SHAP needs it.
        JADBio output usually contains probabilities for each class.
        """
        # Implementation depends on JADBio's output format for probabilities.
        # For KernelExplainer, 'predict' is often sufficient if it returns continuous values.
        # If JADBio returns class labels in 'predict', we'd need 'predict_proba'.
        # Let's start with 'predict' and see if SHAP is happy.
        return self.predict(X)
