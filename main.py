import random
from omegaconf import DictConfig, OmegaConf
import hydra
import pickle
from typing import List
from pathlib import Path

from bitcoin.models import Block, Miner
from sim.util import Region


@hydra.main(config_name="config")
def main(cfg: DictConfig) -> List[Miner]:
    links, nodes = [], []

    for elt in cfg.nodes:
        mine_power = elt.region_mine_power / elt.count
        for idx in range(elt.count):
            nodes.append(Miner(f'MINER_{elt.region}_{idx}', 0, 0, mine_power, Region(elt.region)))

    genesis_block = Block('satoshi', 'satoshi', 0, 0, None)
    total_mine_power = sum([miner.mine_power for miner in nodes])
    difficulty = 1 / (cfg.block_int_iters * total_mine_power)

    for node in nodes:
        node.difficulty = difficulty
        node.add_block(genesis_block)
        node_index = nodes.index(node)
        first_part = nodes[:node_index]
        second_part = nodes[node_index + 1:]
        for i in range(cfg.connections_per_node):
            n2 = random.choice(first_part + second_part)
            links += node.connect(n2) + n2.connect(node)

    for time in range(1, cfg.simulation_iters):
        for node in nodes:
            node.step(cfg.iter_seconds)

    Path(f'../../../dumps/{cfg.sim_name}').mkdir(parents=True, exist_ok=True)
    for node in nodes:
        node.log_blockchain()
        with open(f'../../../dumps/{cfg.sim_name}/{node.name}', 'wb+') as f:
            pickle.dump(node, f)


main()

# plt.plot(active_links)
# plt.axhline(len(links), color='red')
# plt.title('Number of active links')
# plt.show()

# VISUALIZE NETWORK
# if NODE_COUNT <= 100:
#     G = nx.DiGraph()
#     for node in nodes:
#         G.add_node(node, pos=(node.pos.x, node.pos.y))
#     for node in nodes:
#         for link in node.outs:
#             G.add_edge(node, link.end)
#     # fig, ax = plt.subplots()
#     fig = plt.figure(figsize=(500, 500))
#     nx.draw_networkx_nodes(G, nx.get_node_attributes(G, 'pos'))
#     nx.draw_networkx_edges(G, nx.get_node_attributes(G, 'pos'),
#                            connectionstyle="arc3,rad=0.25")
#     plt.show()

# VISUALIZE CHAINS
# miner = nodes[0]
# G = nx.DiGraph()
# for idx, block in enumerate(miner.blockchain.values()):
#     G.add_node(block, pos=(idx, 0))
# for idx, block in enumerate(miner.blockchain.values()):
#     parent = miner.blockchain.get(block.prev_id, None)
#     if parent is not None:
#         G.add_edge(block, parent)
# fig, ax = plt.subplots()
# nx.draw_networkx_nodes(G, nx.get_node_attributes(G, 'pos'))
# nx.draw_networkx_edges(G, nx.get_node_attributes(G, 'pos'),
#                        connectionstyle="arc3,rad=0.25")
# plt.show()
