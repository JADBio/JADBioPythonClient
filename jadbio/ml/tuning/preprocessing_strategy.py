def ai_supplementary(prep_list, order='FIRST'):
    return AISupplementaryPreprocessing(prep_list, order)


def auto():
    return AutoPreprocessing()


class PreprocessingStrategy:
    pass


class AISupplementaryPreprocessing(PreprocessingStrategy):
    prep_list = None
    order = None

    def __init__(self, prep_list, order):
        self.prep_list = prep_list
        self.order = order

    def to_dict(self):
        return {
            'type': 'extended',
            'order': self.order,
            'extraPreprocessors': [e.to_dict() for e in self.prep_list]
        }


class AutoPreprocessing(PreprocessingStrategy):
    def to_dict(self):
        return {
            'type': 'auto'
        }
