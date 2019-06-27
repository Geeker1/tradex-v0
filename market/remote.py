import time
import json
import zmq
import pandas as pd
import websocket
from tradex.config import INTERMED_PORT
from threading import Thread

data = {
  "ticks": "frxEURUSD",
  "subscribe": 1
}
apiUrl = "wss://ws.binaryws.com/websockets/v3?app_id=16157"

class RemoteMarket:

	def __init__(self):

		self.ws = websocket.WebSocketApp(url=apiUrl,on_open=self.on_open
			,on_close=self.on_close,
			on_message=self.on_message,
			on_error=self.on_error)
		
		self.context = zmq.Context()
		self.pub_socket = self.context.socket(zmq.PUB)
		self.pub_socket.bind(f'tcp://*:{INTERMED_PORT}')

	def on_open(self):
		print("[Connected] .... Sending data now")
		json_data = json.dumps(data)
		self.ws.send(json_data)

	def on_message(self,message):
		json_new = json.loads(message)
		print(json_new)
		_bid = json_new['bid']
		_ask = json_new['ask']
		self.pub_socket.send_string(
			f'EURUSD {_bid};{_ask}'
			)

	def on_close(self):
		self.pub_socket.send_string('kill')
		time.sleep(2)
		self.pub_socket.close()
		self.context.term()

	def on_error(self,exception):
		print(f'Exception error changinh now.... {exception}')
		self.ws.close()

# if __name__ == "__main__":
    
#     ws = RemoteMarket()

#     thread = Thread(target=ws.run_forever)
#     thread.start()