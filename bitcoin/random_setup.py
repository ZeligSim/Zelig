import matplotlib.pyplot as plt
import pickle
import random
import math
import networkx as nx
from multiprocessing import Pool

from models import Block, Miner


NODE_COUNT = 8
SIMULATION_TIME = 1000
CONNECTIONS_PER_NODE = 2
BLOCK_INTERVAL = 100  # iterations

nodes, links = [], []

for i in range(NODE_COUNT):
    x = 1 * math.cos(2 * math.pi * i / NODE_COUNT)
    y = 1 * math.sin(2 * math.pi * i / NODE_COUNT)
    node = Miner(f'MINER_{i}', x, y, 100)
    nodes.append(node)

for node in nodes:
    for i in range(CONNECTIONS_PER_NODE):
        m2 = random.choice(nodes)
        while m2 == node:
            m2 = random.choice(nodes)
        links += node.connect(m2)

total_mine_power = sum([miner.mine_power for miner in nodes])
difficulty = 1 / (BLOCK_INTERVAL * total_mine_power)

genesis_block = Block('satoshi', 'satoshi', 0, 0, None)

for node in nodes:
    node.difficulty = difficulty
    node.add_block(genesis_block)

active_links = []
# one iter corresponds to 0.1 sec
for time in range(1, SIMULATION_TIME):
    active_links.append(sum([len(link.queue) > 0 for link in links]))
    for node in nodes:
        node.step()


# LOG / STATS
for node in nodes:
    node.log_blockchain()
    node.log_statistics()
    with open(f'dumps/{node.name}', 'wb+') as f:
        pickle.dump(node, f)

plt.plot(active_links)
plt.axhline(len(links), color='red')
plt.title('Number of active links')
plt.show()

if NODE_COUNT <= 100:
    G = nx.DiGraph()
    for node in nodes:
        G.add_node(node, pos=(node.pos.x, node.pos.y))
    for node in nodes:
        for link in node.outs:
            G.add_edge(node, link.end)
    fig, ax = plt.subplots()
    nx.draw_networkx_nodes(G, nx.get_node_attributes(G, 'pos'))
    nx.draw_networkx_edges(G, nx.get_node_attributes(G, 'pos'),
                           connectionstyle="arc3,rad=0.25")
    plt.show()



