from typing import List
import random
import sys
sys.path.append("..")

from sim.base_models import *
from messages import *


class Block(Item):
    def __init__(self, miner: Node, sender_id: str, timestamp: int, created_at: int, prev_id: str):
        super().__init__(self, timestamp, sender_id, 0, created_at)
        self.prev_id = prev_id
        self.size = 10 #TODO: calculate size
        self.miner = miner


class Miner(Node):
    def __init__(self, pos_x: float, pos_y: float, mine_power: int, mine_cost=0,  timestamp=0):
        super().__init__(self, pos_x, pos_y, timestamp)
        self.mine_power = mine_power
        self.mine_cost = mine_cost
        self.blockchain: List[Block] = []
        self.blockpool: List[Block] = []

    def step(self):
        super().step()
        items = self.__get_items()
        for item in items:
            self.__consume(item)

        if random.random() <= self.mine_power * (self.__get_difficulty()):
            self.__generate_block()

    def connect(self, node: Node):
        link = Link(self, node, os.getenv('BANDWIDTH')) #TODO: bandwidth
        self.outs.append(link) 
        node.ins.append(link)

    def __consume(self, item: Item):
        kind = type(item)
        if kind == Block:
            pass
        elif kind == InvMessage:
            block_id = item.block_id
            if block_id not in [block.id for block in self.blockpool]:
                msg = GetDataMessage(block_id, self.id, self.timestamp, 10, self.timestamp)
                self.__send_to(item.sender_id, msg)
        elif kind == GetDataMessage:
            block_id = item.block_id
            block = [block for block in self.blockpool if block.id == block_id][0]
            self.__send_to(item.sender_id, block)
        elif kind == GetBlockchainMessage:
            pass

    def __generate_block(self):
        prev_id = self.blockchain[-1].id #TODO: compute branch with most work if fork
        block = Block(self, self.id, self.timestamp, self.timestamp, prev_id)
        self.blockchain.append(block)
        for link in self.outs:
            msg = InvMessage(block.id, self.id, self.timestamp, 10, self.timestamp)
            link.send(msg)

    def __send_to(self, node_id: str, item: Item):
        for link in self.outs:
            if link.end.id == node_id:
                link.send(item)

    def __get_difficulty(self) -> float:
        return 2**26 / 2**256




        