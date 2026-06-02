from enum import Enum

class Bagger(Enum):
    Averaging = "AveragingBagger"
    GradientBoosting = "GradientBoostingBagger"
    Majority = "MajorityBagger"
    Probability = "ProbabilityBagger"

    def to_dict(self):
        return {'type': str(self.value) }