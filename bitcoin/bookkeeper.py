import sys
from typing import List, Dict

sys.path.append('..')

from sim.base_models import *


class Bookkeeper:
    def __init__(self):
        self.num_tx_in_pool: List[int] = []
        self.node_block_rcvs: Dict[str, Dict[str, int]] = dict()
        self.node_tx_rcvs: Dict[str, Dict[str, int]] = dict()
        self.node_compute: Dict[str, List[int]] = dict()
        self.node_space: Dict[str, List[int]] = dict()

    def register_node(self, node: Node):
        node.bookkeeper = self
        self.node_tx_rcvs[node.id] = dict()
        self.node_block_rcvs[node.id] = dict()
        self.node_compute[node.id] = []
        self.node_space[node.id] = []

    def save_block(self, node: Node, block: Item, timestamp: int):
        self.node_block_rcvs[node.id][block.id] = timestamp

    def save_tx(self, node: Node, tx: Item, timestamp: int):
        self.node_tx_rcvs[node.id][tx.id] = timestamp

    def get_node_block_rcv(self, node: Node, block: Item) -> int:
        return self.node_block_rcvs[node.id].get(block.id, 2**64)

    def use_compute(self, node: Node, amount: int):
        self.node_compute[node.id].append(amount)

    def use_space(self, node: Node, amount: int):
        self.node_space[node.id].append(amount)

