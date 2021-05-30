from collections import deque
from enum import Enum

from loguru import logger

from typing import List

from sim import util
from sim.network_util import speed, latency
from sim.util import Region


class Item:
    def __init__(self, sender_id: str, size: int, created_at: int):
        self.id = util.generate_uuid()
        self.size = size
        self.created_at = created_at
        self.sender_id = sender_id


# Wrapper class for items to prevent Nodes from modifying items pointed from multiple places
class Packet:
    def __init__(self, timestamp: int, payload: Item):
        self.timestamp = timestamp
        self.payload = payload
        self.reveal_at = 0


class Node:
    def __init__(self, pos_x: float, pos_y: float, region, timestamp=0):
        self.id = util.generate_uuid()
        self.timestamp = timestamp
        self.pos = util.Coords(pos_x, pos_y)
        self.region = region
        self.inbox = dict()
        self.ins = dict()
        self.outs = dict()

    def step(self, seconds: float) -> List[Item]:
        self.timestamp += 1
        try:
            return [packet.payload for packet in self.inbox.pop(self.timestamp)]
        except KeyError:
            return []