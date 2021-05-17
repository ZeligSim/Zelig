import matplotlib.pyplot as plt
import pickle
import networkx as nx
from multiprocessing import Pool

from models import Block, Miner

def connect(m1: Miner, m2: Miner):
    m1.connect(m2)
    m2.connect(m1)


NODE_COUNT = 5
SIMULATION_TIME = 1000
BLOCK_INTERVAL = 100  # iterations

nodes = [Miner(f'MINER_{i}', (-1)**i, i, 10) for i in range(NODE_COUNT)]

links = []
for i1, m1 in enumerate(nodes):
    for i2, m2 in enumerate(nodes):
        if m1 != m2 and abs(i2 - i1) < 2:
            links.append(m1.connect(m2))

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
    # if time == 5:
    #    a_block = nodes[0].generate_block()
    # if time == 40:
    #     aa_block = miner_a.generate_block()
    # if time == 80:
    #     c_block = miner_c.generate_block(prev=genesis_block)
    # if time == 120:
    #     a_block = miner_a.generate_block()

for node in nodes:
    node.log_blockchain()
    node.log_statistics()
    # with open(f'dumps/{node.name}', 'wb+') as f:
    #     pickle.dump(node, f)


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



