import sys
sys.path.append("..")
from collections import deque

import util
from item import Item
from node import Node

class Link:
  def __init__(self, start: Node, end: Node, bandwidth: float):
      self.id = util.generate_uuid()
      self.start = start
      self.end = end
      self.bandwidth = bandwidth
      self.latency = 10 # TODO: network util
      self.queue = deque()
       

  def step(self):
    item = self.queue[-1]
    item.delay -= 1
    if item.delay == 0:
      end.queue.appendleft(self.queue.pop())
    

  def send(self, item: Item):
    item.delay = self.latency + (item.size / self.bandwidth)
    self.queue.appendleft(item)
    



