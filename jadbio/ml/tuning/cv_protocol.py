def custom_cv(repeats: int, folds: int = None):
    return CV(repeats, folds)

class CVProtocol:
    pass


class HoldOut(CVProtocol):
    def to_dict(self):
        return {
            'type': 'holdout'
        }


class IncompleteCV(CVProtocol):
    def to_dict(self):
        return {
            'type': 'incompleteCV'
        }


class CV(CVProtocol):
    repeats: int
    folds: int

    def __init__(self, repeats: int = None, folds: int = None):
        self.repeats = repeats
        self.folds = folds

    def to_dict(self):
        return {
            'type': 'cv',
            'folds': self.folds,
            'repeats': self.repeats
        }
