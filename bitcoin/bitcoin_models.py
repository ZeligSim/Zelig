import random
import sys

from typing import Dict

sys.path.append("..")

from loguru import logger

from sim.base_models import *
from messages import InvMessage, GetDataMessage, GetBlockchainMessage


class Block(Item):
    def __init__(self, miner: Node, sender_id: str, timestamp: int, created_at: int, prev_id: str):
        super().__init__(timestamp, sender_id, 0, created_at)
        self.prev_id = prev_id
        self.size = 1000  # TODO: calculate size
        self.miner = miner

    def __str__(self) -> str:
        return f'Block: {self.id}'


# TODO: check timestamp logic and links (not) sending items
class Miner(Node):
    def __init__(self, pos_x: float, pos_y: float, mine_power: int, mine_cost=0, timestamp=0):
        super().__init__(pos_x, pos_y, timestamp)
        self.mine_power = mine_power
        self.mine_cost = mine_cost
        self.blockchain: List[Block] = []
        self.blockpool: Dict[str, Block] = dict()
        logger.info(f'Created miner {self.id}')

    def step(self):
        super().step()
        items = self.get_items()
        for item in items:
            self.__consume(item)

        if random.random() <= self.mine_power * (self.__get_difficulty()):
            self.generate_block()

    def connect(self, node: Node):
        # link = Link(self, node, os.getenv('BANDWIDTH')) #TODO: bandwidth
        link = Link(self, node, 200)
        self.outs.append(link)
        node.ins.append(link)

    def __consume(self, item: Item):
        if type(item) == Block:
            print('hello there')
            self.__publish_block(item)
            if item.prev_id == self.blockchain[-1].id:
                self.blockchain.append(item)
        elif type(item) == InvMessage:
            if item.block_id not in self.blockpool.keys():
                msg = GetDataMessage(item.block_id, self.id, self.timestamp, 10, self.timestamp)
                self.__send_to(item.sender_id, msg)
        elif type(item) == GetDataMessage:
            self.__send_to(item.sender_id, self.blockpool[item.block_id])
        elif type(item) == GetBlockchainMessage:
            for block in self.blockchain:
                self.__send_to(item.sender_id, block)

    def generate_block(self):
        prev = self.__choose_prev_block()
        block = Block(self, self.id, self.timestamp, self.timestamp, prev.id)
        self.blockchain.append(block)  # TODO:
        self.blockpool[block.id] = block
        self.__publish_block(block)

    def __publish_block(self, block: Block):
        for link in self.outs:
            msg = InvMessage(block.id, self.id, self.timestamp, 10, self.timestamp)
            link.send(msg)

    # TODO: implements the main consensus logic to choose which block to mine on
    def __choose_prev_block(self) -> Block:
        return self.blockchain[-1]

    def __send_to(self, node_id: str, item: Item):
        for link in self.outs:
            if link.end.id == node_id:
                link.send(item)

    def __get_difficulty(self) -> float:
        return 2 ** 2 / 2 ** 256
