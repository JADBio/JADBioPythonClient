class StandardPP:
    pp = []

    def to_dict(self):
        chain = [
            {'type' : 'MeanImputationFactory'},
            {'type': 'ModeImputationFactory'},
            {'type' : 'ConstantRemoverFactory'},
            {'type': 'NormalizerFactory'}
        ]

        return {'type': 'PreprocessChainFactory', 'chain': chain}