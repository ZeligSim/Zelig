import uuid
import math
from enum import Enum


# top 10 countries for April 2020
# corresponding to > 95% of the global hash power
class Region(Enum):
    US = 'US'
    RU = 'RU'
    KZ = 'KZ'
    ML = 'ML'
    CN = 'CN'
    GE = 'GE'
    NR = 'NR'
    VN = 'VN'
    CH = 'CH'


class Coords:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def distance(self, c) -> float:
        return math.sqrt((self.x - c.x) ** 2 + (self.y - c.y) ** 2)


def generate_uuid() -> str:
    return str(uuid.uuid4())


