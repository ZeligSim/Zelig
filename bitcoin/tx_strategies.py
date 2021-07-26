import sys
import heapq
import numpy as np

sys.path.append("..")

from bitcoin.models import Miner, Block, Transaction
from bitcoin.messages import InvMessage

from loguru import logger


class TxStrategy:
    def __init__(self):
        pass

    def generate(self, node: Miner) -> Transaction:
        size, value, fee = 5, 5, 5  # TODO
        tx = Transaction(node.id, node.timestamp, size, value, fee)
        return tx

    def publish(self, node: Miner, tx: Transaction, direct: bool = False):
        pass

    def receive(self, node: Miner, tx: Transaction = None):
        pass

    def fill_block(self, node: Miner, block: Block) -> Block:
        pass

    def update_mempool(self, node: Miner, block: Block):
        pass


class NullTxStrategy(TxStrategy):
    def __init__(self):
        super().__init__()

    def generate(self, node: Miner) -> Transaction:
        pass

    def fill_block(self, node: Miner, block: Block) -> Block:
        """
        Assign tx count and total size to block.
        """
        block.tx_count = np.random.normal(2104.72, 236.63)
        block.size = block.tx_count * np.random.normal(615.32, 89.43)
        return block


class FullTxStrategy(TxStrategy):
    def __init__(self):
        super().__init__()

    def generate(self, node: Miner) -> Transaction:
        """
        Create transaction and directly (without inv/getdata) send to all peers.
        """
        tx = super().generate(node)
        self.publish(node, tx, direct=True)

    def publish(self, node: Miner, tx: Transaction, direct: bool = False):
        """
        Send transaction either directly (without inv/getdata) or with inv/getdata to all peers
        """
        msg = tx if direct else InvMessage(tx.id, 'tx', node.id)
        for peer in node.outs.values():
            node.send_to(peer, msg)

    def receive(self, node: Miner, tx: Transaction = None):
        """
        Receive transaction, add it local mempool, save its receipt time, and relay to peers.
        """
        logger.debug(f'[{node.timestamp}] {node.name} RECEIVED TX {tx.id}')
        node.stat_tx_rcvs[tx.id] = node.timestamp
        node.tx_ids[tx.id] = tx
        heapq.heappush(node.mempool, tx)
        self.publish(node, tx, direct=False)  # relay

    def fill_block(self, miner: Miner, block: Block) -> Block:
        """
        Fill block until reaching max block size.
        """
        while block.size < miner.max_block_size:
            try:
                block.add_tx(heapq.heappop(miner.mempool))
            except:
                break
        return block

    def update_mempool(self, node: Miner, block: Block):
        """
        Remove the transactions in the  block from the local mempool.
        """
        for tx in block.transactions:
            del node.tx_ids[tx.id]
            node.mempool.remove(tx)
        heapq.heapify(node.mempool)
