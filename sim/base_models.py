from collections import deque
from typing import List

from sim import util, network_util


class Item:
    def __init__(self, timestamp: int, size: int, created_at: int):
        self.id = util.generate_uuid()
        self.timestamp = timestamp
        self.size = size
        self.created_at = created_at
        self.delay = 0 # link will compute this after item creation


class Node:
    def __init__(self, pos_x: int, pos_y: int, timestamp=0):
        self.id = util.generate_uuid()
        self.timestamp = timestamp
        self.pos = util.Coords(pos_x, pos_y)
        self.queue = deque()
        self.ins = []
        self.outs = []

    def step(self):
        self.timestamp += 1
        for link in self.outs:
            link.step()

    # get items to operate on current time step
    #   assumes can handle infinitely many inputs in one step
    def __get_items(self) -> List[Item]:
        try:
            item = self.queue[-1]
            if item.timestamp == self.timestamp - 1:
                return [self.queue.pop()] + self.__get_items()
            else:
                return []
        except:
            return []

    def __str__(self) -> str:
        return f'Node {self.id}: pos=({self.pos.x}, {self.pos.y})'


class Link:
    def __init__(self, start: Node, end: Node, bandwidth: float):
        self.id = util.generate_uuid()
        self.timestamp = start.timestamp
        self.bandwidth = bandwidth
        self.bit_delay = 0 #TODO: 
        self.start = start
        self.end = end
        self.queue = deque()

    def step(self):
        self.timestamp += 1
        item = self.queue[-1]
        item.delay -= 1
        if item.delay == 0:
            self.end.queue.appendleft(self.queue.pop())

    def send(self, item: Item):
        item.delay = self.bit_delay + (item.size / self.bandwidth)
        self.queue.appendleft(item)



