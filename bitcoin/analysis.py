from typing import List, Dict
import math

from models import Miner, Block, Transaction


# union of all nodes' blockchains (excluding the genesis block)
def get_all_blocks(nodes: List[Miner]) -> Dict[str, Block]:
    blocks = dict()
    for node in nodes:
        for _, block in node.blockchain.items():
            if block != 'placeholder' and block.created_at != 0:
                blocks[block.id] = block
    return blocks


# given a block, computes how much time it took for that block to reach each node
def block_prop_delays(block: Block, nodes: List[Miner]) -> List[int]:
    return [node.stat_block_rcvs.get(block.id, 2**64) - block.created_at for node in nodes]


# how much time it takes for block to reach percent of nodes
def block_percentile_delay(block: Block, nodes: List[Miner], percent: float) -> int:
    delays = block_prop_delays(block, nodes)
    nodes_required = math.ceil(percent * len(nodes))
    delays.sort()
    result = delays[nodes_required - 1]
    if result > 2**50: # did not reach that percentage of nodes
        return None
    return sorted(delays)[nodes_required - 1]


# given a node, returns share of blocks that are not built upon
def stale_block_rate(node: Miner) -> float:
    return (len(node.heads) - 1) / len(node.blockchain)


def transactions_per_second(blocks: List[Block], sim_seconds: int) -> float:
    return sum([block.tx_count for block in blocks]) / sim_seconds


def avg_block_interval(node: Miner) -> float:
    total, count = 0, 1
    head = node.choose_prev_block()
    while True:
        block = node.blockchain.get(head.prev_id, None)
        if block is None:
            break
        count += 1
        total += head.created_at - block.created_at
        head = block
    return total / count
