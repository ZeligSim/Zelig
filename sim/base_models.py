"""
The classes that make up the core simulator.
"""
import math
from enum import Enum

from loguru import logger

from typing import List, Dict

from sim import util
from sim.network_util import get_delay, Region


class Item:
    """Represents objects that can be transmitted over a network (e.g. blocks, messages)."""

    def __init__(self, sender_id: str, size: float):
        """
        Create an Item object.
        * sender_id (str): Id of the sender node. Can be used as a return address.
        * size (float): size of the item in bytes.
        """
        self.id = util.generate_uuid()
        self.size = size
        self.sender_id = sender_id


class Block(Item):
    """Represents a Bitcoin block."""

    def __init__(self, creator, prev_id: str, height: int):
        """
        Create a Block object.

        * miner (`Node`): Node that created the block.
        * prev_id (str): Id of the block this block was mined on top of.
        * height (int): Height of the block in the blockchain.
        """
        super().__init__(None, 0)
        self.prev_id = prev_id
        self.miner = creator.name
        self.created_at = creator.timestamp
        self.height = height
        self.size = 0
        self.tx_count = 0
        self.transactions = []
        self.reward: Reward = None

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


class Packet:
    """Wrapper class for transmitting `Item` objects over the network."""

    def __init__(self, payload: Item):
        """
        Create a Packet object.
        * payload (`Item`): Item contained in the packet.
        """
        self.payload = payload
        self.reveal_at = 0


class Node:
    """Represents the participants in the blockchain system."""

    def __init__(self, iter_seconds, name, region, timestamp=0):
        """
        Create a Node object.
        * region (`sim.util.Region`): Geographic region of the node.
        * timestamp (int): Initial timestamp of the node. Defaults to zero.
        """
        self.id = util.generate_uuid()
        self.name = name
        self.timestamp = timestamp
        self.region = region
        self.iter_seconds = iter_seconds

        self.blockchain: Dict[str, Block] = dict()
        """A dictionary that stores `BTCBlock` ids as keys and `BTCBlock`s as values."""

        self.heads: List[Block] = []
        """Stores the current head blocks (blocks that hasn't been mined on) as a list."""

        self.inbox: Dict[int, List[Packet]] = dict()
        """Node's inbox with simulation timestamps as keys and lists of `Item`s to be consumed at that timestamp as values."""

        self.ins: Dict[str, Node] = dict()
        """Dictionary storing incoming connections. Keys are `Node` ids and values are `Node`s."""

        self.outs: Dict[str, Node] = dict()
        """Dictionary storing outgoing connections. Keys are `Node` ids and values are `Node`s."""

        self.last_reveal_times: Dict[str, int] = dict()
        """
        Dictionary with node ids as keys and integers as values. Values correspond to the reveal time of the last message sent to the node with the given id.
        
        This is used to simulate links that can only  transmit one message at a time. A new message starts transmission only after the previous one has been received.
        """

    def __getstate__(self):
        """Return state values to be pickled."""
        state = self.__dict__.copy()
        # Remove the unpicklable entries.
        del state['ins']
        del state['outs']
        del state['inbox']
        del state['timestamp']
        return state

    def __str__(self) -> str:
        return self.name

    def __setstate__(self, state):
        """Restore state from the unpickled state values."""
        self.__dict__.update(state)

    def step(self, seconds: float) -> List[Item]:
        """
        Perform one simulation step. Increments its timestamp by 1 and returns the list of `Item` objects to act on in that step.
        * seconds (float): How many real-time seconds one simulation step corresponds to.
        """
        self.timestamp += 1
        try:
            return [packet.payload for packet in self.inbox.pop(self.timestamp)]
        except KeyError:
            return []

    def reset(self):
        """
        Reset node state back to simulation start, deleting connections as well.
        """
        self.timestamp = 0
        self.blockchain = dict()
        self.heads = []
        self.inbox = dict()
        self.ins = dict()
        self.outs = dict()
        self.last_reveal_times = dict()

    def send_to(self, node, item: Item):
        """
        Send an item to a specific node. Can be used to respond to messages.
        * node (`sim.base_models.Node`): Target node.
        * item (`sim.base_models.Item`): Item to send.
        """
        packet = Packet(item)
        delay = get_delay(self.region, node.region, item.size) / self.iter_seconds
        reveal_time = math.ceil(max(self.timestamp, self.last_reveal_times.get(node.id, 0)) + delay)
        self.last_reveal_times[node.id] = reveal_time
        packet.reveal_at = reveal_time
        try:
            node.inbox[packet.reveal_at].append(packet)
        except KeyError:
            node.inbox[packet.reveal_at] = [packet]

    def save_block(self, block: Block, relay=False):
        self.blockchain[block.id] = block
        try:
            self.heads.remove(self.blockchain[block.prev_id])
        except (ValueError, KeyError):
            pass
        self.heads.append(block)

    def connect(self, *argv):
        """
        Establish an outgoing connection to one or more nodes.
        * argv (`sim.base_models.Node`+): Node(s) to establish connections with.
        """
        for node in argv:
            self.outs[node.id] = node
            node.ins[self.id] = self

    def print_blockchain(self, head: Block = None):
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


class Reward:
    def __init__(self, node: Node, value: int):
        self.value = value
        self.timestamp = node.timestamp
        self.node = node
