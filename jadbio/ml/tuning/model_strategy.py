def auto():
    return Auto()


def random():
    return Random(None)


def static(models):
    return Static(models)


def extended(only_interpretable: bool, extra_models=None):
    return AIExtended(only_interpretable, extra_models)


class ModelStrategy:
    pass


class Auto(ModelStrategy):
    def to_dict(self):
        return {
            'type': 'auto'
        }


class AIExtended(ModelStrategy):
    only_interpretable: bool
    extra_models = None

    def __init__(self, only_interpretable: bool, extra_models):
        self.only_interpretable = only_interpretable
        self.extra_models = extra_models

    def to_dict(self):
        return {
            'type': 'extended',
            'onlyInterpretable': self.only_interpretable,
            'extraModels': self.extra_models
        }


class Static(ModelStrategy):
    models = None

    def __init__(self, models):
        if models is None or len(models) == 0:
            raise 'Empty models param'
        self.models = models

    def to_dict(self):
        return {
            'type': 'static',
            'models': [m.to_dict() for m in self.models]
        }


class Random(ModelStrategy):
    modelBlackList = None

    def __init__(self, modelBlackList):
        self.modelBlackList = modelBlackList

    def to_dict(self):
        return {
            'type': 'random',
            'modelBlackList': self.modelBlackList
        }
