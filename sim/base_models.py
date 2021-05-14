from collections import deque

from sim import util


class Node:
    def __init__(self, pos_x: int, pos_y: int, timestamp=0):
        self.id = util.generate_uuid()
        self.timestamp = timestamp
        self.pos = util.Coords(pos_x, pos_y)
        self.queue = deque()
        self.ins = []
        self.outs = []

    def step(self):
        pass

    def __str__(self) -> str:
        return f'Node {self.id}: pos=({self.pos.x}, {self.pos.y})'


class Item:
    def __init__(self, timestamp: int, size: int, delay: int, created_at: int):
        self.id = util.generate_uuid()
        self.timestamp = timestamp
        self.size = size
        self.delay = delay
        self.created_at = created_at


class Link:
    def __init__(self, timestamp: int, start: Node, end: Node, bandwidth: float):
        self.id = util.generate_uuid()
        self.timestamp = timestamp
        self.bandwidth = bandwidth
        self.start = start
        self.end = end
        self.latency = 10  # TODO: network util
        self.queue = deque()

    def step(self):
        item = self.queue[-1]
        item.delay -= 1
        if item.delay == 0:
            self.end.queue.appendleft(self.queue.pop())

    def send(self, item: Item):
        item.delay = self.latency + (item.size / self.bandwidth)
        self.queue.appendleft(item)



