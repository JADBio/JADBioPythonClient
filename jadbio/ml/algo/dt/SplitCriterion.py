from enum import Enum

class SplitCriterion(Enum):
    CMLogRank = "CMLogRankSplittingCriterionFactory"
    Deviance = "DevianceSplittingCriterionFactory"
    MHLogRank = "MHLogRankSplittingCriterionFactory"
    MSES = "MSESplittingCriterionFactory"

    def to_dict(self):
        return {'type': str(self.value) }


