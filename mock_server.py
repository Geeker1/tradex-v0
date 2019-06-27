import zmq
from tradex.config import MOCK_PORT
import time

from tradex.market.clear_database import main as mo
from tradex.market.parse_index import parse_hst
from tradex.tests.mocked_classes import MockedMarketPair
from datetime import datetime,timedelta
from threading import Thread

def publish(port=MOCK_PORT):

	context = zmq.Context()
	publish = context.socket(zmq.PUB)
	publish.bind(f'tcp://*:{port}')

	now = datetime.now()
	term = now + timedelta(minutes=1,seconds=10)

	while datetime.now() < term:

		try:
			publish.send_string(f'USDCHF 1.9023;1.9879')
			print('Moving on.....')
			time.sleep(1)
		except KeyboardInterrupt as e:
			publish.close()
			context.term()

	publish.send_string('USDCHF kill')

	publish.close()
	context.term()


def main():

	mo('EURUSD',True)

	x = MockedMarketPair('USDCHF')

	thread1 = Thread(target=publish)
	thread2 = Thread(target=x.start)
	thread3 = Thread(target=x.logic_contained)

	thread1.start()
	thread2.start()
	thread3.start()

	thread1.join()
	print('Thread 1 cut out successfully')

	print('Is publish thread alive ?', thread1.is_alive())
	print('Is start thread alive ?', thread2.is_alive())
	print('Is logic thread alive ?', thread3.is_alive())

	mo('EURUSD',True)

if __name__ == '__main__':
	main()