from enum import Enum


class Votes(Enum):
    YES = 1
    NO = 2
    ABSTAIN = 3
    NOWITHVETO = 4


class Ordertype(Enum):
    LIMIT = 2


class Side(Enum):
    BUY = 1
    SELL = 2


class Timeinforce(Enum):
    GTE = 1
    IOC = 3
