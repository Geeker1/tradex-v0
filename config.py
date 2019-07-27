import os

from tradex.reuse import parse_to_integer

PUSH_PORTS = parse_to_integer("PUSH_PORTS")

MARKET_PAIRS = [
    'EURUSD', 'EURJPY', 'EURCHF', 'EURGBP',
    'EURCAD', 'EURAUD', 'EURNZD', 'GBPUSD',
    'GBPAUD', 'GBPJPY', 'USDCHF', 'USDJPY',
    'AUDUSD', 'AUDCAD', 'AUDCHF', 'AUDJPY',
    'AUDNZD', 'CADCHF', 'CHFJPY', 'EURTEST',
    'frxEURUSD', 'frxEURJPY', 'frxEURCHF', 'frxEURGBP',
    'frxEURCAD', 'frxEURAUD', 'frxEURNZD', 'frxGBPUSD',
    'frxGBPAUD', 'frxGBPJPY', 'frxUSDCHF', 'frxUSDJPY',
    'frxAUDUSD', 'frxAUDCAD', 'frxAUDCHF', 'frxAUDJPY',
    'frxAUDNZD', 'frxCADCHF', 'frxCHFJPY',
]

M_SUB_PORT = parse_to_integer("XpubPortNo")

M_PUSH_PORTS = {
    value: PUSH_PORTS + index for index, value in enumerate(MARKET_PAIRS)
}

INFLUXDB_PORT = parse_to_integer("InfluxDbPortNo")

USER = 'devcode'

SERVER_PUSH_PORT = parse_to_integer("MetaPushPort")
SERVER_PULL_PORT = parse_to_integer("MetaPullPort")
SERVER_SUB_PORT = parse_to_integer("MetaSubPort")

MT4_PATH = f'/home/{USER}/.wine/drive_c/Program Files (x86)/Tickmill MT4 Client Terminal/history/Tickmill-DemoUK/'

MOCK_SUB_PORT = parse_to_integer("MockSubPort")
MOCK_ROUTER_PORT = parse_to_integer("MockRouterPort")
INTERMED_ROUTER = parse_to_integer("InterRouterNo")


