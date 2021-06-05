import random
import sys

from omegaconf import DictConfig
import hydra
import pickle
from typing import List
from pathlib import Path
import time

from loguru import logger

from bitcoin.models import Block, Miner
from sim.util import Region


@hydra.main(config_name="config")
def main(cfg: DictConfig) -> List[Miner]:
    logger.remove()
    logger.add(sys.stdout, level=cfg.log_level)

    for rep in range(cfg.sim_reps):
        links, nodes = [], []

        sim_name = f'{cfg.sim_name}_{rep}'
        simulation_iters = cfg.simulation_iters
        iter_seconds = cfg.iter_seconds
        connections_per_node = cfg.connections_per_node
        results_dir = cfg.results_directory

        logger.warning(f'Simulation {sim_name} ({simulation_iters} iterations).')
        logger.warning('Creating nodes...')

        # -- create nodes --
        cfg_nodes = cfg.nodes
        for elt in cfg_nodes:
            nodes_in_region = 2
            # nodes_in_region = elt.count
            mine_power = elt.region_mine_power / nodes_in_region
            region = elt.region
            for idx in range(nodes_in_region):
                nodes.append(Miner(f'MINER_{region}_{idx}', mine_power, Region(region)))

        genesis_block = Block(Miner('satoshi', 0, None), None, 0)
        total_mine_power = sum([miner.mine_power for miner in nodes])
        difficulty = 1 / (cfg.block_int_iters * total_mine_power)

        logger.warning('Setting up connections...')

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

        # -- start sim --
        for i in range(1, simulation_iters):
            [node.step(iter_seconds) for node in nodes]

        Path(f'{results_dir}/{sim_name}').mkdir(parents=True, exist_ok=True)
        for node in nodes:
            # node.log_blockchain()
            with open(f'{results_dir}/{sim_name}/{node.name}', 'wb+') as f:
                pickle.dump(node, f)

        logger.warning(f'Simulation {sim_name} complete. Dumped nodes to  {results_dir}/{sim_name}. Have a good day!')


main()
