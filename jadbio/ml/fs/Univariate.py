class Univariate:
    max_vars = None
    alpha = 0

    def __init__(self, alpha, max_vars):
        self.alpha = alpha
        self.max_vars = max_vars

    def to_dict(self):
        d = {}
        d['alpha'] = self.alpha
        d['type'] = 'univariate'
        d['maxVars'] = self.max_vars
        return d
