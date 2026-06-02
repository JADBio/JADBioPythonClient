from jadbio.ml.tuning import tuning_params, cv_params
from jadbio.ml.tuning.cv_params import CVParams
from jadbio.ml.tuning.tuning_params import TuningParams


def plots_from_analysis_type(type):
    if type == 'CLASSIFICATION':
        return ['Roc', 'Ice', 'Probabilities', 'Pca', 'UMAP']
    return []


def classification(target: str, tuning: str, concurrency: int):
    """

    :param target:
    :param tuning: 'QUICK' | 'NORMAL' | 'EXTENSIVE'
    :param concurrency: 1-24
    :return:
    """
    return AnalysisForm(
        target, target, 'CLASSIFICATION', 'STANDARD', tuning, concurrency
    )


def regression(target: str, tuning: str, concurrency: int):
    """

    :param target:
    :param tuning: 'QUICK' | 'NORMAL' | 'EXTENSIVE'
    :param concurrency: 1-24
    :return:
    """
    return AnalysisForm(
        target, target, 'REGRESSION', 'STANDARD', tuning, concurrency
    )


def survival(target: str, tuning: str, concurrency: int):
    """

    :param target:
    :param tuning: 'QUICK' | 'NORMAL' | 'EXTENSIVE'
    :param concurrency: 1-24
    :return:
    """
    return AnalysisForm(
        target, target, 'SURVIVAL', 'STANDARD', tuning, concurrency
    )


def testing(target: str, tuning: str, concurrency: int, tuning_params):
    return AnalysisForm(title=target, target=target, analysis_type=None, dataset_type='STANDARD', tuning_level=tuning,
                        concurrency=concurrency,
                        cv_args=cv_params.auto().with_disabled_progress_update().with_best_model_rule(),
                        tuning=tuning_params, plots=[])


class AnalysisForm:
    target = None
    analysis_type = None  # STANDARD or DISTANCE
    dataset_type = None
    tuning_args: TuningParams = None
    cv_args: CVParams = None
    tuning_level = None
    concurrency = 1
    timeout = 1000000000
    title = None
    plots = []

    def __init__(
            self,
            title,
            target,
            analysis_type: str,
            dataset_type: str,
            tuning_level,
            concurrency,
            cv_args=cv_params.auto(),
            tuning=tuning_params.auto(),
            plots=None
    ):
        self.title = title
        self.target = target
        self.analysis_type = analysis_type
        self.dataset_type = dataset_type
        self.tuning_level = tuning_level
        self.concurrency = concurrency
        self.plots = plots_from_analysis_type(analysis_type) if plots is None else plots
        self.tuning_args = tuning
        self.cv_args = cv_args

    def with_cv_params(self, cv_conf: CVParams):
        return AnalysisForm(
            title=self.title,
            target=self.target,
            analysis_type=self.analysis_type,
            dataset_type=self.dataset_type,
            tuning_level=self.tuning_level,
            concurrency=self.concurrency,
            cv_args=cv_conf,
            tuning=self.tuning_args,
            plots=self.plots
        )

    def with_tuning_strategy(self, tuning_strategy):
        return AnalysisForm(
            title=self.title,
            target=self.target,
            analysis_type=self.analysis_type,
            dataset_type=self.dataset_type,
            tuning_level=self.tuning_level,
            concurrency=self.concurrency,
            cv_args=self.cv_args,
            tuning=tuning_strategy,
            plots=self.plots
        )

    def with_title(self, title):
        return AnalysisForm(
            title=title,
            target=self.target,
            analysis_type=self.analysis_type,
            dataset_type=self.dataset_type,
            tuning_level=self.tuning_level,
            concurrency=self.concurrency,
            cv_args=self.cv_args,
            tuning=self.tuning_args,
            plots=self.plots
        )

    def with_distance_dataset(self):
        return AnalysisForm(
            title=self.title,
            target=self.target,
            analysis_type=self.analysis_type,
            dataset_type='DISTANCE',
            tuning_level=self.tuning_level,
            concurrency=self.concurrency,
            cv_args=self.cv_args,
            tuning=self.tuning_args,
            plots=self.plots
        )

    def with_plots(self, plots):
        return AnalysisForm(
            title=self.title,
            target=self.target,
            analysis_type=self.analysis_type,
            dataset_type=self.dataset_type,
            tuning_level=self.tuning_level,
            concurrency=self.concurrency,
            cv_args=self.cv_args,
            tuning=self.tuning_args,
            plots=plots
        )

    def to_dict(self):
        return {
            'title': self.title,
            'target': self.target,
            'analysisType': self.analysis_type,
            'datasetType': self.dataset_type,
            'tuningEffort': self.tuning_level,
            'coreCount': self.concurrency,
            'plots': self.plots,
            'timeout': self.timeout,
            'cvPreferences': self.cv_args.to_dict() if self.cv_args is not None else None,
            'tuningParams': self.tuning_args.to_dict() if self.tuning_args is not None else None
        }
