
################# REGULAR PYTHON IMPORTS ##################

import json
import os
import random
import pickle


################# LIBRARY IMPORTS ##################

import zmq
import pandas as pd
import influxdb as db

################# Object IMPORTS ##################

from tradex.market.parse_index import parse_hst
from influxdb.exceptions import InfluxDBClientError
from threading import Thread
from datetime import datetime


from tradex.config import MT4_PATH,MARKET_PUSH_PORTS,INTERMED_PORT


# def proxy(port):
# 	context = zmq.Context()
# 	frontend = context.socket(zmq.SUB)
# 	frontend.connect(f'tcp://localhost:{port}')
# 	frontend.setsockopt_string(zmq.SUBSCRIBE,'')

# 	backend = context.socket(zmq.PUB)
# 	backend.bind(f'tcp://*:{port+1}')

# 	while True:

# 		try:
# 			msg = frontend.recv_string(zmq.DONTWAIT)
# 			if msg != '':
# 				backend.send_string(msg)

# 		except zmq.error.Again:
# 			pass

# 		except Exception as e:
# 			backend.close()
# 			frontend.close()
# 			context.term()
		


# def publish(port):

# 	context = zmq.Context()
# 	publish = context.socket(zmq.PUB)
# 	publish.bind(f'tcp://*:{port}')

# 	while True:
		
# 		try:
# 			print('Sending message ....')
# 			rand = random.choice(['ledum','hello','hi','where'])
# 			publish.send_string(f'hello;keania')
# 			time.sleep(1)
# 		except KeyboardInterrupt as e:
# 			publish.close()
# 			context.term()

cdef class MarketPair:

	##############  NOTE: DO NOT INHERIT FROM BASE CLASS DIRECTLY.... ########

	cdef:
		readonly int _push_port,_port
		readonly str _pair,string_delimiter
		object context,push
		public object df_tick

	def __init__(self,pair,string_delimiter=';'):

		"""
		This is class is base class of Market Pairs

		[INIT VALUES]

		1. pair :== This is the name of market pair and it
		 is passed as string to init function

		2. port :== This is the port that market pair runs on and 
		should be unique to the specific market pair 
		so as not to have more than one pair running in the system...


		"""

		self._push_port = MARKET_PUSH_PORTS[pair]
		self.string_delimiter = string_delimiter

		self.context = zmq.Context()
		self.push = self.context.socket(zmq.PUSH)
		self.push.bind(f'tcp://*:{self._push_port}')
		
		self._port = INTERMED_PORT
		self._pair = pair
		
		self.df_tick = pd.DataFrame(
			{},index=pd.to_datetime([]),columns=['Bid','Ask']
		)

	"""
	
	#####################################################################

			The start function defined by start();
			It connects MARKETCLIENT with the METATRADER 4 connnector;
			It parses data received and sends it on a push socket to ==
			thread based function that analyses data received and 
			sends to strategy manager for signal...

	#####################################################################

	
	"""

	cpdef start(self):
		cdef:
			object context,subscribe,_tx,last_last_val,last_val
			str msg,_symbol,_data,_bid,_ask,_timestamp,range_1,range_2
			bytes dump_data

		context = zmq.Context()
		subscribe = context.socket(zmq.SUB)
		subscribe.connect(f'tcp://localhost:{self._port}')

		subscribe.setsockopt_string(zmq.SUBSCRIBE,self._pair)

		
		while True:
			try:
				msg = subscribe.recv_string(zmq.DONTWAIT)
				if msg != '':
					_symbol, _data = msg.split(" ")
					_bid, _ask = _data.split(self.string_delimiter)
					_tx = pd.Timestamp.now('UTC')
					_timestamp = str(_tx)[:-6]

					self.df_tick.append(
						pd.DataFrame({
							'Bid':[float(_bid)],'Ask':[float(_ask)]
							},
							index=pd.to_datetime([_timestamp])
						))

					print('Received message .... ',msg)

					last_last_val = self.df_tick.index[-2]
					last_val = self.df_tick.index[-1]

					if last_val.minute - self.last_last_val.minute == 1:
						range_1 = str(
							last_last_val.replace(
							second=0,microsecond=0))

						range_2 = str(last_last_val)

						dump_data = pickle.dumps(
							self.df.loc[range_1:range_2]['Bid'].resample('1Min').ohlc()
							)

						self.push.send(dump_data)

			except zmq.error.Again:
				pass
			except ValueError:
				pass
			except KeyboardInterrupt as e:
				subscribe.close()
				context.term()

	



cdef class MarketParser(MarketPair):

	""" This class inherits from Market pair and adds extra functionality


	It initially queries INFLUXDB database for all data in minute candle,

	then adds this initially to 1min dataframe, before comparing today's time

	with influxdb time, getting loophole and querying out loophole values

	 from hst archive, then creating another dataframe minute candle 

	 and appending to initial minute candlestick before the main process 
	 starts...

	 Note that if InfluxDB database is empty, or not created, then it 
	 is automatically created and filled with a large dataset of hst archive values for 1min candle 
	 so we dont ave to query hst archive again when we want 
	 to get old tick values but loop holes instead to fill in the gaps

	This class implements the process of resampling data
	 to different timeframes and appending each data value
	  to timeframe variables

	Note initial dataframes have None as value, this changes over time..

	"""

	cdef:
		str pair,pair_n
		readonly int pull_port
		readonly object client,pull_socket
		public M1,M5,M15,H1,H4,D1

	def __init__(self,pair):

		""" ####### Defining Initial timeframe DataFrames ########## """

		self.M1 = None
		self.M5 = None
		self.M15 = None
		self.H1 = None
		self.H4 = None
		self.D1 = None

		self.pair = pair

		self.pair_n = self.pair + '60.hst'

		""" [ Initialize connection and Query Database for values ] """

		# Open client

		""" Note: Main Influx DB service must be started before this class is 
		run to avoid error """

		self.client = db.DataFrameClient(host='localhost',port=8086,database=pair)

		"""  Query DataBase for values, if No Database"""

		print('Gotten here')

		self.M1 = self.initials()

		print('\nGotten Minute values')

		super().__init__(pair=pair)

		print('Passed super stage')

		self.pull_port = self._push_port

		self.pull_socket = self.context.socket(zmq.PULL)

		self.pull_socket.connect(f'tcp://localhost:{self.pull_port}')

		print('\nDone, exiting [INIT] block')

	"""
	
	#####################################################################

			Fetches data from hst archive

	#####################################################################

	
	"""

	
	cdef object fetch_parse(self,year_val=None,range_1=None,range_2=None):
		_path = os.path.join(MT4_PATH,self.pair_n)
		if os.path.exists(_path):
			return parse_hst(_path,year_val,range1=range_1,range2=range_2)

		raise FileNotFoundError(
			'''The file was not found on this device, try changing paths...'''
		)

	"""
	
	#####################################################################

			The initials function defined by initials();
			It is the first function run in this class and it's work is 
			to fill up the M1(1 minute dataframe) with recent data 
			from either database or hst archive...

	#####################################################################

	
	"""

	cdef initials(self):

		cdef:
			object _M1,_now,_loop_frame
			double _range_1,_range_2

		try:
			_M1 = self.client.query(
				f'select * from {self.pair}'
				)[f'{self.pair}']
			
			_now = pd.Timestamp.now('UTC')

			_range_1 = self.M1.index[-1].timestamp()
			_range_2 = (
				_now.replace(second=0,microsecond=0) - pd.Timedelta(minutes=1)
				).timestamp()

			_loop_frame = self.fetch_parse(_range_1,_range_2)

			_M1 = self.M1.append(_loop_frame)

			return _M1

		except InfluxDBClientError as e:
			print('Database error, >>>>> Creating new database \n')
			print('Fetching Data from HST Archive as replcacement')
			# raise e('Database was not found fot this market pair')

			_M1 = self.fetch_parse(year_val=2018)
			print('Gotten values')
			self.client.create_database(f'{self.pair}')
			self.client.write_points(_M1,f'{self.pair}',protocol='json')

			print('Done and dusted')
			return _M1

	def validate_resampling(self):
		pass

	"""
	
	#####################################################################

			This is the main logic and would be responsible 

	#####################################################################

	
	"""

	def main_logic(self):
		while True:
			try:
				msg = self.pull_socket.recv()
				if msg != '':
					frame = pickle.loads(msg)
					self.M1 = self.M1.append(frame)
					self.validate_resampling()
			except zmq.error.Again:
				pass
			except ValueError:
				pass
			except KeyboardInterrupt as e:
				self.pull_socket.close()
				self.context.term()


cpdef main():
	MarketParser('EURUSD')


