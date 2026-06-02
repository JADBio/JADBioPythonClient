class Epilogi:
    max_vars = None
    single = None
    threshold = 0
    stopping_criterion = None
    equiv_threshold = 0
    canonical = False

    # possible values for stopping_criterion
    # aic, aicc, bic, ebic, hqc, nested(default)
    def __init__(self, threshold, max_vars, stopping_criterion='nested', equiv_threshold = 0, multiple_signatures = False):
        self.threshold = threshold
        self.max_vars = max_vars
        self.stopping_criterion = stopping_criterion
        self.equiv_threshold = equiv_threshold
        self.single = multiple_signatures

    def to_dict(self):
        d = {}
        d['equivThreshold'] = self.equiv_threshold
        d['canonical'] = self.canonical
        d['type'] = 'EpilogiFeatureSelector'
        d['single'] = self.single
        d['stoppingCriterionFactory'] = { 'type': self.stopping_criterion, 'threshold': self.threshold }
        d['residualsFactory'] = { 'type': 'vector', 'mlr': False }
        d['maxVars'] = self.max_vars
        return d
