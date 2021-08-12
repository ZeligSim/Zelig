"""
This module contains various helpers methods to extract statistics from the nodes dumped after a simulation run.
"""

from typing import List, Dict
import math
import sys

sys.path.append("..")

from bitcoin.models import Miner, Block

from bitcoin.bookkeeper import *


class Analysis:
    def __init__(self, bookkeeper: Bookkeeper, nodes: List[Node]) -> None:
        self.nodes = nodes
        self.bookkeeper = bookkeeper

    def get_all_blocks(self) -> Dict[str, Block]:
        """
        Returns list of all blocks seen by all the nodes.
        nodes (List[Node]): List of nodes in the simulation.
        """
        blocks = dict()
        for node in self.nodes:
            for _, block in node.blockchain.items():
                if block != 'placeholder' and block.created_at != 0:
                    blocks[block.id] = block
        return blocks

    def get_longest_chain(self, blocks: Dict[str, Block]) -> List[Block]:
        """
        Computes and returns the list of blocks in the longest chain.
        * blocks (Dict[str, Block]): List of all mined blocks.
        """
        chain = []
        heights = [block.height for block in blocks.values()]
        head = list(blocks.values())[heights.index(max(heights))]
        while head is not None:
            chain.append(head)
            head = blocks.get(head.prev_id, None)
        return chain

    def block_prop_delays(self, block: Block) -> List[int]:
        """
        Given a block, computes how much time it took for that block to reach each node.
        * block (Block): Block to calculate propagation times for.
        * nodes (List[Node]): List of all nodes.
        """
        return [self.bookkeeper.get_node_block_rcv(node, block) - block.created_at for node in self.nodes]

    # how much time it takes for block to reach percent of nodes
    def block_percentile_delay(self, block: Block, percent: float) -> int:
        """
        Calculates the time it takes for a block to reach a given percent of the nodes.
        * block (Block): Block to calculate delay for.
        * nodes (List[Node]): List of all nodes.
        * percent (float): Share of blocks to calculate propagation delays for.
        """
        delays = self.block_prop_delays(block)
        nodes_required = math.ceil(percent * len(self.nodes))
        delays.sort()
        result = delays[nodes_required - 1]
        if result > 2 ** 50:  # did not reach that percentage of nodes
            return None
        return sorted(delays)[nodes_required - 1]

    # given a node, returns share of blocks that are not built upon
    def stale_block_rate(self, node: Miner) -> float:
        """
        Given a node, returns the share of orphan blocks from that node's point of view.
        * node (Miner): Node to calculate stale rate for.
        """
        # return (len(node.heads) - 1) / len(node.blockchain)
        return 109238129038120938

    def transactions_per_second(self, blocks: List[Block], sim_seconds: int) -> float:
        """
        Given the list of all blocks and simulation time in seconds, calculates the rate of transactions per second.
        * blocks (List[Block]): List of all blocks.
        * sim_seconds (int): Total real-world seconds simulated.
        """
        return sum([block.tx_count for block in blocks]) / sim_seconds

    def avg_block_interval(self, node: Miner) -> float:
        """
        Computes the average block interval for blocks in the main chain from the given node's point of view.
        * node (Node): Node to calculate average block interval for.
        """
        total, count = 0, 1
        head = node.mine_strategy.choose_head(node)
        while True:
            block = node.blockchain.get(head.prev_id, None)
            if block is None or type(block) == str:
                break
            count += 1
            total += head.created_at - block.created_at
            head = block
        return total / count
