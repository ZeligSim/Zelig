from models import Region


def latency(a: Region, b: Region) -> int:
    latency = LATENCY.get((a, b), None)
    if latency is None:
        return LATENCY[(b, a)]
    return latency


def speed(src: Region, dest: Region) -> int:
    return min(SPEED[src]['up'], SPEED[dest]['down'])


# 2021 - https://testmy.net/country
SPEED = {
    Region.US: {
        'down': 55.3,
        'up': 19.2,
    },
    Region.EU: {
        'down': 65.0,
        'up': 34.0,
    },
    Region.SA: {
        'down': 23.4,
        'up': 6.4,
    },
    Region.AP: {
        'down': 32.2,
        'up': 23.5,
    },
    Region.JP: {
        'down': 47.8,
        'up': 54.1,
    },
    Region.AU: {
        'down': 51.2,
        'up': 16.8,
    },
    Region.RU: {
        'down': 23.2,
        'up': 22.1,
    },
}

# 2021 - https://wondernetwork.com/pings
LATENCY = {  # milliseconds
    (Region.US, Region.US): 0,
    (Region.US, Region.EU): 73,
    (Region.US, Region.SA): 164,
    (Region.US, Region.AP): 227,
    (Region.US, Region.JP): 176,
    (Region.US, Region.AU): 152,
    (Region.US, Region.RU): 118,

    (Region.EU, Region.EU): 0,
    (Region.EU, Region.SA): 244,
    (Region.EU, Region.AP): 226,
    (Region.EU, Region.JP): 235,
    (Region.EU, Region.AU): 258,
    (Region.EU, Region.RU): 47,

    (Region.SA, Region.SA): 0,
    (Region.SA, Region.AP): 442,
    (Region.SA, Region.JP): 315,
    (Region.SA, Region.AU): 327,
    (Region.SA, Region.RU): 284,

    (Region.AP, Region.AP): 0,
    (Region.AP, Region.JP): 143,
    (Region.AP, Region.AU): 377,
    (Region.AP, Region.RU): 119,

    (Region.JP, Region.JP): 0,
    (Region.JP, Region.AU): 160,
    (Region.JP, Region.RU): 288,

    (Region.AU, Region.AU): 0,
    (Region.AU, Region.RU): 324,

    (Region.RU, Region.RU): 0,
}
