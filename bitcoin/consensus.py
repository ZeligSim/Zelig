from sim.base_models import Node, Item
from typing import List
import random


class Reward:
    def __init__(self, node: Node,  value: int):
        self.value = value
        self.timestamp = node.timestamp
        self.node = node


class Oracle:
    def __init__(self, nodes: List[Node], block_interval: int):
        self.block_interval = block_interval
        self.nodes = nodes

    def can_mine(self, miner: Node, *blocks) -> bool:
        pass

    def get_reward(self, miner: Node) -> Reward:
        pass


class PoWOracle(Oracle):
    def __init__(self, nodes: List[Node], block_interval: int, block_reward: int, dynamic=False):
        super().__init__(nodes, block_interval)
        self.dynamic = dynamic
        self.total_power = self.compute_total_power()
        self.block_reward = block_reward

        self.timestamp = 0
        self.new_total_mine_power = 0

    def can_mine(self, miner: Node, *blocks) -> bool:
        if self.dynamic:
            if miner.timestamp > self.timestamp:
                self.total_power = self.new_total_mine_power
                self.new_total_mine_power = 0
                self.timestamp = miner.timestamp
            self.new_total_mine_power += miner.mine_power

        if len(blocks) <= 1:
            return random.random() <= miner.mine_power / (self.block_interval * self.total_power)
        else:
            return [random.random() <= (miner.mine_power / len(blocks)) / (self.block_interval * self.total_power)
                    for _ in blocks]

    def compute_total_power(self) -> float:
        return sum([node.mine_power for node in self.nodes])

    def get_reward(self, miner: Node) -> Reward:
        return Reward(miner, self.block_reward)


