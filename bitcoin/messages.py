import sys

sys.path.append("..")

from sim.base_models import *


class InvMessage(Item):
    def __init__(self, block_id: str, sender_id: str, timestamp: int, size: int, created_at: int):
        super().__init__(timestamp, sender_id, size, created_at)
        self.block_id = block_id


class GetDataMessage(Item):
    def __init__(self, block_id: str, sender_id: str, timestamp: int, size: int, created_at: int):
        super().__init__(timestamp, sender_id, size, created_at)
        self.block_id = block_id


class GetBlockchainMessage(Item):
    def __init__(self, sender_id: str, timestamp: int, size: int, created_at: int):
        super().__init__(timestamp, sender_id, size, created_at)
