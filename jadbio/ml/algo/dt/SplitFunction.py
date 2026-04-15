from abc import ABC

class SplitFunction(ABC):
    pass

    @staticmethod
    def sqrt(n1: float):
        return VariableSQRT(n1)

    @staticmethod
    def ratio(n1: float):
        return VariableRatio(n1)

    @staticmethod
    def perc(n1: float):
        return VariablePercentage(n1)

class VariableSQRT(SplitFunction):
    n1=0
    def __init__(self, n1):
        self.n1 = n1

    def to_dict(self):
        return {'type': 'VariableSQRT', 'n1': self.n1}

class VariableRatio(SplitFunction):
    n1=0
    def __init__(self, n1):
        self.n1 = n1

    def to_dict(self):
        return {'type': 'VariableRatio', 'n1': self.n1}

class VariablePercentage(SplitFunction):
    n1=0
    def __init__(self, n1):
        self.n1 = n1

    def to_dict(self):
        return {'type': 'VariablePercentage', 'n1': self.n1}