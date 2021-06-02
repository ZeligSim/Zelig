import random
from omegaconf import DictConfig
import hydra
import pickle
from typing import List
from pathlib import Path
import time

from bitcoin.models import Block, Miner
from sim.util import Region


@hydra.main(config_name="config")
def main(cfg: DictConfig) -> List[Miner]:
    for rep in range(cfg.sim_reps):
        links, nodes = [], []

        sim_name = f'{cfg.sim_name}_{rep}'
        simulation_iters = cfg.simulation_iters
        iter_seconds = cfg.iter_seconds
        connections_per_node = cfg.connections_per_node

        # -- create nodes --
        setup_start = time.time()
        cfg_nodes = cfg.nodes
        for elt in cfg_nodes:
            nodes_in_region = 1
            # nodes_in_region = elt.count
            mine_power = elt.region_mine_power / nodes_in_region
            for idx in range(nodes_in_region):
                region = elt.region
                nodes.append(Miner(f'MINER_{region}_{idx}', mine_power, Region(region)))

        genesis_block = Block(Miner('satoshi', 0, None), None, 0)
        total_mine_power = sum([miner.mine_power for miner in nodes])
        difficulty = 1 / (cfg.block_int_iters * total_mine_power)

        # -- setup random connections for nodes --
        for node in nodes:
            node.set_difficulty(difficulty)
            node.add_block(genesis_block)
            node_index = nodes.index(node)
            first_part = nodes[:node_index]
            second_part = nodes[node_index + 1:]
            for i in range(connections_per_node):
                n2 = random.choice(first_part + second_part)
                node.connect(n2)
                n2.connect(node)
        setup_end = time.time()
        setup_time = setup_end - setup_start

        # -- start sim --
        sim_start = time.time()
        for i in range(1, simulation_iters):
            [node.step(iter_seconds) for node in nodes]
        sim_end = time.time()
        total_sim_time = sim_end - sim_start

        Path(f'../../../dumps/{sim_name}').mkdir(parents=True, exist_ok=True)
        for node in nodes:
            node.log_blockchain()
            with open(f'../../../dumps/{sim_name}/{node.name}', 'wb+') as f:
                pickle.dump(node, f)

        print(f'COMPLETED {sim_name}')
        print(f'Times (seconds):')
        print(f'\tSetup time: {setup_time:.7f}')
        print(f'\tTotal sim time: {total_sim_time:.7f}')
        print(f'\tAvg per iter: {(total_sim_time / simulation_iters):.7f}')


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
