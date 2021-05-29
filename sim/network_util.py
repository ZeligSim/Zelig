from sim.util import Region


def get_delay(a: Region, b: Region, size: int) -> int:
    lat = latency(a, b)
    trans = (size / speed(a, b))
    return lat + trans


def latency(a: Region, b: Region) -> int:
    latency = LATENCY.get((a, b), None)
    if latency is None:
        return LATENCY[(b, a)]
    return latency


def speed(src: Region, dest: Region) -> int:
    return min(SPEED[src]['up'], SPEED[dest]['down'])


# 2021 - https://testmy.net/country
SPEED = {  # Mbps => MB/s
    Region.CH: {
        'down': 31.6 * (10 ** 6 / 8),
        'up': 23.6 * (10 ** 6 / 8),
    },
    Region.US: {
        'down': 55.3 * (10 ** 6 / 8),
        'up': 19.2 * (10 ** 6 / 8),
    },
    Region.RU: {
        'down': 23.1 * (10 ** 6 / 8),
        'up': 20.2 * (10 ** 6 / 8),
    },
    Region.KZ: {
        'down': 12.9 * (10 ** 6 / 8),
        'up': 8.0 * (10 ** 6 / 8),
    },
    Region.ML: {
        'down': 25.1 * (10 ** 6 / 8),
        'up': 19.4 * (10 ** 6 / 8),
    },
    Region.CN: {
        'down': 59.0 * (10 ** 6 / 8),
        'up': 14.6 * (10 ** 6 / 8),
    },
    Region.GE: {
        'down': 63.4 * (10 ** 6 / 8),
        'up': 24.5 * (10 ** 6 / 8),
    },
    Region.NR: {
        'down': 37.5 * (10 ** 6 / 8),
        'up': 17.6 * (10 ** 6 / 8),
    },
    Region.VN: {
        'down': 7.7 * (10 ** 6 / 8),
        'up': 3.5 * (10 ** 6 / 8),
    },
}

# 2021 - https://wondernetwork.com/pings
LATENCY = {  # seconds
    (Region.US, Region.US): 0 * 0.001,
    (Region.US, Region.CH): 235 * 0.001,
    (Region.US, Region.RU): 118 * 0.001,
    (Region.US, Region.KZ): 182 * 0.001,
    (Region.US, Region.ML): 364 * 0.001,
    (Region.US, Region.CN): 63 * 0.001,
    (Region.US, Region.GE): 92 * 0.001,
    (Region.US, Region.NR): 97 * 0.001,
    (Region.US, Region.VN): 59 * 0.001,

    (Region.CH, Region.CH): 0 * 0.001,
    (Region.CH, Region.RU): 119 * 0.001,
    (Region.CH, Region.KZ): 305 * 0.001,
    (Region.CH, Region.ML): 174 * 0.001,
    (Region.CH, Region.CN): 161 * 0.001,
    (Region.CH, Region.GE): 227 * 0.001,
    (Region.CH, Region.NR): 241 * 0.001,
    (Region.CH, Region.VN): 161 * 0.001,

    (Region.RU, Region.RU): 0 * 0.001,
    (Region.RU, Region.KZ): 70 * 0.001,
    (Region.RU, Region.ML): 326 * 0.001,
    (Region.RU, Region.CN): 191 * 0.001,
    (Region.RU, Region.GE): 43 * 0.001,
    (Region.RU, Region.NR): 48 * 0.001,
    (Region.RU, Region.VN): 173 * 0.001,

    (Region.KZ, Region.KZ): 0 * 0.001,
    (Region.KZ, Region.ML): 406 * 0.001,
    (Region.KZ, Region.CN): 241 * 0.001,
    (Region.KZ, Region.GE): 106 * 0.001,
    (Region.KZ, Region.NR): 84 * 0.001,
    (Region.KZ, Region.VN): 219 * 0.001,

    (Region.ML, Region.ML): 0 * 0.001,
    (Region.ML, Region.CN): 220 * 0.001,
    (Region.ML, Region.GE): 242 * 0.001,
    (Region.ML, Region.NR): 223 * 0.001,
    (Region.ML, Region.VN): 651 * 0.001,

    (Region.CN, Region.CN): 0 * 0.001,
    (Region.CN, Region.GE): 154 * 0.001,
    (Region.CN, Region.NR): 179 * 0.001,
    (Region.CN, Region.VN): 109 * 0.001,

    (Region.GE, Region.GE): 0 * 0.001,
    (Region.GE, Region.NR): 35 * 0.001,
    (Region.GE, Region.VN): 144 * 0.001,

    (Region.NR, Region.NR): 0 * 0.001,
    (Region.NR, Region.VN): 165 * 0.001,

    (Region.VN, Region.VN): 0 * 0.001,
}
