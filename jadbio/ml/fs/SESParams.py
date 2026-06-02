class SESParams:
    max_k = 0
    max_vars = 0
    single = False
    threshold = 0

    def __init__(self, max_k, threshold, max_vars):
        self.max_k = max_k
        self.threshold = threshold
        self.max_vars = max_vars

    def to_dict(self):
        d = {}
        d['type'] = 'SESFeatureSelector'
        d['maxk'] = self.max_k
        d['single'] = self.single
        d['threshold'] = self.threshold
        d['maxvars'] = self.max_vars
        return d