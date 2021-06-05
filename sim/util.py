"""
Various utility classes and methods.
"""

import uuid
import math
from enum import Enum


class Region(Enum):
    """The supported regions."""
    US = 'US'
    RU = 'RU'
    KZ = 'KZ'
    ML = 'ML'
    CN = 'CN'
    GE = 'GE'
    NR = 'NR'
    VN = 'VN'
    CH = 'CH'


def generate_uuid() -> str:
    """
    Generate UUIDs to use as `sim.base_models.Node` and `sim.base_models.Item` ids.
    """
    return str(uuid.uuid4())


