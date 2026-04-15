class Logistic:
    l = 0

    def __init__(self, l):
        """
        :param l: lambda
        """
        self.l = l

    def to_dict(self):
        return {'type': 'LogisticRegressionModelTrainer', 'l': self.l}