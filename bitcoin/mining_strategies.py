"""
Mining strategies. For performance, although not strictly enforced, we recommend using these classes as singletons.
"""

from loguru import logger

from bitcoin.models import Miner, BTCBlock
from bitcoin.consensus import Reward


class NullMining:
    """
    The default no-mining strategy. Corresponds to the full nodes in Bitcoin.
    """
    def __init__(self):
        pass

    def setup(self, node: Miner):
        pass

    def choose_head(self, node: Miner) -> BTCBlock:
        """
        Returns the head of the longest chain.
        """
        max_height, max_block = 0, None
        for block in node.blockchain.values():
            if type(block) != str and block.height >= max_height:
                max_block = block
                max_height = block.height
        return max_block

    def generate_block(self, node: Miner, prev: BTCBlock = None) -> BTCBlock:
        """
        Specifies the strategy for mining  a new block.
        """
        pass

    def receive_block(self, node: Miner, block: BTCBlock, relay: bool = False, shallow=False):
        """
        Specifies the strategy for receiving a block.

        The given block is published to the node's peers if `relay` is True.
        """
        node.blockchain[block.id] = block
        node.bookkeeper.save_block(node, block, node.timestamp)
        node.tx_model.update_mempool(node, block)
        if relay:
            node.publish_item(block, 'block')


class HonestMining(NullMining):
    """
    Implements a honest miner following the Bitcoin protocol.
    """
    def __init__(self):
        super().__init__()

    def generate_block(self, node: Miner, prev: BTCBlock = None) -> BTCBlock:
        """
        Generates and returns a Block.
        * prev (`Block`): Block to build upon. If not provided, the block is chosen according to the protocol.
        """
        if prev is None:
            prev = self.choose_head(node)
        block = BTCBlock(node, prev.id, prev.height + 1)
        block = node.tx_model.fill_block(node, block)
        block.reward = node.consensus_oracle.get_reward(node)
        self.receive_block(node, block, relay=True)
        logger.success(f'[{node.timestamp}] {node.name} GENERATED BLOCK {block.id} ==> {prev.id}')
        return block

    def receive_block(self, node: Miner, block: BTCBlock, relay: bool = False, shallow=False):
        super().receive_block(node, block, relay=relay)


class SelfishMining(NullMining):
    """
    Implements a miner  launching the selfish mining attack.
    See https://arxiv.org/abs/1311.0243 for the details.
    """
    def __init__(self):
        super().__init__()

    def setup(self, node: Miner):
        node.private_chain = node.blockchain.copy()
        node.private_branch_len = 0

    def choose_head(self, node: Miner, private=True) -> BTCBlock:
        chain = node.private_chain if private else node.blockchain

        max_height, max_block = 0, None
        for block in chain.values():
            if type(block) != str and block.height >= max_height:
                max_block = block
                max_height = block.height
        return max_block

    def generate_block(self, node: Miner, prev: BTCBlock = None) -> BTCBlock:
        if prev is None:
            prev = self.choose_head(node)
        block = BTCBlock(node, prev.id, prev.height + 1)
        block.id = '[SELFISH]' + block.id
        block = node.tx_model.fill_block(node, block)
        block.reward = node.consensus_oracle.get_reward(node)
        logger.success(f'[{node.timestamp}] {node.name} GENERATED BLOCK {block.id} ==> {prev.id}')

        node.private_chain[block.id] = block
        node.bookkeeper.save_block(node, block, node.timestamp)
        node.tx_model.update_mempool(node, block)

        delta_prev = self.get_delta_prev(node)
        node.private_branch_len += 1
        if delta_prev == 0 and node.private_branch_len == 2:
            self.publish_private_chain(node)
            node.private_branch_len = 0
        return block

    def receive_block(self, node: Miner, block: BTCBlock, relay: bool = False, shallow=False):
        if not shallow:
            delta_prev = self.get_delta_prev(node)

        super().receive_block(node, block, relay=True)

        if not shallow:
            if delta_prev == 0:
                node.private_chain = node.blockchain.copy()
                node.private_branch_len = 0
            elif delta_prev == 1:
                self.publish_private_chain(node)
            else:
                self.publish_private_chain(node)

    def publish_private_chain(self, node: Miner):
        for block in node.private_chain.values():
            node.blockchain[block.id] = block
            node.publish_item(block, 'block')

    def get_delta_prev(self, node: Miner) -> int:
        priv_length = self.choose_head(node).height
        pub_length = self.choose_head(node, private=False).height
        return priv_length - pub_length
