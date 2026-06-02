from jadbio.ml.tuning import preprocessing_strategy, fs_strategy, model_strategy
from jadbio.ml.tuning.fs_strategy import FSStrategy, FSPreference
from jadbio.ml.tuning.model_strategy import ModelStrategy
from jadbio.ml.tuning.preprocessing_strategy import PreprocessingStrategy


def auto():
    return AutoTuning()

def random():
    return RandomTuning()


def hpo(n_configurations: int = None, explore_as_grid: bool = None, bayesian_prefs=None, fs_preference=None, fs_blacklist=None):
    return HpoTuning(n_configurations, explore_as_grid, bayesian_prefs, fs_preference, fs_blacklist)


def auto_with_fs_blacklist(fs_blacklist):
    return Guided(
        preprocessing_strategy.auto(),
        fs_strategy.ai_supplementary(FSPreference.FS, 25, 5, fs_blacklist),
        model_strategy.auto()
    )


# Perform ai based preprocessing and modeling but custom fs,
# Takes as argument list of feature selectors
def custom_fs(feature_selectors):
    return Guided(
        preprocessing_strategy.auto(),
        fs_strategy.static(feature_selectors),
        model_strategy.auto()
    )


# Perform AI based preprocessing and fs but custom models,
# Takes as argument list of models
def custom_models(models):
    return Guided(
        preprocessing_strategy.auto(),
        fs_strategy.auto(),
        model_strategy.static(models)
    )

def custom_fs_and_models(feature_selectors, models):
    return Guided(
        preprocessing_strategy.auto(),
        fs_strategy.static(feature_selectors),
        model_strategy.static(models)
    )

def custom(configurations):
    return Static(configurations)


class TuningParams:
    def to_dict(self):
        pass

    @staticmethod
    def auto():
        return AutoTuning()


class AutoTuning(TuningParams):
    def to_dict(self):
        return {
            'type': 'auto'
        }

class RandomTuning(TuningParams):
    def to_dict(self):
        return {
            'type': 'random'
        }


class HpoTuning(TuningParams):
    n_configurations: int = None
    explore_as_grid: bool = None
    bayesian_prefs = None
    fs_preference = None
    fs_blacklist = None

    def __init__(self, n_configurations: int = None, explore_as_grid: bool = None, bayesian_prefs=None,
                 fs_preference=None, fs_blacklist=None):
        self.n_configurations = n_configurations
        self.explore_as_grid = explore_as_grid
        self.bayesian_prefs = bayesian_prefs
        self.fs_preference = fs_preference
        self.fs_blacklist = fs_blacklist

    @staticmethod
    def __serialize_fs_preference__(fs_preference):
        if fs_preference is None:
            return FSPreference.FS.value
        if isinstance(fs_preference, FSPreference):
            return fs_preference.value
        if isinstance(fs_preference, str):
            normalized = fs_preference.upper()
            allowed_values = {member.value for member in FSPreference}
            if normalized in allowed_values:
                return normalized
            raise ValueError('Unsupported fs_preference: {}'.format(fs_preference))
        if isinstance(fs_preference, bool):
            return FSPreference.FS.value if fs_preference else FSPreference.NO_FS.value
        raise ValueError('Unsupported fs_preference: {}'.format(fs_preference))

    def to_dict(self):
        return {
            'type': 'hpo',
            'configurationsSize': self.n_configurations,
            'gridExplore': self.explore_as_grid,
            'bayesianPreferences': self.bayesian_prefs,
            'fsPreference': HpoTuning.__serialize_fs_preference__(self.fs_preference),
            'fsBlackList': [] if self.fs_blacklist is None else self.fs_blacklist
        }


class Guided(TuningParams):
    pp_strategy: PreprocessingStrategy
    fs_strategy: FSStrategy
    model_strategy: ModelStrategy

    def __init__(self,
                 pp_strategy: PreprocessingStrategy,
                 fs_strategy_param: FSStrategy,
                 model_strategy_param: ModelStrategy
                 ):
        self.pp_strategy = pp_strategy
        self.fs_strategy = fs_strategy_param
        self.model_strategy = model_strategy_param

    def to_dict(self):
        return {
            'type': 'guided',
            'preprocessingParams': self.pp_strategy.to_dict(),
            'fsTuningParams': self.fs_strategy.to_dict(),
            'modelTuningParams': self.model_strategy.to_dict()
        }


class Static(TuningParams):
    configurations = None

    def __init__(self, configurations):
        if configurations is None or len(configurations) == 0:
            raise 'invalid configurations'
        self.configurations = configurations

    def to_dict(self):
        return {
            'type': 'static',
            'configurations': [c.to_dict() for c in self.configurations]
        }
