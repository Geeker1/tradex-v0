import time
import json
import zmq
import pandas as pd
import websocket
from tradex.config import INTERMED_PORT, binary_url
from threading import Thread

data = {
  "ticks": "frxEURUSD",
  "subscribe": 1
}

a = 2


class RemoteMarketServer:

    '''
    A class to serve tick data from remote apis, just link and
    start data is all this class needs, if you want to add extra functionality,
    subclass it in a new class and keep on...
    '''

    def __init__(self, url=binary_url):

        self.ws = websocket.WebSocketApp(
            url=url,
            on_open=self.on_open,
            on_close=self.on_close, on_message=self.on_message,
            on_error=self.on_error
        )

        self.context = zmq.Context()
        self.pub_socket = self.context.socket(zmq.PUB)
        self.pub_socket.bind(f'tcp://*:{INTERMED_PORT}')

    def on_open(self):
        print("[Connected] .... Sending data now")
        json_data = json.dumps(data)
        self.ws.send(json_data)

    def on_message(self, message):

        _json_new = json.loads(message)
        _bid = _json_new['tick']['bid']
        _ask = _json_new['tick']['ask']
        _time = _json_new['tick']['epoch']

        print(f'server time: {_time} ; real time: {time.time()}')
        print(_bid, _ask)
        self.pub_socket.send_string(
            f'EURUSD {_bid};{_ask};{_time}'
        )
        print(f'EURUSD {_bid};{_ask};{_time}')

    def on_close(self):
        self.pub_socket.send_string('kill')
        time.sleep(2)
        self.pub_socket.close()
        self.context.term()

    def on_error(self, exception):
        print(f'Exception error changinh now.... {exception}')
        self.ws.close()

# if __name__ == "__main__":

#     ws = RemoteMarket()

#     thread = Thread(target=ws.run_forever)
#     thread.start()
