"""
The classes that make up the core simulator.
"""


from collections import deque
from enum import Enum

from loguru import logger

from typing import List, Dict

from sim import util
from sim.network_util import speed, latency
from sim.util import Region


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
    def __init__(self, region, timestamp=0):
        """
        Create a Node object.
        * region (`sim.util.Region`): Geographic region of the node.
        * timestamp (int): Initial timestamp of the node. Defaults to zero.
        """
        self.id = util.generate_uuid()
        self.timestamp = timestamp
        self.region = region

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
