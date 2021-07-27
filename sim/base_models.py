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
        self.iter_seconds = 0.1


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

    def reset(self):
        """
        Reset node state back to simulation start, deleting connections as well.
        """
        self.timestamp = 0
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

    def connect(self, *argv):
        """
        Establish an outgoing connection to one or more nodes.
        * argv (`sim.base_models.Node`+): Node(s) to establish connections with.
        """
        for node in argv:
            self.outs[node.id] = node
            node.ins[self.id] = self
