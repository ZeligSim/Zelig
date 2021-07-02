import random
import sys
import os
from omegaconf import DictConfig
import hydra
import pickle
from typing import List
from pathlib import Path
import importlib
import yaml

from loguru import logger

from bitcoin.models import Block, Miner
from sim.util import Region


class Sim:
    def __init__(self, config_file=None):
        self.name = ""
        self.results_dir = ""
        self.log_level = "SUCCESS"
        self.sim_reps = 1
        self.sim_iters = 1
        self.iter_seconds = 0.1
        self.block_int_iters = 6000
        self.connections_per_node = 2
        self.nodes_in_each_region = -1
        self.__set_log_level(self.log_level)
        self.config_file = config_file

    def run(self):
        if self.config_file is not None:
            self.__load_config_file(detailed=False)

        iter_seconds = self.iter_seconds
        logger.warning('Started simulation.')
        for rep in range(self.sim_reps):
            if self.config_file is not None:
                self.__load_config_file(detailed=True)

            sim_name = f'{self.name}_{rep}'
            for i in range(1, self.sim_iters):
                [node.step(iter_seconds) for node in self.nodes]

            Path(f'{self.results_dir}/{sim_name}').mkdir(parents=True, exist_ok=True)
            for node in self.nodes:
                with open(f'{self.results_dir}/{sim_name}/{node.name}', 'wb+') as f:
                    pickle.dump(node, f)
            logger.warning(f'Simulation {sim_name} complete. Dumped nodes to {self.results_dir}/{sim_name}. Have a good day!')

    def __load_config_file(self, detailed=False):
        with open(self.config_file, 'r') as f:
            config = yaml.safe_load(f)
            self.name = config['sim_name']
            self.results_dir = config['results_directory']
            self.sim_reps = config['sim_reps']
            self.sim_iters = config['sim_iters']
            self.iter_seconds = config['iter_seconds']
            self.block_int_iters = config['block_int_iters']
            self.nodes_in_each_region = config['nodes_in_each_region']
            self.connections_per_node = config['connections_per_node']
            self.__set_log_level(config['log_level'])

            if detailed:
                logger.warning(f'Simulation {self.name} ({self.sim_iters} iterations).')
                logger.warning('Creating nodes...')

                self.nodes = []
                for node in config['nodes']:
                    num_nodes = node['count'] if self.nodes_in_each_region == -1 else self.nodes_in_each_region
                    mine_power = node['region_mine_power'] / num_nodes
                    region = node['region']
                    for idx in range(num_nodes):
                        NodeClass = getattr(importlib.import_module('bitcoin.models'), node['type'])
                        self.nodes.append(NodeClass(f'MINER_{region}_{idx}', mine_power, Region(region), self.iter_seconds))
                genesis_block = Block(Miner('satoshi', 0, None, 1), None, 0)
                total_mine_power = sum([miner.mine_power for miner in self.nodes])
                difficulty = 1 / (self.block_int_iters * total_mine_power)

                logger.warning('Setting up random P2P network...')
                for node in self.nodes:
                    node.set_difficulty(difficulty)
                    node.add_block(genesis_block)
                    node_index = self.nodes.index(node)
                    first_part = self.nodes[:node_index]
                    second_part = self.nodes[node_index + 1:]
                    for i in range(self.connections_per_node):
                        n2 = random.choice(first_part + second_part)
                        node.connect(n2)
                        n2.connect(node)

    @staticmethod
    def __set_log_level(level:str):
        logger.remove()
        logger.add(sys.stdout, level=level)
