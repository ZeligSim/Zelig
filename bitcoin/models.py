import random
import sys
import numpy as np

from typing import Dict

sys.path.append("..")

from loguru import logger

from sim.base_models import *
from bitcoin.messages import InvMessage, GetDataMessage

logger.remove()
logger.add(sys.stdout, level='INFO')
logger.add('logs/bitcoin_logs.txt', level='DEBUG')


class Block(Item):
    def __init__(self, miner: Node, sender_id: str, timestamp: int, created_at: int, prev_id: str):
        super().__init__(sender_id, 0, created_at)
        self.prev_id = prev_id
        self.miner = miner
        self.size = np.random.normal(1.19, 0.26) * 10 ** 6

    def __str__(self) -> str:
        return f'BLOCK (id:{self.id}, prev: {self.prev_id})'


class Transaction(Item):
    def __init__(self, fee: int, sender_id: str, created_at: int):
        super().__init__(sender_id, 0, created_at)
        self.fee = fee
        self.size = 400  # bytes TODO


class Miner(Node):
    def __init__(self, name: str, pos_x: float, pos_y: float, mine_power: int, region: Region, mine_cost=0,
                 timestamp=0):
        super().__init__(pos_x, pos_y, region, timestamp)
        self.name = name
        self.mine_power = mine_power
        self.mine_cost = mine_cost
        self.blockchain: Dict[str, Block] = dict()
        self.txpool: Dict[str, Transaction] = dict()
        self.heads: List[Block] = []
        self.difficulty = 0

        self.stat_block_rcvs: Dict[str, int] = dict()
        logger.info(f'CREATED MINER {self.name}')

    def __str__(self) -> str:
        return self.name

    def step(self, seconds: float):
        super().step(seconds)
        items = self.get_items()
        for item in items:
            self.__consume(item)

        # if random.random() <= 0.001:
        #     self.__generate_transaction()
        if random.random() <= self.mine_power * self.difficulty:
            self.generate_block()

    def connect(self, *argv) -> List[Link]:
        links = []
        for node in argv:
            if node not in [link.end for link in self.outs]:
                link = Link(self, node)
                self.outs.append(link)
                node.ins.append(link)
                links.append(link)
        return links

    def __consume(self, item: Item):
        if type(item) == Block:
            logger.info(f'[{self.timestamp}] {self.name} RECEIVED BLOCK {item.id}')
            self.__consume_block(item)
        # elif type(item) == Transaction:
        #     logger.debug(f'[{self.timestamp}] {self.name} RECEIVED TX {item.id}')
        #     self.__consume_transaction(item)
        elif type(item) == InvMessage:
            logger.debug(f'[{self.timestamp}] {self.name} RECEIVED INV MESSAGE FOR {item.type} {item.item_id}')
            self.__consume_inv(item)
        elif type(item) == GetDataMessage:
            logger.debug(f'[{self.timestamp}] {self.name} RECEIVED GETDATA MESSAGE FOR {item.type} {item.item_id}')
            self.__consume_getdata(item)

    # -- CONSUMING MESSAGE TYPES --
    def __consume_block(self, block: Block):
        self.stat_block_rcvs[block.id] = self.timestamp
        self.add_block(block)
        self.__publish_item(block, 'block')

    def __consume_transaction(self, tx: Transaction):
        self.txpool[tx.id] = tx
        self.__publish_item(tx, 'tx')

    def __consume_inv(self, msg: InvMessage):
        if msg.type == 'block':
            if self.blockchain.get(msg.item_id, None) is None:
                logger.debug(f'[{self.timestamp}] {self.name} RESPONDED WITH GETDATA')
                self.blockchain[msg.item_id] = 'placeholder'  # not none
                getdata = GetDataMessage(msg.item_id, msg.type, self.id, self.timestamp, 10, self.timestamp)
                self.__send_to(msg.sender_id, getdata)
        # elif msg.type == 'tx':
        #     if self.txpool.get(msg.item_id, None) is None:
        #         logger.debug(f'[{self.timestamp}] {self.name} RESPONDED WITH GETDATA')
        #         self.txpool[msg.item_id] = 'placeholder'  # not none
        #         getdata = GetDataMessage(msg.item_id, msg.type, self.id, self.timestamp, 10, self.timestamp)
        #         self.__send_to(msg.sender_id, getdata)

    def __consume_getdata(self, msg: GetDataMessage):
        if msg.type == 'block':
            self.__send_to(msg.sender_id, self.blockchain[msg.item_id])
        # elif msg.type == 'tx':
        #     self.__send_to(msg.sender_id, self.txpool[msg.item_id])

    # ------------------------------

    # FIXME: public for testing
    def generate_block(self, prev=None) -> Block:
        if prev is None:
            prev = self.__choose_prev_block()
        block = Block(self, self.id, self.timestamp, self.timestamp, prev.id)
        logger.success(f'[{self.timestamp}] {self.name} GENERATED BLOCK {block.id} ==> {prev.id}')
        self.add_block(block)
        self.stat_block_rcvs[block.id] = self.timestamp
        self.__publish_item(block, 'block')
        return block

    # FIXME: public for testing
    # remove block.prev from heads if exists and add block to blockchain
    def add_block(self, block):
        self.blockchain[block.id] = block
        prev = list(filter(lambda head: head.id == block.prev_id, self.heads))
        if len(prev) > 0:
            self.heads.remove(prev[0])
        self.heads.append(block)

    def __generate_transaction(self) -> Transaction:
        fee = 10
        tx = Transaction(fee, self.id, self.timestamp)
        self.txpool[tx.id] = tx
        self.__publish_item(tx, 'tx')
        return tx

    def __publish_item(self, item: Item, item_type: str):
        for link in self.outs:
            msg = InvMessage(item.id, item_type, self.id, self.timestamp, 10, self.timestamp)
            link.send(msg)

    # returns the head of the longest chain
    def __choose_prev_block(self) -> Block:
        lengths = [self.__get_length(block) for block in self.heads if block != 'placeholder']
        return self.heads[lengths.index(max(lengths))]

    def __send_to(self, node_id: str, item: Item):
        for link in self.outs:
            if link.end.id == node_id:
                link.send(item)
                return

    # get length of chain starting ending at `block`
    def __get_length(self, block):
        count = 0
        prev = self.blockchain.get(block.prev_id, None)
        while prev is not None:
            count += 1
            prev = self.blockchain.get(prev.prev_id, None)
        return count


    # -- LOGGING / INFO METHODS --
    def log_blockchain(self):
        head = self.__choose_prev_block()
        logger.warning(f'{self.name}')
        logger.warning(f'\tBLOCKCHAIN:')
        for block in self.blockchain.values():
            logger.warning(f'\t\t{block}')
        logger.warning(f'\tHEADS:')
        for block in self.heads:
            if block == head:
                logger.warning(f'\t\t*** {block}')
            else:
                logger.warning(f'\t\t{block}')