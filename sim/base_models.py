from collections import deque
from enum import Enum

from loguru import logger

from typing import List

from sim import util
from sim.network_consts import speed, latency
from sim.util import Region


class Item:
    def __init__(self, sender_id: str, size: int, created_at: int):
        self.id = util.generate_uuid()
        self.size = size
        self.created_at = created_at
        self.sender_id = sender_id


# Wrapper class for items to prevent Links from modifying items pointed from multiple places
class Packet:
    def __init__(self, timestamp: int, payload: Item):
        self.timestamp = timestamp
        self.payload = payload
        self.delay = 0


class Node:
    def __init__(self, pos_x: float, pos_y: float, region, timestamp=0):
        self.id = util.generate_uuid()
        self.timestamp = timestamp
        self.pos = util.Coords(pos_x, pos_y)
        self.queue: deque = deque()
        self.region = region
        self.ins = dict()
        self.outs = dict()

    def step(self, seconds: float):
        self.timestamp += 1
        outs = self.outs.values()
        for link in outs:
            link.step(seconds)

    # get items to operate on current time step
    #   assumes can handle infinitely many inputs in one step
    def get_items(self) -> List[Item]:
        items = []
        timestamp = self.timestamp
        queue = self.queue
        try:
            packet = queue[-1]
            while packet.timestamp < timestamp:
                items.append(queue.pop().payload)
                packet = queue[-1]
        except IndexError:
            pass
        return items


class Link:
    def __init__(self, start: Node, end: Node):
        self.id = util.generate_uuid()
        self.timestamp = start.timestamp
        self.start = start
        self.end = end
        self.queue: deque = deque()

    def step(self, seconds: float):
        self.timestamp += 1
        try:
            item = self.queue[-1]
            item.delay -= seconds
            if item.delay <= 0:
                item.timestamp = self.timestamp
                self.end.queue.appendleft(self.queue.pop())
        except IndexError:
            return

    def send(self, item: Item):
        packet = Packet(self.timestamp, item)

        lat = latency(self.start.region, self.end.region)
        trans = (item.size / speed(self.start.region, self.end.region))
        packet.delay = lat + trans

        self.queue.appendleft(packet)
