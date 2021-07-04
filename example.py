import random
from bitcoin.models import Miner
from sim.util import Region

from simbadt import Simulation

""" CONFIGURING WITH CODE """
sim = Simulation()
sim.set_log_level('SUCCESS')
sim.name = 'testing'
sim.results_dir = '/Users/egeerdogan/desktop/Simbadt/dumps'
sim.sim_reps = 2
sim.sim_iters = 100000
sim.iter_seconds = 0.1
sim.block_int_iters = 6000

ring = lambda n1, n2: abs(n1.id - n2.id) == 1 or abs(n1.id - n2.id) == 9
star = lambda n1, n2: n1.name == 'center' or n2.name == 'center'
rand = lambda n1, n2: n2.id in [random.randint(0, 9) for _ in range(1)]

sim.connection_predicate = ring

for i in range(10):
    miner = Miner(f'MINER_{i}', 10, Region('US'), sim.iter_seconds)
    miner.id = i
    sim.add_node(miner)

sim.run()
