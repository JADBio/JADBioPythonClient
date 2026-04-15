class Ridge:
    l = 0

    def __init__(self, l):
        self.l = l

    def to_dict(self):
        return {'type': 'LinearRegressionModelTrainer', 'l': self.l}