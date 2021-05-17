import matplotlib.pyplot as plt
import pickle
import networkx as nx
from multiprocessing import Pool

from models import Block, Miner


def connect(m1: Miner, m2: Miner):
    m1.connect(m2)
    m2.connect(m1)


SIMULATION_TIME = 100000
BLOCK_INTERVAL = 6000  # iterations

us = Miner('US', 80, 150, 73)
ch = Miner('CH', 600, 180, 650)
eu = Miner('EU', 360, 110, 20)
ru = Miner('RU', 520, 80, 69)
af = Miner('AF', 400, 250, 5)
au = Miner('AU', 690, 360, 15)
me = Miner('ME', 445, 175, 120)
sa = Miner('SA', 190, 320, 15)

nodes = [us, ch, eu, ru, af, au, me, sa]

links = []
links += us.connect(sa, eu, af)
links += ch.connect(au, me, eu, ru, af)
links += eu.connect(us, ch, me, ru, af)
links += ru.connect(ch, eu, me)
links += af.connect(us, sa, me, eu, ch, au)
links += au.connect(ch, af)
links += me.connect(af, ru, eu, ch)
links += sa.connect(us, af)


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

for node in nodes:
    node.log_blockchain()
    node.log_statistics()
    with open(f'dumps/{node.name}', 'wb+') as f:
        pickle.dump(node, f)


plt.plot(active_links)
plt.axhline(len(links), color='red')
plt.title('Number of active links')
plt.show()

G = nx.DiGraph()
for node in nodes:
    G.add_node(node, pos=(node.pos.x, node.pos.y))
for node in nodes:
    for link in node.outs:
        G.add_edge(node, link.end)
img = plt.imread("etc/world.webp")
fig, ax = plt.subplots()
ax.imshow(img)
nx.draw_networkx_nodes(G, nx.get_node_attributes(G, 'pos'), node_color='red')
nx.draw_networkx_edges(G, nx.get_node_attributes(G, 'pos'),
                       connectionstyle="arc3,rad=0")
plt.show()



