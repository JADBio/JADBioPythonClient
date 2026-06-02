class LASSO:
    max_vars = 0
    penalty = []

    def __init__(self, max_vars: int, penalty: float):
        self.max_vars = max_vars
        self.penalty = penalty

    def to_dict(self):
        d = {}
        d['type'] = 'LassoFeatureSelector'
        d['conf'] = {'maxVars': self.max_vars, 'penalty': self.penalty}
        return d