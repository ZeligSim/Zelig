from loguru import logger

from bitcoin.models import Miner, BTCBlock
from bitcoin.consensus import Reward


class NullMining:
    def __init__(self):
        pass

    def setup(self, node: Miner):
        pass

    def choose_head(self, node: Miner) -> BTCBlock:
        """
        Returns the head of the longest chain.
        """
        heights = [block.height for block in node.heads if block != 'placeholder']
        return node.heads[heights.index(max(heights))]

    def generate_block(self, node: Miner, prev: BTCBlock = None) -> BTCBlock:
        pass

    def receive_block(self, node: Miner, block: BTCBlock, relay: bool = False, shallow=False):
        """
        Remove the given block from `heads` if it exists and add it to the `blockchain`.
        """
        node.blockchain[block.id] = block
        try:
            node.heads.remove(node.blockchain[block.prev_id])
        except (ValueError, KeyError):
            pass
        node.heads.append(block)
        node.bookkeeper.save_block(node, block, node.timestamp)
        node.tx_model.update_mempool(node, block)
        if relay:
            node.publish_item(block, 'block')


class HonestMining(NullMining):
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
    def __init__(self):
        super().__init__()

    def setup(self, node: Miner):
        node.private_heads = node.heads.copy()
        node.private_chain = node.blockchain.copy()
        node.private_branch_len = 0

    def choose_head(self, node: Miner) -> BTCBlock:
        """
        Always mine at the head of the private chain
        """
        heights = [block.height for block in node.private_heads if block != 'placeholder']
        return node.private_heads[heights.index(max(heights))]

    def generate_block(self, node: Miner, prev: BTCBlock = None) -> BTCBlock:
        # create block
        if prev is None:
            prev = self.choose_head(node)
        block = BTCBlock(node, prev.id, prev.height + 1)
        block = node.tx_model.fill_block(node, block)
        block.reward = node.consensus_oracle.get_reward(node)
        logger.success(f'[{node.timestamp}] {node.name} GENERATED BLOCK {block.id} ==> {prev.id}')

        # save to private chain
        node.private_chain[block.id] = block
        node.private_heads.append(block)
        node.bookkeeper.save_block(node, block, node.timestamp)
        node.tx_model.update_mempool(node, block)

        # publish private chain if conditions are met
        delta_prev = self.get_delta_prev(node)
        node.private_branch_len += 1
        if delta_prev == 0 and node.private_branch_len == 2:
            logger.info('SELFISH MINER PUBLISHED PRIVATE BLOCKS')
            for block in node.private_chain.values():
                node.blockchain[block.id] = block
                node.publish_item(block, 'block')
            node.private_branch_len = 0
        return block

    def receive_block(self, node: Miner, block: BTCBlock, relay: bool = False, shallow=False):
        # append new block to public chain
        super().receive_block(node, block, relay=True)

        if not shallow:
            delta_prev = self.get_delta_prev(node)
            if delta_prev == 0:
                # they win. reset.
                node.private_chain = node.blockchain.copy()
                node.private_branch_len = 0
            elif delta_prev == 1:
                # publish last block in private chain
                last_priv = self.choose_head(node)
                node.publish_item(last_priv, 'block')
            # elif delta_prev == 2:
            else:
                # publish all private chain
                logger.info('SELFISH MINER PUBLISHED PRIVATE BLOCKS')
                for block in node.private_chain.values():
                    node.blockchain[block.id] = block
                    node.publish_item(block, 'block')

    def get_delta_prev(self, node: Miner) -> int:
        prev_length = max([block.height for block in node.private_heads if block != 'placeholder'] + [0])
        pub_length = max([block.height for block in node.heads if block != 'placeholder'] + [0])
        return prev_length - pub_length
