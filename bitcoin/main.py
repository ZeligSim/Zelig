from bitcoin_models import Block, Miner


def connect(m1: Miner, m2: Miner):
    m1.connect(m2)
    m2.connect(m1)


SIMULATION_TIME = 200

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
    node.add_block(genesis_block)

# one iter corresponds to 0.1 sec
for time in range(1, SIMULATION_TIME):
    for node in reversed(nodes):
        node.step()
    if time == 5:
        a_block = miner_a.generate_block()
    # if time == 40:
    #     aa_block = miner_a.generate_block()
    # if time == 80:
    #     c_block = miner_c.generate_block(prev=genesis_block)
    # if time == 120:
    #     a_block = miner_a.generate_block()


for miner in nodes:
    miner.log_blockchain()

