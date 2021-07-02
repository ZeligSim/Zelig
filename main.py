import random
import sys

from omegaconf import DictConfig
import hydra
import pickle
from typing import List
from pathlib import Path
import importlib

from loguru import logger

from bitcoin.models import Block, Miner
from sim.util import Region

from simbadt import Sim

""" CONFIGURING WITH CONFIG FILE """
# sim = Sim('config.yaml')
# sim.run()

""" CONFIGURING WITH CODE """
sim = Sim()
sim.name = 'testing'
sim.results_dir = '/Users/egeerdogan/desktop/Simbadt/dumps'
sim.log_level = 'SUCCESS'
sim.sim_reps = 2
sim.sim_iters = 100000
sim.iter_seconds = 0.1
sim.block_int_iters = 6000

ring = lambda n1, n2: abs(n1.id - n2.id) == 1 or abs(n1.id - n2.id) == 9
star = lambda n1, n2: n1.name == 'center' or n2.name == 'center'

sim.connection_predicate = ring

for i in range(10):
    miner = Miner(str(i), 10, Region('US'), sim.iter_seconds)
    miner.id = i
    sim.add_node(miner)

sim.run()
