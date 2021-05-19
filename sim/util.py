import uuid
import math
from enum import Enum


class Region(Enum):
    US = 'US'
    EU = 'EU'
    SA = 'SA'
    AP = 'AP'
    JP = 'JP'
    AU = 'AU'
    RU = 'RU'


class Coords:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def distance(self, c) -> float:
        return math.sqrt((self.x - c.x) ** 2 + (self.y - c.y) ** 2)


def generate_uuid() -> str:
    return str(uuid.uuid4())


