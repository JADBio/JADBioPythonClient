from enum import Enum

from jadbio.ml.pp.StandardPP import StandardPP


def default_preprocessing():
    return PP.Standard


def no_preprocessing():
    return PP.Identity


class Identity:
    def to_dict(self):
        return {'type': 'IdentityFactory'}


class PP(Enum):
    Standard = StandardPP()
    Identity = Identity()
