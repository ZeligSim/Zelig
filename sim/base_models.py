from collections import deque
from loguru import logger

from typing import List

from sim import util
from sim.network_consts import speed, latency


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
        self.ins = []
        self.outs = []

    def step(self):
        self.timestamp += 1
        for link in self.outs:
            link.step()

    # get items to operate on current time step
    #   assumes can handle infinitely many inputs in one step
    def get_items(self) -> List[Item]:
        if len(self.queue) > 0:
            packet = self.queue[-1]
            if packet.timestamp < self.timestamp:
                return [self.queue.pop().payload] + self.get_items()
            else:
                return []
        else:
            return []


class Link:
    def __init__(self, start: Node, end: Node, bandwidth: float):
        self.id = util.generate_uuid()
        self.timestamp = start.timestamp
        self.bandwidth = bandwidth
        self.start = start
        self.end = end
        self.queue: deque = deque()

    def step(self):
        self.timestamp += 1
        if len(self.queue) > 0:
            item = self.queue[-1]
            item.delay -= 0.1
            item.timestamp = self.timestamp
            if item.delay <= 0:
                self.end.queue.appendleft(self.queue.pop())

    def send(self, item: Item):
        packet = Packet(self.timestamp, item)

        lat = latency(self.start.region, self.end.region)
        trans = (item.size / speed(self.start.region, self.end.region))
        packet.delay = lat + trans

        self.queue.appendleft(packet)
