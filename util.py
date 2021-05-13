from collections import deque

import uuid
import models.item
import models.node


def generate_uuid() -> str:
    return str(uuid.uuid4())


def get_valid_items(queue: deque, timestamp: int) -> list[Item]: #TODO: test
    items = []
    while True:
        try:
            item = queue[-1]
            if item.timestamp == timestamp - 1:
                items.append(queue.pop())
            else:
                break
        except:
            break
    return items

def distance_between(coord1: Coords, coord2: Coords):
    distance_x = abs(coord1.pos_x - coord2.pos_x)