import random
from bitcoin.models import Miner
from sim.util import Region
from bitcoin.tx_modelings import *
from bitcoin.mining_strategies import *

from zelig import Simulation

""" CONFIGURING WITH CODE """
sim = Simulation()
sim.set_log_level('INFO')
sim.name = 'selfish_mine_test'
sim.results_dir = '/Users/egeerdogan/desktop/projects/zelig/dumps'
sim.sim_reps = 1
sim.sim_iters = 100000
sim.iter_seconds = 0.1
sim.block_int_iters = 6000
sim.max_block_size = 1000000
sim.tx_modeling = NoneTxModel()
sim.dynamic = False
sim.block_reward = 100

ring = lambda n1, n2: abs(n1.id - n2.id) == 1 or abs(n1.id - n2.id) == 9
star = lambda n1, n2: n1.name == 'center' or n2.name == 'center'
rand = lambda n1, n2: n2.id in [random.randint(0, 32) for _ in range(3)]
mesh = lambda n1, n2: True

sim.connection_predicate = mesh

selfish_mining = SelfishMining()
honest_mining = HonestMining()
null_mining = NullMining()

selfish_power, honest_power = 40,60

selfish_miner = Miner(f'SELFISH', selfish_power, Region('US'), sim.iter_seconds)
selfish_miner.mine_strategy = selfish_mining
selfish_miner.id = 0
sim.add_node(selfish_miner)

honest_miner = Miner(f'HONEST', honest_power, Region('US'), sim.iter_seconds)
honest_miner.mine_strategy = honest_mining
honest_miner.id = 1
sim.add_node(honest_miner)

# for i in range(30):
#     full_node = Miner(f'FULL_{i}', 10, Region('US'), sim.iter_seconds)
#     full_node.mine_strategy = null_mining
#     full_node.id = i + 2
#     sim.add_node(full_node)

sim.run(report_time=True, track_perf=True)
