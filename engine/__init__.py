import time
from threading import Thread
from multiprocessing import Process
from tradex.engine.connector import DWX_ZeroMQ_Connector
from tradex.market.api import MarketParser
from tradex.market.clear_database import main as clear
from tradex.market.remote import RemoteMarket

def main():
	# clear database first
	clear('EURUSD',True)
	p = MarketParser('EURUSD')

	# connector = DWX_ZeroMQ_Connector()
	# connector._DWX_MTX_SUBSCRIBE_MARKETDATA_('EURUSD')

	mark = RemoteMarket()

	p1 = Thread(target=p.start)
	p2 = Thread(target=p.main_logic)
	thread = Thread(target=mark.ws.run_forever)

	thread.start()
	p1.start()
	p2.start()

	mark.ws.close()
