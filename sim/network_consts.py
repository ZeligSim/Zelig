from sim.util import Region

def latency(a: Region, b: Region) -> int:
    latency = LATENCY.get((a, b), None)
    if latency is None:
        return LATENCY[(b, a)]
    return latency


def speed(src: Region, dest: Region) -> int:
    return min(SPEED[src]['up'], SPEED[dest]['down'])


# 2021 - https://testmy.net/country
SPEED = { # Mbps => MB/s
    Region.US: {
        'down': 55.3 * (10**6 / 8),
        'up': 19.2 * (10**6 / 8),
    },
    Region.EU: {
        'down': 65.0 * (10**6 / 8),
        'up': 34.0 * (10**6 / 8),
    },
    Region.SA: {
        'down': 23.4 * (10**6 / 8),
        'up': 6.4 * (10**6 / 8), # ?!
    },
    Region.AP: {
        'down': 32.2 * (10**6 / 8),
        'up': 23.5 * (10**6 / 8),
    },
    Region.JP: {
        'down': 47.8 * (10**6 / 8),
        'up': 54.1 * (10**6 / 8),
    },
    Region.AU: {
        'down': 51.2 * (10**6 / 8),
        'up': 16.8 * (10**6 / 8),
    },
    Region.RU: {
        'down': 23.2 * (10**6 / 8),
        'up': 22.1 * (10**6 / 8),
    },
}

# 2021 - https://wondernetwork.com/pings
LATENCY = {  # seconds
    (Region.US, Region.US): 0 * 0.001,
    (Region.US, Region.EU): 73 * 0.001,
    (Region.US, Region.SA): 164 * 0.001,
    (Region.US, Region.AP): 227 * 0.001,
    (Region.US, Region.JP): 176 * 0.001,
    (Region.US, Region.AU): 152 * 0.001,
    (Region.US, Region.RU): 118 * 0.001,

    (Region.EU, Region.EU): 0 * 0.001,
    (Region.EU, Region.SA): 244 * 0.001,
    (Region.EU, Region.AP): 226 * 0.001,
    (Region.EU, Region.JP): 235 * 0.001,
    (Region.EU, Region.AU): 258 * 0.001,
    (Region.EU, Region.RU): 47 * 0.001,

    (Region.SA, Region.SA): 0 * 0.001,
    (Region.SA, Region.AP): 442 * 0.001,
    (Region.SA, Region.JP): 315 * 0.001,
    (Region.SA, Region.AU): 327 * 0.001,
    (Region.SA, Region.RU): 284 * 0.001,

    (Region.AP, Region.AP): 0 * 0.001,
    (Region.AP, Region.JP): 143 * 0.001,
    (Region.AP, Region.AU): 377 * 0.001,
    (Region.AP, Region.RU): 119 * 0.001,

    (Region.JP, Region.JP): 0 * 0.001,
    (Region.JP, Region.AU): 160 * 0.001,
    (Region.JP, Region.RU): 288 * 0.001,

    (Region.AU, Region.AU): 0 * 0.001,
    (Region.AU, Region.RU): 324 * 0.001,

    (Region.RU, Region.RU): 0 * 0.001,
}
