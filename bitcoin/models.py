"""
Main implementation of the Bitcoin simulator.
"""

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


class Block(Item):
    """Represents a Bitcoin block."""

    def __init__(self, miner: Node, prev_id: str, height: int):
        """
        Create a Block object.

        * miner (`Node`): Node that created the block.
        * prev_id (str): Id of the block this block was mined on top of.
        * height (int): Height of the block in the blockchain.
        """
        super().__init__(None, 0)
        self.prev_id = prev_id
        self.miner = miner.name
        self.created_at = miner.timestamp
        self.height = height
        self.tx_count = np.random.normal(2104.72, 236.63)
        self.size = self.tx_count * np.random.normal(615.32, 89.43)

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['sender_id']
        del state['size']
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)

    def __str__(self) -> str:
        return f'BLOCK (id:{self.id}, prev: {self.prev_id})'


# class Transaction(Item):
#     def __init__(self, fee: int, sender_id: str):
#         super().__init__(sender_id, 0)
#         self.fee = fee
#         self.size = 400  # bytes TODO


class Miner(Node):
    """Represents a Bitcoin miner. """

    def __init__(self, name: str, mine_power: float, region: Region, iter_seconds, timestamp=0):
        """
        Create a Miner object.

        * name (str): Human-legible name for the miner. Uniqueness of names is not enforced.
        * mine_power (float): Mining power of the miner, representing what share of the global mining power this miner controls.
        * region (`sim.util.Region`): Miner's region.
        * iter_seconds (float): How many real-world seconds one simulation step corresponds to.
        * timestamp (int): Used to keep track of the simulation step count. Defaults to 0.
        """
        super().__init__(region, timestamp)
        self.name = name
        self.mine_power = mine_power
        self.difficulty = 0
        self.mine_probability = 0
        self.iter_seconds = iter_seconds

        self.blockchain: Dict[str, Block] = dict()
        """A dictionary that stores block `Block` ids as keys and """

        self.heads: List[Block] = []
        """Stores the current head blocks (blocks that hasn't been mined on) as a list."""

        self.stat_block_rcvs: Dict[str, int] = dict()
        """Stores the receipt time of blocks, to calculate metrics such as block propagation times."""
        logger.info(f'CREATED MINER {self.name}')

    def __getstate__(self):
        """Return state values to be pickled."""
        state = self.__dict__.copy()
        # Remove the unpicklable entries.
        del state['mine_power']
        del state['ins']
        del state['outs']
        del state['inbox']
        del state['difficulty']
        del state['mine_probability']
        del state['timestamp']
        del state['region']
        return state

    def __setstate__(self, state):
        """Restore state from the unpickled state values."""
        self.__dict__.update(state)

    def __str__(self) -> str:
        return self.name

    def step(self, seconds: float):
        items = super().step(seconds)
        for item in items:
            self.consume(item)

        # if random.random() <= 0.001:
        #     self.__generate_transaction()
        if random.random() <= self.mine_probability:
            self.generate_block()

    def connect(self, *argv):
        """
        Establish an outgoing connection to one or more nodes.
        * argv (`sim.base_models.Node`+): Node(s) to establish connections with.
        """
        for node in argv:
            self.outs[node.id] = node
            node.ins[self.id] = self

    def set_difficulty(self, difficulty: float):
        """
        Set mining difficulty to the given value. Mining difficulty is the probability of finding a block in one step with a mining power of 1.
        * difficulty (float): new difficulty value.
        """
        self.difficulty = difficulty
        self.mine_probability = self.mine_power * self.difficulty

    def consume(self, item: Item):
        """
        Given an Item, performs the necessary action based on its type.
        * item (`sim.base_models.Item`): Item to consume.
        """
        if type(item) == Block:
            logger.info(f'[{self.timestamp}] {self.name} RECEIVED BLOCK {item.id}')
            self.stat_block_rcvs[item.id] = self.timestamp
            self.add_block(item)
            self.publish_item(item, 'block')
        # elif type(item) == Transaction:
        #     logger.debug(f'[{self.timestamp}] {self.name} RECEIVED TX {item.id}')
        #     self.txpool[item.id] = item
        #     self.publish_item(item, 'tx')
        elif type(item) == InvMessage:
            logger.debug(f'[{self.timestamp}] {self.name} RECEIVED INV MESSAGE FOR {item.type} {item.item_id}')
            if item.type == 'block':
                if self.blockchain.get(item.item_id, None) is None:
                    logger.debug(f'[{self.timestamp}] {self.name} RESPONDED WITH GETDATA')
                    self.blockchain[item.item_id] = 'placeholder'  # not none
                    self.send_to(self.outs[item.sender_id], GetDataMessage(item.item_id, item.type, self.id))
            # elif msg.type == 'tx':
            #     if self.txpool.get(msg.item_id, None) is None:
            #         logger.debug(f'[{self.timestamp}] {self.name} RESPONDED WITH GETDATA')
            #         self.txpool[msg.item_id] = 'placeholder'  # not none
            #         getdata = GetDataMessage(msg.item_id, msg.type, self.id, self.timestamp, 10, self.timestamp)
            #         self.__send_to(msg.sender_id, getdata)
        elif type(item) == GetDataMessage:
            logger.debug(f'[{self.timestamp}] {self.name} RECEIVED GETDATA MESSAGE FOR {item.type} {item.item_id}')
            if item.type == 'block':
                self.send_to(self.outs[item.sender_id], self.blockchain[item.item_id])
            # elif msg.type == 'tx':
            #     self.__send_to(msg.sender_id, self.txpool[msg.item_id])

    def generate_block(self, prev: Block = None) -> Block:
        """
        Generates and returns a Block.
        * prev (`Block`): Block to build upon. If not provided, the block is chosen according to the protocol.
        """
        if prev is None:
            prev = self.choose_prev_block()
        block = Block(self, prev.id, prev.height + 1)
        logger.success(f'[{self.timestamp}] {self.name} GENERATED BLOCK {block.id} ==> {prev.id}')
        self.add_block(block)
        self.stat_block_rcvs[block.id] = self.timestamp
        self.publish_item(block, 'block')
        return block

    def add_block(self, block: Block):
        """
        Removes the given block from `heads` if it exists and adds it to the `blockchain`.
        * block (`Block`): Block to add to the blockchain.
        """
        self.blockchain[block.id] = block
        try:
            self.heads.remove(self.blockchain[block.prev_id])
        except (ValueError, KeyError):
            pass
        self.heads.append(block)

    # def generate_transaction(self) -> Transaction:
    #     fee = 10
    #     tx = Transaction(fee, self.id, self.timestamp)
    #     self.txpool[tx.id] = tx
    #     self.publish_item(tx, 'tx')
    #     return tx

    def publish_item(self, item: Item, item_type: str):
        """
        Publishes an item over all of the node's outgoing connections.
        * item (`sim.base_models.Item`): Item to publish.
        * item_type (str): Item's type (e.g. 'block').
        """
        msg = InvMessage(item.id, item_type, self.id)
        for node in self.outs.values():
            self.send_to(node, msg)

    def send_to(self, node: Node, item: Item):
        """
        Send an item to a specific node. Can be used to respond to messages.
        * node (`sim.base_models.Node`): Target node.
        * item (`sim.base_models.Item`): Item to send.
        """
        packet = Packet(item)
        delay = get_delay(self.region, node.region, item.size) / self.iter_seconds
        packet.reveal_at = math.ceil(self.timestamp + delay)
        try:
            node.inbox[packet.reveal_at].append(packet)
        except KeyError:
            node.inbox[packet.reveal_at] = [packet]

    def choose_prev_block(self) -> Block:
        """
        Returns the head of the longest chain.
        """
        heights = [block.height for block in self.heads if block != 'placeholder']
        return self.heads[heights.index(max(heights))]

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
