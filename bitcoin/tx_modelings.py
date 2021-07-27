import sys
import heapq
import random

sys.path.append("..")

from bitcoin.models import Miner, Block, Transaction
from bitcoin.messages import InvMessage

from loguru import logger


class TxModel:
    def __init__(self):
        pass

    def generate(self, node: Miner) -> Transaction:
        size = random.gauss(509.23, 191.45)  # https://tradeblock.com/bitcoin/historical/1w-f-tsize_per_avg-01101
        fee = random.gauss(7.17E-5, 7.53E-5)  # https://www.blockchain.com/btc/blocks?page=1
        value = random.gauss(1.1185684485714287, 2.2917997016339346)  # same
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


class NoneTxModel(TxModel):
    def __init__(self):
        super().__init__()

    def generate(self, node: Miner) -> Transaction:
        pass

    def fill_block(self, node: Miner, block: Block) -> Block:
        """
        Assign tx count and total size to block.
        """
        block.tx_count = random.gauss(2104.72, 236.63)
        block.size = block.tx_count * random.gauss(615.32, 89.43)
        return block


class SimpleTxModel(TxModel):
    def __init__(self):
        """
        Initialize shared mempool.
        """
        super().__init__()
        self.mempool = []

    def generate(self, node: Miner) -> Transaction:
        """
        Create transaction and add it to shared mempool.
        """
        tx = super().generate(node)
        heapq.heappush(self.mempool, tx)

    def fill_block(self, node: Miner, block: Block) -> Block:
        """
        Add txs to block from shared mempool until it reaches max size.
        """
        while block.size < node.max_block_size:
            try:
                block.add_tx(heapq.heappop(self.mempool))
            except IndexError:
                break
        return block

    def update_mempool(self, node: Miner, block: Block):
        """
        Remove transactions in the block from the shared mempool.
        """
        for tx in block.transactions:
            try:
                node.mempool.remove(tx)
            except ValueError:
                pass
        heapq.heapify(self.mempool)


class FullTxModel(TxModel):
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
            except IndexError:
                break
        return block

    def update_mempool(self, node: Miner, block: Block):
        """
        Remove the transactions in the  block from the local mempool.
        """
        for tx in block.transactions:
            # del node.tx_ids[tx.id]
            try:
                node.mempool.remove(tx)
            except ValueError:
                pass
        heapq.heapify(node.mempool)
