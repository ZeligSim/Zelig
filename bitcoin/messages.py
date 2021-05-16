import sys

sys.path.append("..")

from sim.base_models import *


class InvMessage(Item):
    def __init__(self, item_id: str, type: str, sender_id: str, timestamp: int, size: int, created_at: int):
        super().__init__(timestamp, sender_id, size, created_at)
        self.size = 100  # TODO: inv/getdata message size (61? Decker et al)
        self.item_id = item_id
        self.type = type

class GetDataMessage(Item):
    def __init__(self, item_id: str, type: str, sender_id: str, timestamp: int, size: int, created_at: int):
        super().__init__(timestamp, sender_id, size, created_at)
        self.size = 100  # TODO: inv/getdata message size (61? Decker et al)
        self.item_id = item_id
        self.type = type

class GetBlockchainMessage(Item):
    def __init__(self, sender_id: str, timestamp: int, size: int, created_at: int):
        super().__init__(timestamp, sender_id, size, created_at)
