import pandas as pd

from tradex.market.api import MarketPair,MarketParser
from tradex.config import MOCK_PORT
import zmq







class MockedMarketPair(MarketPair):

	def __init__(self,pair,string_delimiter=';',port=MOCK_PORT):

		super().__init__(
			pair=pair,port=port,string_delimiter=string_delimiter
			)

		self.pull_port = self._push_port
		self.pull_socket = self.context.socket(zmq.PULL)
		self.pull_socket.connect(f'tcp://localhost:{self.pull_port}')

		self.M1 = pd.DataFrame(
			{'open':[1.4567],'high':[3.4567],'low':[0.9800],'close':[1.4532]}
			,index=pd.to_datetime(['2019-09-08 01:00:00'])
		)

	def logic_contained(self):
		
		MarketParser.main_logic(self)

	def validate_resampling(self):
		pass



