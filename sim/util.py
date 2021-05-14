import uuid
import math


def generate_uuid() -> str:
    return str(uuid.uuid4())


class Coords:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def distance(self, c) -> float:
        return math.sqrt((self.x - c.x) ** 2 + (self.y - c.y) ** 2)


# FIXME: this will only be executed by Nodes, can implement there
# def get_valid_items(queue: deque, timestamp: int) -> List[Item]: #TODO: test
#     items = []
#     while True:
#         try:
#             item = queue[-1]
#             if item.timestamp == timestamp - 1:
#                 items.append(queue.pop())
#             else:
#                 break
#         except:
#             break
#     return items

