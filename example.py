import random
from bitcoin.models import Miner
from sim.util import Region
from bitcoin.tx_modelings import *
from bitcoin.mining_strategies import *

from zelig import Simulation

""" CONFIGURING WITH CODE """
sim = Simulation()
sim.set_log_level('SUCCESS')
sim.name = 'selfish_mine_test'
sim.results_dir = '/Users/egeerdogan/desktop/projects/zelig/dumps'
sim.sim_reps = 1
sim.sim_iters = 100000
sim.iter_seconds = 0.1
sim.block_int_iters = 6000
sim.max_block_size =  1000000
sim.tx_modeling = SimpleTxModel()
sim.dynamic = False
sim.block_reward = 100

ring = lambda n1, n2: abs(n1.id - n2.id) == 1 or abs(n1.id - n2.id) == 9
star = lambda n1, n2: n1.name == 'center' or n2.name == 'center'
rand = lambda n1, n2: n2.id in [random.randint(0, 9) for _ in range(2)]

sim.connection_predicate = rand

selfish_count, honest_count = 8, 12
selfish_mining = SelfishMining()
honest_mining = HonestMining()

for i in range(selfish_count):
    miner = Miner(f'SFSH_{i}', 10, Region('US'), sim.iter_seconds)
    miner.mine_strategy = selfish_mining
    sim.add_node(miner)

for i in range(honest_count):
    miner = Miner(f'HNST_{i}', 10, Region('US'), sim.iter_seconds)
    miner.mine_strategy = honest_mining
    sim.add_node(miner)

sim.run()
