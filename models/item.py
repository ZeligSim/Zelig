import sys
sys.path.append("..")
import util

class Item:

    def __init__(timestamp: int, size: int, delay: int, created_at: int):
        self.id = util.generate_uuid()
        self.timestamp = timestamp
        self.size = size
        self.delay = delay
        self.created_at = created_at
