class CVArgs:
    dataset_id = 0
    target = None
    type = None
    threads = 1
    grouped_factor = None
    configurations: dict

    def __init__(self, dataset_id, target, type):
        """
        :param dataset_id: the id upload returned
        :param target: target name, in case of survival comma separated event, time_to_event
        :param type: analysis type (CLASSIFICATION, REGRESSION, SURVIVAL)
        """
        self.dataset_id = dataset_id
        self.target = target
        self.type = type
        self.configurations = {}

    def add_threads(self, threads):
        self.threads = threads
        return self

    def add_grouped_factor(self, gf):
        self.grouped_factor = gf
        return self

    def add_conf(self, confKey, confVal):
        self.configurations[confKey] = confVal
        return self

    def to_dict(self):
        d = {}
        d['datasetId'] = self.dataset_id
        d['target'] = self.target
        d['groupedFactor'] = self.grouped_factor
        d['concurrency'] = self.threads
        d['analysisType'] = str(self.type.value)
        d['configurations'] = {}
        for c in self.configurations.keys() :
            d['configurations'][c] = self.configurations[c].to_dict()
        return d