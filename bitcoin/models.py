import math
import random
import sys
import numpy as np

from typing import Dict

sys.path.append("..")

from loguru import logger

from sim.base_models import *
from bitcoin.messages import InvMessage, GetDataMessage
from sim.network_util import get_delay

logger.remove()
logger.add(sys.stdout, level='INFO')
# logger.add('logs/bitcoin_logs.txt', level='DEBUG')


class Block(Item):
    def __init__(self, miner: Node, sender_id: str, timestamp: int, created_at: int, prev_id: str):
        super().__init__(sender_id, 0, created_at)
        self.prev_id = prev_id
        self.miner = miner
        self.size = np.random.normal(1.19, 0.26) * (10 ** 6)

    def __getstate__(self):
        """Return state values to be pickled."""
        state = self.__dict__.copy()
        # Remove the unpicklable entries.
        del state['miner']
        del state['sender_id']
        del state['timestamp']
        del state['size']
        return state

    def __setstate__(self, state):
        """Restore state from the unpickled state values."""
        self.__dict__.update(state)

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
        self.blockchain: Dict[str, Block] = dict()
        self.txpool: Dict[str, Transaction] = dict()
        self.heads: List[Block] = []

        self.mine_power = mine_power
        self.mine_cost = mine_cost
        self.difficulty = 0
        self.mine_probability = 0

        self.stat_block_rcvs: Dict[str, int] = dict()
        logger.info(f'CREATED MINER {self.name}')

    def __getstate__(self):
        """Return state values to be pickled."""
        state = self.__dict__.copy()
        # Remove the unpicklable entries.
        del state['txpool']
        del state['mine_power']
        del state['mine_cost']
        del state['ins']
        del state['outs']
        del state['inbox']
        del state['difficulty']
        del state['mine_probability']
        del state['timestamp']
        del state['pos']
        del state['region']
        del state['timestamp']
        return state

    def __setstate__(self, state):
        """Restore state from the unpickled state values."""
        self.__dict__.update(state)

    def __str__(self) -> str:
        return self.name

    def step(self, seconds: float):
        items = super().step(seconds)
        for item in items:
            self.__consume(item)

        # if random.random() <= 0.001:
        #     self.__generate_transaction()
        if random.random() <= self.mine_probability:
            self.generate_block()

    def connect(self, *argv):
        for node in argv:
            self.outs[node.id] = node
            node.ins[self.id] = self

    def set_difficulty(self, difficulty):
        self.difficulty = difficulty
        self.mine_probability = self.mine_power * self.difficulty

    def __consume(self, item: Item):
        if type(item) == Block:
            logger.info(f'[{self.timestamp}] {self.name} RECEIVED BLOCK {item.id}')
            self.stat_block_rcvs[item.id] = self.timestamp
            self.add_block(item)
            self.__publish_item(item, 'block')
        elif type(item) == Transaction:
            logger.debug(f'[{self.timestamp}] {self.name} RECEIVED TX {item.id}')
            self.txpool[item.id] = item
            self.__publish_item(item, 'tx')
        elif type(item) == InvMessage:
            logger.debug(f'[{self.timestamp}] {self.name} RECEIVED INV MESSAGE FOR {item.type} {item.item_id}')
            if item.type == 'block':
                if self.blockchain.get(item.item_id, None) is None:
                    logger.debug(f'[{self.timestamp}] {self.name} RESPONDED WITH GETDATA')
                    self.blockchain[item.item_id] = 'placeholder'  # not none
                    self.__send_to(self.outs[item.sender_id], GetDataMessage(item.item_id, item.type, self.id, self.timestamp, 10, self.timestamp))
            # elif msg.type == 'tx':
            #     if self.txpool.get(msg.item_id, None) is None:
            #         logger.debug(f'[{self.timestamp}] {self.name} RESPONDED WITH GETDATA')
            #         self.txpool[msg.item_id] = 'placeholder'  # not none
            #         getdata = GetDataMessage(msg.item_id, msg.type, self.id, self.timestamp, 10, self.timestamp)
            #         self.__send_to(msg.sender_id, getdata)
        elif type(item) == GetDataMessage:
            logger.debug(f'[{self.timestamp}] {self.name} RECEIVED GETDATA MESSAGE FOR {item.type} {item.item_id}')
            if item.type == 'block':
                self.__send_to(self.outs[item.sender_id], self.blockchain[item.item_id])
            # elif msg.type == 'tx':
            #     self.__send_to(msg.sender_id, self.txpool[msg.item_id])

    # FIXME: public for testing
    def generate_block(self, prev=None) -> Block:
        if prev is None:
            prev = self.choose_prev_block()
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
        try:
            self.heads.remove(self.blockchain[block.prev_id])
        except (ValueError, KeyError):
            pass
        self.heads.append(block)

    def __generate_transaction(self) -> Transaction:
        fee = 10
        tx = Transaction(fee, self.id, self.timestamp)
        self.txpool[tx.id] = tx
        self.__publish_item(tx, 'tx')
        return tx

    def __publish_item(self, item: Item, item_type: str):
        msg = InvMessage(item.id, item_type, self.id, self.timestamp, 10, self.timestamp)
        for node in self.outs.values():
            self.__send_to(node, msg)

    def __send_to(self, node: Node, item: Item):
        packet = Packet(self.timestamp, item)
        delay = get_delay(self.region, node.region, item.size) / 0.1
        packet.reveal_at = math.ceil(self.timestamp + delay)
        try:
            node.inbox[packet.reveal_at].append(packet)
        except KeyError:
            node.inbox[packet.reveal_at] = [packet]

    # returns the head of the longest chain
    def choose_prev_block(self) -> Block:
        get_length = self.__get_length
        lengths = [get_length(block) for block in self.heads if block != 'placeholder']
        return self.heads[lengths.index(max(lengths))]

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
        head = self.choose_prev_block()
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
