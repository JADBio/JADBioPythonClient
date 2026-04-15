from jadbio.ml.algo.DT import DT
from jadbio.ml.algo.rf.Bagger import Bagger
from jadbio.ml.algo.rf.LossFunction import LossFunction


class RF:
    nmodels = 0
    loss= None
    dt = None
    bagger = None

    def __init__(self, nmodels: int, dt: DT, loss: LossFunction, bagger: Bagger):
        self.nmodels = nmodels
        self.loss = loss
        self.dt = dt
        self.bagger = bagger

    def to_dict(self):
        return {
            'type': 'BaggedTreeModelTrainer',
            'mt': self.dt.to_dict(),
            'b': self.bagger.to_dict(),
            'lcf': self.loss.to_dict(),
            'nmodels': self.nmodels,
            'withreplacement': True,
            'resampleratio': 1,
        }