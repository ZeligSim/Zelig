from sim.base_models import Node, Link, Item

nodes = [Node(x,y) for x,y in zip(range(10), range(10))]

for node in nodes:
    print(node)