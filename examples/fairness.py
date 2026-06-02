import numpy as np
import pandas as pd
import warnings


class Fairness:
    """
    The main arguments of the functions in the Fairness class are
        target: the target variable of the analysis
        oos_predictions: the out-of-sample predictions of the CV process
        folds: the fold membership of each sample
        metric: the performance metric used in the analysis, although other metrics can be tried as well
        fairness_cat: the variable, for which we want to check for performance bias

    The output variables of the functions are
        categories: the categories of the variable, for which we want to check for performance bias
        performances: the performance by category
        original_var: the variance of performance values for the various categories, used in the bootstrap testing procedure
        bootstrap_vars: the variance of the bootstrapped performance values for the various categories, used in the bootstrap
                    testing procedure
        p_value: the p-value of the test for equality of performances
    """

    def __init__(self, target, oos_predictions, folds, metric):
        self.target = np.asarray(target)
        self.oos_predictions = np.asarray(oos_predictions)
        self.folds = np.asarray(folds)
        self.metric = metric

    def metric_per_cat(self, fairness_cat):
        fairness_cat = np.asarray(fairness_cat)
        categories = sorted(set(fairness_cat))
        performances = []

        for c in categories:
            fold_metric = []
            fold_size = []
            category_mask = fairness_cat == c
            target_cat = self.target[category_mask]
            oos_cat = self.oos_predictions[category_mask]
            folds_cat = self.folds[category_mask]

            for f in sorted(set(folds_cat)):
                fold_mask = folds_cat == f
                target_cat_fold = target_cat[fold_mask]
                oos_cat_fold = oos_cat[fold_mask]
                if len(target_cat_fold) == 0:
                    continue

                fold_value = compute_metric_value(
                    self.metric,
                    target_cat_fold,
                    squeeze_predictions(oos_cat_fold),
                )
                if fold_value is None:
                    continue

                fold_metric.append(fold_value)
                fold_size.append(len(target_cat_fold))

            if len(fold_metric) == 0 or np.sum(fold_size) == 0:
                performances.append(np.nan)
            else:
                performances.append(np.average(a=fold_metric, weights=fold_size))

        return categories, performances

    def bootstrap_test(self, fairness_cat, iterations):
        fairness_cat = np.asarray(fairness_cat)
        original_performances = np.asarray(self.metric_per_cat(fairness_cat)[1], dtype=float)
        original_var = safe_nanvar(original_performances)
        bootstrap_vars = []

        for _ in range(iterations):
            bootstrapped_fairness_cat = np.random.choice(a=fairness_cat, size=len(fairness_cat), replace=False)
            bootstrapped_performances = np.asarray(self.metric_per_cat(bootstrapped_fairness_cat)[1], dtype=float)
            bootstrap_vars.append(safe_nanvar(bootstrapped_performances))

        bootstrap_vars = np.asarray(bootstrap_vars, dtype=float)
        finite_bootstrap_vars = bootstrap_vars[np.isfinite(bootstrap_vars)]
        if len(finite_bootstrap_vars) == 0:
            p_value = np.nan
        else:
            p_value = np.mean(finite_bootstrap_vars >= original_var)

        return original_var, bootstrap_vars, p_value


def print_value_and_shape(name, value):
    value_array = np.asarray(value)
    print(f"{name}: {value} : shape: {value_array.shape}")


def safe_nanvar(values):
    values = np.asarray(values, dtype=float)
    finite_values = values[np.isfinite(values)]
    if len(finite_values) == 0:
        return np.nan
    return np.var(finite_values)


def compute_metric_value(metric, y_true, y_pred):
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            metric_value = metric(y_true, y_pred)
    except (ValueError, TypeError, ZeroDivisionError):
        return None

    metric_array = np.asarray(metric_value, dtype=float)
    if metric_array.ndim != 0:
        return None

    metric_value = float(metric_array)
    if not np.isfinite(metric_value):
        return None

    return metric_value


def normalize_prediction_matrix(prediction_matrix):
    prediction_matrix = np.asarray(prediction_matrix)
    if prediction_matrix.ndim == 1:
        prediction_matrix = prediction_matrix[:, np.newaxis]
    if prediction_matrix.ndim not in (2, 3):
        raise ValueError(
            "prediction_matrix must have shape (n_samples, n_prediction_sets) or "
            f"(n_samples, n_prediction_sets, n_prediction_values), got {prediction_matrix.shape}"
        )
    return prediction_matrix


def squeeze_predictions(predictions):
    predictions = np.asarray(predictions)
    if predictions.ndim == 2 and predictions.shape[1] == 1:
        return predictions[:, 0]
    return predictions


def is_complete_partition(split_block, sample_count):
    merged = []
    for indices in split_block:
        merged.extend(indices)

    if len(merged) != sample_count:
        return False

    return sorted(merged) == list(range(sample_count))


def infer_folds_per_repetition(split_indices, sample_count):
    total_splits = len(split_indices)
    if total_splits == 0:
        raise ValueError("split_indices cannot be empty")

    valid_candidates = []
    for folds_per_repetition in range(1, total_splits + 1):
        if total_splits % folds_per_repetition != 0:
            continue

        repetition_count = total_splits // folds_per_repetition
        if all(
            is_complete_partition(
                split_indices[
                    repetition_index * folds_per_repetition:(repetition_index + 1) * folds_per_repetition
                ],
                sample_count,
            )
            for repetition_index in range(repetition_count)
        ):
            valid_candidates.append(folds_per_repetition)

    if not valid_candidates:
        raise ValueError(
            "Could not infer folds_per_repetition from split_indices. "
            "Expected splits to be grouped into complete sample partitions."
        )

    return min(valid_candidates)


def describe_cv_layout(split_indices, prediction_matrix):
    prediction_matrix = normalize_prediction_matrix(prediction_matrix)

    if len(split_indices) == 0:
        raise ValueError("split_indices cannot be empty")

    sample_count = prediction_matrix.shape[0]
    folds_per_repetition = infer_folds_per_repetition(split_indices, sample_count)
    planned_repetitions = len(split_indices) // folds_per_repetition
    realized_repetitions = prediction_matrix.shape[1]
    usable_repetitions = min(planned_repetitions, realized_repetitions)
    usable_split_count = usable_repetitions * folds_per_repetition

    if usable_repetitions == 0:
        raise ValueError("No usable repetitions were found in the prediction matrix")

    cv_layout = {
        'planned_repetitions': planned_repetitions,
        'realized_repetitions': realized_repetitions,
        'usable_repetitions': usable_repetitions,
        'folds_per_repetition': folds_per_repetition,
        'usable_split_count': usable_split_count,
        'sample_count': sample_count,
        'prediction_ndim': prediction_matrix.ndim,
    }
    return cv_layout


def extract_fold_predictions(split_indices, prediction_matrix, cv_layout):
    prediction_matrix = normalize_prediction_matrix(prediction_matrix)

    fold_predictions = []
    for fold_index, indices in enumerate(split_indices[:cv_layout['usable_split_count']]):
        repetition_index = fold_index // cv_layout['folds_per_repetition']
        fold_predictions.append(prediction_matrix[indices, repetition_index, ...])
    return fold_predictions


def select_reference_splits(split_indices, cv_layout):
    selected_splits = split_indices[:cv_layout['usable_split_count']]
    return selected_splits


def build_reference_predictions(selected_splits, prediction_matrix):
    prediction_matrix = normalize_prediction_matrix(prediction_matrix)
    sample_count = prediction_matrix.shape[0]
    folds_per_repetition = infer_folds_per_repetition(selected_splits, sample_count)
    usable_repetitions = len(selected_splits) // folds_per_repetition

    reference_predictions = []
    for fold_index, indices in enumerate(selected_splits):
        repetition_index = fold_index // folds_per_repetition
        if repetition_index >= usable_repetitions:
            break
        reference_predictions.append(prediction_matrix[indices, repetition_index, ...])

    if not reference_predictions:
        raise ValueError("No predictions were assigned for the selected splits")

    reference_predictions = np.concatenate(reference_predictions, axis=0)
    return squeeze_predictions(reference_predictions)


def build_fold_membership(selected_splits, sample_count):

    folds_per_repetition = infer_folds_per_repetition(selected_splits, sample_count)
    fold_ids = []
    for fold_index, indices in enumerate(selected_splits):
        repetition_index = fold_index // folds_per_repetition
        fold_in_repetition = fold_index % folds_per_repetition
        global_fold_id = repetition_index * folds_per_repetition + fold_in_repetition
        fold_ids.extend([global_fold_id] * len(indices))

    folds = np.asarray(fold_ids, dtype=int)
    return folds


def build_fairness_categories(dataset, fairness_column):
    unique_values = dataset[fairness_column].nunique(dropna=False)
    if unique_values > 10:
        raise ValueError(
            f"Fairness column '{fairness_column}' has {unique_values} unique values. "
            "Please choose a column with at most 10 unique values."
        )
    fairness_values = dataset[fairness_column].to_numpy()
    return fairness_values


def expand_target_over_splits(target, selected_splits):
    expanded_target = [np.asarray(target)[indices] for indices in selected_splits]
    if not expanded_target:
        raise ValueError("No target values were assigned for the selected splits")
    return np.concatenate(expanded_target, axis=0)


def expand_fairness_categories_over_splits(fairness_values, selected_splits):
    expanded_fairness_values = [np.asarray(fairness_values)[indices] for indices in selected_splits]
    if not expanded_fairness_values:
        raise ValueError("No fairness categories were assigned for the selected splits")
    return np.concatenate(expanded_fairness_values, axis=0)


def prepare_fairness(
    detailed_result,
    dataset_path,
    fairness_column='variable1',
):
    dataset = pd.read_csv(dataset_path)

    target = np.asarray(detailed_result['targetData']['data'])
    best_model_description = detailed_result['bestModel']
    prediction_matrix = np.asarray(detailed_result['oosPredictions']['predictions'][best_model_description])
    prediction_matrix = normalize_prediction_matrix(prediction_matrix)

    cv_layout = describe_cv_layout(detailed_result['splitIndices'], prediction_matrix)
    all_fold_predictions = extract_fold_predictions(
        detailed_result['splitIndices'],
        prediction_matrix,
        cv_layout,
    )

    reference_splits = select_reference_splits(
        detailed_result['splitIndices'],
        cv_layout,
    )
    oos_predictions = build_reference_predictions(reference_splits, prediction_matrix)

    expanded_target = expand_target_over_splits(target, reference_splits)

    folds = build_fold_membership(
        reference_splits,
        len(target),
    )

    fairness_values = build_fairness_categories(dataset, fairness_column=fairness_column)
    fairness_cat = expand_fairness_categories_over_splits(fairness_values, reference_splits)

    return {
        'detailed_result': detailed_result,
        'analysis_type': detailed_result['type'],
        'target_name': detailed_result['targetData']['name'],
        'fairness_column': fairness_column,
        'best_model_description': best_model_description,
        'target': expanded_target,
        'oos_predictions': oos_predictions,
        'all_fold_predictions': all_fold_predictions,
        'cv_layout': cv_layout,
        'folds': folds,
        'fairness_cat': fairness_cat,
    }
