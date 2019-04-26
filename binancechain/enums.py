from enum import Enum
class VOTES(Enum):
    Yes=1
    No=2
    Abstain=3
    NoWithVeto=4

class ORDERTYPE(Enum):
    Limit=2

class SIDE(Enum):
    Buy=1
    Sell=2
class TIMEINFORCE(Enum):
    GTE=1
    IOC=3
