from loguru import logger

from bitcoin.models import Miner, BTCBlock
from bitcoin.consensus import Reward


class NullMining:
    def __init__(self):
        pass

    def choose_head(self, node: Miner) -> BTCBlock:
        """
        Returns the head of the longest chain.
        """
        heights = [block.height for block in node.heads if block != 'placeholder']
        return node.heads[heights.index(max(heights))]

    def mine_block(self,  node: Miner, prev: BTCBlock = None) -> BTCBlock:
        pass


class HonestMining(NullMining):
    def __init__(self):
        super().__init__()

    def mine_block(self, node: Miner, prev: BTCBlock = None) -> BTCBlock:
        """
        Generates and returns a Block.
        * prev (`Block`): Block to build upon. If not provided, the block is chosen according to the protocol.
        """
        if prev is None:
            prev = self.choose_head(node)
        block = BTCBlock(node, prev.id, prev.height + 1)
        block = node.tx_model.fill_block(node, block)
        block.reward = node.consensus_oracle.get_reward(node)
        node.save_block(block, relay=True)
        logger.success(f'[{node.timestamp}] {node.name} GENERATED BLOCK {block.id} ==> {prev.id}')
        return block
