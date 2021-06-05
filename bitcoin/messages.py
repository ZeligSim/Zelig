"""
This module contains the various message types that can be sent over the Bitcoin network.
"""

import sys

sys.path.append("..")

from sim.base_models import *


class InvMessage(Item):
    """Represents INV messages used to announce new blocks."""
    def __init__(self, item_id: str, type: str, sender_id: str):
        """
        Create an InvMessage object.
        * item_id (str): Id of the block/transaction being announced.
        * sender_id (str): Id of the sender node. Can be used as a return address.
        * size (float): size of the item in bytes.
        """
        super().__init__(sender_id, 100)
        self.size = 100
        self.item_id = item_id
        self.type = type


class GetDataMessage(Item):
    """Represents GET_DATA messages used to request blocks after receiving INV messages."""
    def __init__(self, item_id: str, type: str, sender_id: str):
        """
        Create a GetDataMessage object.
        * item_id (str): Id of the block/transaction being requested.
        * sender_id (str): Id of the sender node. Can be used as a return address.
        * size (float): size of the item in bytes.
        """
        super().__init__(sender_id, 100)
        self.size = 100
        self.item_id = item_id
        self.type = type
