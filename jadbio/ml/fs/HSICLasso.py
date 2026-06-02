class HSICLasso:
    max_vars = None
    threshold = 0

    def __init__(self, threshold, max_vars):
        self.threshold = threshold
        self.max_vars = max_vars

    def to_dict(self):
        d = {}
        d['type'] = 'HsicLassoMrmrFeatureSelector'
        d['conf'] = {'threshold': self.threshold, 'maxVars': self.max_vars}
        return d
