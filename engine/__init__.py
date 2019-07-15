from threading import Thread
from tradex.engine.connector import DWX_ZeroMQ_Connector
from tradex.market.api import MarketParser
from tradex.market.clear_database import main as clear
from tradex.market.remote import RemoteMarketServer
from tradex.mock_server import publish
from tradex.config import INTERMED_PORT

def main():

    # clear database first
    # clear('EURUSD', True)
    p = MarketParser('EURUSD')

    connector = DWX_ZeroMQ_Connector()
    connector._DWX_MTX_SUBSCRIBE_MARKETDATA_('EURUSD')

    # mark = RemoteMarketServer()

    p1 = Thread(target=p.start)
    p2 = Thread(target=p.main_logic)
    # p3 = Thread(target=publish, args=(INTERMED_PORT,))

    # thread.start()
    p1.start()
    p2.start()
    # p3.start()

    # mark.ws.close()
