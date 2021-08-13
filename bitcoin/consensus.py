from sim.base_models import Node, Item, Reward
from typing import List
import random


class Oracle:
    def __init__(self, nodes: List[Node], block_interval: int):
        self.block_interval = block_interval
        self.nodes = nodes

    def can_mine(self, miner: Node, *blocks) -> bool:
        """
        Returns true if the given miner is allowed to mine the given block(s) in the current step.
        If multiple blocks are provided, should return a boolean list.
        """
        pass

    def get_reward(self, miner: Node) -> Reward:
        """
        Returns mining reward.
        """
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
        """
        A miner is allowed to mine each block with a certain probability computed with respect to that miner's power, total power, and the expected block interval.
        """
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
        """
        Returns the total mining power, iterating over all nodes.
        """
        return sum([node.mine_power for node in self.nodes])

    def get_reward(self, miner: Node) -> Reward:
        """
        Returns the mining reward. For PoW, this is a fixed value.
        """
        return Reward(miner, self.block_reward)


