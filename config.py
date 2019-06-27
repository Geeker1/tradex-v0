
BASE_PORT = 50091

PUSH_PORTS = 40091

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
	value: BASE_PORT + index for index,value in enumerate(MARKET_PAIRS)
}

MARKET_PUSH_PORTS = {
	value: PUSH_PORTS + index for index,value in enumerate(MARKET_PAIRS)
}

INFLUXDB_PORT = 8086

INTERMED_PORT = 9023

USER = 'devcode'

SERVER_PUSH_PORT = 32768
SERVER_PULL_PORT = 32769
SERVER_SUB_PORT = 32770

MT4_PATH = f'/home/{USER}/.wine/drive_c/Program Files (x86)/Tickmill MT4 Client Terminal/history/Tickmill-DemoUK/'

MOCK_PORT = 67091