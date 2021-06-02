import sys

sys.path.append("..")

from sim.base_models import *


class InvMessage(Item):
    def __init__(self, item_id: str, type: str, sender_id: str):
        super().__init__(sender_id, 100)
        self.size = 100  # TODO: inv/getdata message size (61? Decker et al)
        self.item_id = item_id
        self.type = type


class GetDataMessage(Item):
    def __init__(self, item_id: str, type: str, sender_id: str):
        super().__init__(sender_id, 100)
        self.size = 100  # TODO: inv/getdata message size (61? Decker et al)
        self.item_id = item_id
        self.type = type
