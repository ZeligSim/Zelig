from bitcoin_models import Block, Miner


def connect(m1: Miner, m2: Miner):
    m1.connect(m2)
    m2.connect(m1)


SIMULATION_TIME = 40

miner_a = Miner('MINER_A', 0, 0, 1000)
miner_b = Miner('MINER_B', 100, 100, 1000)
miner_c = Miner('MINER_C', 200, 200, 1000)
miner_d = Miner('MINER_D', 300, 300, 1000)

connect(miner_a, miner_b)
connect(miner_b, miner_c)
connect(miner_c, miner_d)

nodes = [miner_a, miner_b, miner_c, miner_d]

genesis_block = Block('satoshi', 'satoshi', 0, 0, 'satoshi')

for node in nodes:
    node.blockchain.append(genesis_block)

for time in range(1, SIMULATION_TIME):
    for node in nodes:
        node.step()
    if time == 5:
        miner_a.generate_block()

