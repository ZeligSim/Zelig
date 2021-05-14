from bitcoin_models import Block, Miner


miner_a = Miner(0, 0, 1000)
miner_b = Miner(100, 100, 1000)

miner_a.connect(miner_b)
miner_b.connect(miner_a)

genesis_block = Block('satoshi', 'satoshi', 0, 0, 'satoshi')
miner_a.blockchain.append(genesis_block)
miner_b.blockchain.append(genesis_block)

nodes = [miner_a, miner_b]
time = 0
while True:
    time += 1
    for node in nodes:
        node.step()
    x = input()
    if time % 10 == 0:
        print(miner_a.blockchain)
        print(miner_b.blockchain)
    