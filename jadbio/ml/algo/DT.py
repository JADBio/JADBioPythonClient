from random import random

from jadbio.ml.algo.dt.SplitCriterion import SplitCriterion
from jadbio.ml.algo.dt.SplitFunction import SplitFunction


class DT:
    min_leaf_size = 0
    nsplits = 0
    alpha = 0
    seed = 0
    split_criterion = None
    vars_function = None

    def __init__(self, mls: int, splits: int, alpha: float, criterion: SplitCriterion, vars_f: SplitFunction, seed=None):
        self.min_leaf_size = mls
        self.nsplits = splits
        self.alpha = alpha
        self.vars_function = vars_f
        self.seed = seed if seed is not None else random()
        self.split_criterion = criterion

    def to_dict(self):
        d = {}
        d['type'] = 'DecisionTreeTrainer'
        d['factory'] = self.split_criterion.to_dict()
        d['variablestosplit'] = self.vars_function.to_dict()
        d['minleafsize'] = self.min_leaf_size
        d['splitstoperform'] = self.nsplits
        d['alpha'] = self.alpha
        d['seed'] = self.seed
        return d