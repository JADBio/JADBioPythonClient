from enum import Enum

class LossFunction(Enum):
    Accuracy = "AccuracyLossComputerFactory"
    CI = "CILossComputerFactory"
    Deviance = "DevianceLossComputerFactory"
    Gini = "GiniLossComputerFactory"
    MSE = "MSELossComputerFactory"
    R2 = "R2LossComputerFactory"

    def to_dict(self):
        return {'type': str(self.value) }