# Zelig

<p align="center">
      <img src="assets/zelig_profile.png" width="220">      
</p>

**Zelig** is a (WIP) blockchain simulator designed with the main goals of customizability and extensibility to streamline research on blockchain-based systems, and provide a useful tool for blockchain education. 

~~**Reference Documentation** : [https://zeligsim.github.io](https://zeligsim.github.io)~~ (updated soon)

[What is behind the name?](https://www.imdb.com/title/tt0086637/)

## Installation

To install zelig, clone this repository with the following command:
```
https://github.com/ZeligSim/Zelig.git
```
and install the required Python libraries:
```
pip install -r requirements.txt
```

# Design

Zelig consists of a core simulator module (`/sim`) that handles the functionality found in all blockchains, such as the network layer and the basic node properties (storing the blockchain, maintaining connections, etc.).

The core simulator can be extended to implement specific blockchains. The repository contains a Bitcoin simulator (`/bitcoin`) extending the core simulator.

# Running Simulations

A simulation in Zelig is run for a specified number of steps, and the nodes are then serialized into a specified directory. The nodes can then be deserialized and analyzed. The `analysis.py` module under the `bitcoin` directory contains some helpful starter analysis methods.

There are two ways of setting up Bitcoin simulations in Zelig: 

* **With YAML config files:** Modifying the config files allows for rapid experimentation when the customizations consist of changing certain parameters.
* **Programatically:** Programmatic setup enables more powerful customization, such as custom network topologies, consensus algorithms, and mining strategies.

## Setup with Config Files

The fastest way of running simulations is through a YAML config file. Once a config file is setup, simulations can be started with the command:
```
python zelig.py -c <config-filename> -s <random-seed>
```

As the example in the repository demonstrates, the following parameters can be set in a config file:
* `sim_name`: Name of the experiment. Directory containing the nodes at the end will have this name.
* `results_directory`: Target directory the nodes will be saved.
* `log_level`: See `config.yaml` for available logging levels.
* `sim_reps`: How many times to repeat the same simulation. This might be useful for obtaining more representative results from experiments.
* `iter_seconds`: How many real-world seconds one simulation step corresponds to  (setting `0.1` means one simulation step will *simulate* 0.1 seconds; it will not *take*  0.1 seconds).
* `block_int_iters`: Expected block interval in iters (e.g. if `iter_seconds` is 0.1 and the block interval is 10 minutes, this value should be set to 6,000).
* `block_reward`: Reward given to miners.
* `dynamic_difficulty`: (`True` or `False`) Mining difficulty dynamically changes if  set to `True`.
* `max_block_size`: Maximum block size in bytes.
* `tx_modeling`: Transaction modeling detail.
* `tx_per_node_per_iter`: Number of transactions each node will publish in each step.
* `connections_per_node`: Number of *outgoing* connections per node.
* `nodes_in_each_region`: Number of nodes in each of the geographic regions. Set to `-1` to use real-world values (see `config.yaml`).
* `nodes`: (see `config.yaml`)


## Programmatic Setup 

Programmatic setup revolves around the `Simulation` class defined in `zelig.py`. The `example.py` file in the home directory provides an example. After creating such a file, it is enough to simply execute it:
```
python example.py
```

The first step is to instantiate a `Simulation` object. Afterwards, various customization opportunities are possible.

**Setting up parameters:** Similar to the config file approach, certain parameters  can be configured as fields of the `Simulation` object. Refer to the `example.py` file or the `Simulation` class definition for a comprehensive list.

**Adding nodes:** Nodes can be added to the simulation through the `add_node(node: Node)` method of the `Simulation` class. Each Bitcoin miner has a `mining_strategy` field that stores an instance of the class correspdonding to the node's mining strategy (see the section below on custom mining strategies for more detail).

**Custom Network Topologies:** The `connection_predicate` field of the `Simulation` class stores a Python method with the signature `(n1: Node, n2: Node) -> bool` that returns `True`  if the nodes are connected and `False` otherwise. You can see some examples in the form of `lambda` expressions in the `example.py` file for ring, star, mesh, and random topologies.

**Starting simulations:** To run the simulations, call the `run` method of the `Simulation` object. It takes two optional parameters: `track_perf` and `report_time`. If set to `True`, `track_perf` displays the CPU and memory use stats at the end, and `report_time` displays the time it took for the simulation (and each step) to run.

# Customizing Simulations

There are two main areas of customization in Zelig: consensus protocols and mining strategies.

❗️ Note that for performance, although not strictly enforced, the classes we describe now are implemented to have a single instance. That is why the methods take the caller node as their first arguments.

## Custom Consensus Protocols

You can implement a consensus protocol by extending the `Oracle` defined in `bitcoin/consensus.py`. The file already contains a basic proof-of-work implementation that dynamically adjusts difficulty (`PoWOracle`). 

We model a consensus protocol as consisting of three steps: election of leader(s), updating state, and distributing rewards. The second step is independent of the specific consensus protocol, and the `Oracle` class contains a method for the first and the last steps.

The main interface contains two methods:
* `can_mine(miner) -> bool`: Returns `True` if the specified miner is allowed to mine in that step. In PoW, this corresponds to checking if a random number is below a specific value that denotes the probability of that miner generating a block. 
* `get_reward(miner) -> Reward`: Miners call this method after they generate a block to collect their rewards; they then include their rewards in the generated block. In PoW, this method returns a `Reward` object with a fixed, pre-specified value. More complex protocols can also be implemented.

## Custom Mining Strategies

Custom mining strategies can be implemented by extending the `NullMining` class defined in `bitcoin/mining_strategies.py`. 

Similar to the consensus protocols, we model a mining strategy as consisting of four components: an initial setup, a protocol for generating a new block, choosing which block to mine on, and receiving a block from another node.

The provided `mining_strategies.py` file contains examples of a full node (no mining), honest miner, and a selfish miner (implements the selfish mining attack).

These four methods implement the four components:
* `setup(node)`: Performs initial setup if necessary.
* `choose_head(node)`: Choose block to mine on. In basic PoW, this is the head of the chain with the highest work.
* `generate_block(node, prev) -> `: Create a new block; fill it with transactions.
* `receive_block(node, block)`: Specifies the action to be taken when the miner receives a new block.

# Analysis

At the end of an experiment, all the nodes are dumped to the specified results directory using the Pickle module. Some fields are removed to prevent infinite loops caused by circular references.

Additionally, a `Bookkeeper` that collects some statistics, such as block receipt times, is also serialized.

The `Analysis` class defined in `bitcoin/analysis.py` provides some useful methods, although the analysis capabilities are not limited to them. The Jupyter notebook `analysis_notebook.ipynb` likewise displays an example use of those methods.

# Contributing

TODO

# Cite Zelig in Your Work

```
@misc{erdogan2021demo,
      title={Demo -- Zelig: Customizable Blockchain Simulator}, 
      author={Ege Erdogan and Can Arda Aydin and Oznur Ozkasap and Waris Gill},
      year={2021},
      eprint={2107.07972},
      archivePrefix={arXiv},
      primaryClass={cs.CR}
}
```
