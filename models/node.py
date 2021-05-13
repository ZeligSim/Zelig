from collections import deque
import sys
sys.path.append("..")

import util
import link


class Node:

    def __init__(timestamp: int, ins: list[link.Link], outs: list[link.Link], pos_x: int, pos_y: int):
        self.id = util.generate_uuid()
        self.timestamp = timestamp
        self.ins = ins
        self.outs = outs
        self.coords = Coords(pos_x,pos_y)
        self.queue = deque()


class Coords:
    def __init__(pos_x: int, pos_y: int):
        self.pos_x = pos_x
        self.pos_y = pos_y

        
