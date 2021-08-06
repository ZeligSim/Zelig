import sys
from typing import List, Dict

sys.path.append('..')

from sim.base_models import *


class Bookkeeper:
    def __init__(self):
        self.num_tx_in_pool: List[int] = []
        self.node_block_rcvs: Dict[str, Dict[str, int]] = dict()
        self.node_tx_rcvs: Dict[str, Dict[str, int]] = dict()

    def register_node(self, node: Node):
        node.bookkeeper = self
        self.node_tx_rcvs[node.id] = dict()
        self.node_block_rcvs[node.id] = dict()

    def save_block(self, node: Node, block: Item, timestamp: int):
        self.node_block_rcvs[node.id][block.id] = timestamp

    def save_tx(self, node: Node, tx: Item, timestamp: int):
        self.node_tx_rcvs[node.id][tx.id] = timestamp

    def get_node_block_rcv(self, node: Node, block: Item) -> int:
        return self.node_block_rcvs[node.id].get(block.id, 2**64)
