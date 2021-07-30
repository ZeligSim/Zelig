"""
Main implementation of the Bitcoin simulator.
"""

import random
import sys

from typing import Dict

sys.path.append("..")

from loguru import logger

from sim.base_models import *
from bitcoin.messages import InvMessage, GetDataMessage


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
        self.size = 80  # size of block header in bytes
        self.tx_count = 0
        self.transactions = []

    def add_tx(self, tx):
        self.transactions.append(tx)
        self.size += tx.size
        self.tx_count += 1

    def has_tx(self, tx):
        return tx in self.transactions

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['sender_id']
        del state['size']
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)

    def __str__(self) -> str:
        return f'BLOCK (id:{self.id}, prev: {self.prev_id})'


class Transaction(Item):
    def __init__(self, sender_id: str, created_at: int, size: float, value: float, fee: float):
        super().__init__(sender_id, 0)
        self.fee = 0
        self.size = 400  # bytes
        self.value = 100
        self.created_at = created_at
        self.feerate = self.fee / self.size

    def __str__(self) -> str:
        return f'TX (id:{self.id}, value: {self.value}, feerate: {self.feerate})'

    def __lt__(self, other):
        """
        Compare this Transaction object with another on the basis of their feerates.
        We want the mempool heap to treat the highest feerate as the "minimum" element, so the comparison operator is <=.
        """
        return self.feerate >= other.feerate


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
        self.max_block_size = 1

        self.tx_model = None
        self.tx_per_iter = 0

        self.mine_strategy = None

        self.blockchain: Dict[str, Block] = dict()
        """A dictionary that stores `Block` ids as keys and `Block`s as values."""

        self.mempool: List[Transaction] = []  # heapq
        self.tx_ids: Dict[str, Transaction] = dict()

        self.heads: List[Block] = []
        """Stores the current head blocks (blocks that hasn't been mined on) as a list."""

        self.stat_block_rcvs: Dict[str, int] = dict()
        """Stores the receipt time of blocks, to calculate metrics such as block propagation times."""

        self.stat_tx_rcvs: Dict[str, int] = dict()
        """Stores the receipt time of transactions, for analysis."""

        logger.info(f'CREATED MINER {self.name}')

    def __getstate__(self):
        """Return state values to be pickled."""
        state = self.__dict__.copy()
        # Remove the unpicklable entries.
        del state['ins']
        del state['outs']
        del state['inbox']
        del state['timestamp']
        del state['mempool']
        del state['tx_model']
        del state['mine_strategy']
        return state

    def __setstate__(self, state):
        """Restore state from the unpickled state values."""
        self.__dict__.update(state)

    def __str__(self) -> str:
        return self.name

    def reset(self):
        """Reset state back to simulation start."""
        super().reset()
        self.blockchain = dict()
        self.heads = []
        self.stat_block_rcvs = dict()

    def step(self, seconds: float):
        items = super().step(seconds)
        for item in items:
            self.consume(item)

        # TODO
        # tx_count = math.ceil(random.gauss(self.tx_per_iter, self.tx_per_iter / 10))
        tx_count = self.tx_per_iter
        for c in range(tx_count):
            self.tx_model.generate(self)

        if random.random() <= self.mine_probability:
            self.mine_strategy.mine_block(self)

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
            self.save_and_relay_block(item)
        elif type(item) == Transaction:
            self.tx_model.receive(self, item)
        elif type(item) == InvMessage:
            logger.debug(f'[{self.timestamp}] {self.name} RECEIVED INV MESSAGE FOR {item.type} {item.item_id}')
            if item.type == 'block':
                if self.blockchain.get(item.item_id, None) is None:
                    logger.debug(f'[{self.timestamp}] {self.name} RESPONDED WITH GETDATA')
                    self.blockchain[item.item_id] = 'placeholder'  # not none
                    self.send_to(self.outs[item.sender_id], GetDataMessage(item.item_id, item.type, self.id))
            elif item.type == 'tx':
                if self.tx_ids.get(item.item_id, None) is None:
                    logger.debug(f'[{self.timestamp}] {self.name} RESPONDED WITH GETDATA')
                    self.tx_ids[item.item_id] = True
                    self.send_to(self.outs[item.sender_id], GetDataMessage(item.item_id, item.type, self.id))
        elif type(item) == GetDataMessage:
            logger.debug(f'[{self.timestamp}] {self.name} RECEIVED GETDATA MESSAGE FOR {item.type} {item.item_id}')
            if item.type == 'block':
                self.send_to(self.outs[item.sender_id], self.blockchain[item.item_id])
            elif item.type == 'tx':
                self.send_to(self.outs[item.sender_id], self.tx_ids[item.item_id])

    def save_and_relay_block(self, block: Block):
        """
        Removes the given block from `heads` if it exists and adds it to the `blockchain`.
        * block (`Block`): Block to add to the blockchain.
        """
        self.blockchain[block.id] = block
        try:
            self.heads.remove(self.blockchain[block.prev_id])
        except (ValueError, KeyError):
            pass
        self.stat_block_rcvs[block.id] = self.timestamp
        self.heads.append(block)
        self.tx_model.update_mempool(self, block)
        self.publish_item(block, 'block')

    def publish_item(self, item: Item, item_type: str):
        """
        Publishes an item over all of the node's outgoing connections.
        * item (`sim.base_models.Item`): Item to publish.
        * item_type (str): Item's type (e.g. 'block').
        """
        msg = InvMessage(item.id, item_type, self.id)
        for node in self.outs.values():
            self.send_to(node, msg)

    def log_blockchain(self):
        head = self.mine_strategy.choose_head()
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
