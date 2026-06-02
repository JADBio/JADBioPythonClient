class Cox:
    l = 0

    def __init__(self, l: float):
        self.l = l

    def to_dict(self):
        return {'type': 'CoxRegressionModelTrainer', 'l': self.l}