import numpy as np
import pandas as pd
from typing import Dict, Callable, Union


class DataTransformer:
    """
    A class to apply and manage data transformations consistently across datasets.
    """
    
    BUILTIN_TRANSFORMS = {
        'log': np.log,
        'log10': np.log10,
        'sqrt': np.sqrt,
        'exp': np.exp,
        'square': lambda x: x ** 2,
        'cube': lambda x: x ** 3,
        'reciprocal': lambda x: 1 / x,
        'abs': np.abs,
    }

    BUILTIN_INVERSE_TRANSFORMS = {
        'log': np.exp,
        'log10': lambda x: 10 ** x,
        'sqrt': lambda x: x ** 2,
        'exp': np.log,
        'square': np.sqrt,
        'cube': lambda x: np.cbrt(x),
        'reciprocal': lambda x: 1 / x,
        'abs': np.abs,
    }
    
    def __init__(
        self,
        transformations: Dict[str, Union[str, Callable]],
        inverse_transformations: Dict[str, Union[str, Callable]] = None
    ):
        """
        Initialize the transformer with a dictionary of transformations.
        
        Args:
            transformations: Dict mapping variable names to transformation functions or string names
            inverse_transformations: Optional dict mapping variable names to inverse
                transformation functions or string names
        """
        self.transformations = transformations
        self.inverse_transformations = inverse_transformations or {}
        self._resolve_transforms()
    
    def _resolve_transforms(self):
        """Resolve string transformation names to actual functions for both directions."""
        resolved = {}
        resolved_inverse = {}
        for var_name, transform in self.transformations.items():
            if isinstance(transform, str):
                if transform in self.BUILTIN_TRANSFORMS:
                    resolved[var_name] = self.BUILTIN_TRANSFORMS[transform]
                    if var_name not in self.inverse_transformations:
                        resolved_inverse[var_name] = self.BUILTIN_INVERSE_TRANSFORMS[transform]
                else:
                    raise ValueError(f"Unknown transformation: {transform}")
            elif callable(transform):
                resolved[var_name] = transform
            else:
                raise TypeError(f"Transformation must be string or callable, got {type(transform)}")

        for var_name, transform in self.inverse_transformations.items():
            if isinstance(transform, str):
                if transform in self.BUILTIN_TRANSFORMS:
                    resolved_inverse[var_name] = self.BUILTIN_TRANSFORMS[transform]
                elif transform in self.BUILTIN_INVERSE_TRANSFORMS:
                    resolved_inverse[var_name] = self.BUILTIN_INVERSE_TRANSFORMS[transform]
                else:
                    raise ValueError(f"Unknown inverse transformation: {transform}")
            elif callable(transform):
                resolved_inverse[var_name] = transform
            else:
                raise TypeError(f"Inverse transformation must be string or callable, got {type(transform)}")

        self.transformations = resolved
        self.inverse_transformations = resolved_inverse

    def _apply_transformations(
        self,
        data: Union[pd.DataFrame, pd.Series, np.ndarray],
        transformations: Dict[str, Callable]
    ) -> Union[pd.DataFrame, pd.Series, np.ndarray]:
        """Apply a set of transformations to tabular or array-like data."""
        if isinstance(data, pd.DataFrame):
            result = data.copy()
            for var_name, transform_func in transformations.items():
                if var_name in result.columns:
                    result[var_name] = transform_func(result[var_name])
                else:
                    raise ValueError(f"Column '{var_name}' not found in DataFrame")
            return result

        if isinstance(data, pd.Series):
            if len(transformations) != 1:
                raise ValueError("Series inverse/transform requires exactly one configured transformation")
            transform_func = next(iter(transformations.values()))
            return transform_func(data.copy())

        if isinstance(data, np.ndarray):
            if len(transformations) != 1:
                raise ValueError("NumPy array inverse/transform requires exactly one configured transformation")
            transform_func = next(iter(transformations.values()))
            return transform_func(np.array(data, copy=True))

        raise TypeError(f"Data must be a pandas DataFrame/Series or NumPy array, got {type(data)}")
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Apply transformations to a DataFrame.
        
        Args:
            data: Input DataFrame
            
        Returns:
            DataFrame with transformations applied
        """
        return self._apply_transformations(data, self.transformations)

    def transform_file(self, input_path: str, output_path: str, **read_csv_kwargs) -> pd.DataFrame:
        """
        Read a CSV file, apply configured transformations, and write the result.

        Args:
            input_path: Path to the input CSV file
            output_path: Path where the transformed CSV will be saved
            read_csv_kwargs: Extra keyword arguments forwarded to pandas.read_csv

        Returns:
            The transformed DataFrame
        """
        data = pd.read_csv(input_path, **read_csv_kwargs)
        transformed = self.transform(data)
        transformed.to_csv(output_path, index=False)
        return transformed
    
    def inverse_transform(
        self,
        data: Union[pd.DataFrame, pd.Series, np.ndarray],
        inverse_transforms: Dict[str, Union[str, Callable]] = None
    ) -> Union[pd.DataFrame, pd.Series, np.ndarray]:
        """
        Apply inverse transformations to a DataFrame.
        
        Args:
            data: Input DataFrame
            inverse_transforms: Optional dict mapping variable names to inverse
                transformation functions. If omitted, the class-level inverse
                transformations are used.
            
        Returns:
            DataFrame with inverse transformations applied
        """
        if inverse_transforms is None:
            transforms_to_apply = self.inverse_transformations
        else:
            temp_transformer = DataTransformer({}, inverse_transformations=inverse_transforms)
            transforms_to_apply = temp_transformer.inverse_transformations

        if not transforms_to_apply:
            raise ValueError("No inverse transformations are configured")

        return self._apply_transformations(data, transforms_to_apply)

    def inverse_transform_file(
        self,
        input_path: str,
        output_path: str,
        inverse_transforms: Dict[str, Union[str, Callable]] = None,
        **read_csv_kwargs
    ) -> pd.DataFrame:
        """
        Read a CSV file, apply inverse transformations, and write the result.

        Args:
            input_path: Path to the input CSV file
            output_path: Path where the inverse-transformed CSV will be saved
            inverse_transforms: Optional dict mapping variable names to inverse
                transformation functions
            read_csv_kwargs: Extra keyword arguments forwarded to pandas.read_csv

        Returns:
            The inverse-transformed DataFrame
        """
        data = pd.read_csv(input_path, **read_csv_kwargs)
        restored = self.inverse_transform(data, inverse_transforms)
        restored.to_csv(output_path, index=False)
        return restored
