import os

BASE_PORT = 50091

PUSH_PORTS = 40099

MARKET_PAIRS = [

    'EURUSD',
        'EURJPY',
        'EURCHF',
        'EURGBP',
        'EURCAD',
        'EURAUD',
        'EURNZD',
        'GBPUSD',
        'GBPAUD',
        'GBPJPY',
        'USDCHF',
        'USDJPY',
        'AUDUSD',
        'AUDCAD',
        'AUDCHF',
        'AUDJPY',
        'AUDNZD',
        'CADCHF',
        'CHFJPY',
        'EURTEST',
]

MARKET_PORTS = {
    value: BASE_PORT + index for index, value in enumerate(MARKET_PAIRS)
}

MARKET_PUSH_PORTS = {
    value: PUSH_PORTS + index for index, value in enumerate(MARKET_PAIRS)
}

INFLUXDB_PORT = os.getenv("InfluxDbPortNo")

INTERMED_PORT = os.getenv("XpubPortNo")

USER = 'devcode'

SERVER_PUSH_PORT = os.getenv("MetaPushPort")
SERVER_PULL_PORT = os.getenv("MetaPullPort")
SERVER_SUB_PORT = os.getenv("MetaSubPort")

MT4_PATH = f'''/home/{USER}/.wine/drive_c/Program Files (x86)/
Tickmill MT4 Client Terminal/history/Tickmill-DemoUK/'''

MOCK_PORT = os.getenv("MockPortNo")
