import influxdb as db
import talib
import zmq
from tradex.strategy.indicators import Indicator
# import time


class Strategy1:

    """This class implements the basic strategy
    of SMA and MACD oscillators"""

    timeframes = ['M1', 'M5', 'M15', 'H1', 'H4']

    def __init__(self, other, timeframe=None):

        self.market = other.database_name if other else 'EURUSD'

        self.max_period = 100

        # self.monitor = self.timeframes[1]
        self.monitor = 'EURUSD'

        self.client = db.DataFrameClient(
            database=self.market)

        self.init = self.client.query(
            f"SELECT open,high,low,close from {self.market} \
            LIMIT {self.max_period}"
        ).get(self.monitor).dropna()

        self.ema = Indicator('ema', talib.EMA, timeperiod=20)
        self.ema.update(self.init)

        self.ema3 = Indicator('ema3', talib.EMA, timeperiod=50)
        self.ema3.update(self.init)

        self.ema4 = Indicator('ema4', talib.EMA, timeperiod=100)
        self.ema4.update(self.init)

    def loop_fill(self, frame):
        for ind in [self.ema, self.ema3, self.ema4]:
            ind.update(frame)

    def loop_subscribe(self):
        self.ctx = zmq.Context()
        self.sub = self.ctx.socket(zmq.SUB)
        self.sub.connect("tcp://localhost:45600")
        self.sub.subscribe(self.market)

        while True:
            try:
                m = self.sub.recv()
                if m != b'':
                    if m == b'EURUSD kill':
                        self.kill_sockets()
                        break
                    if m == b'EURUSD':
                        self.init = self.client.query(
                            f"select open,high,low,close from\
                             {self.market} LIMIT \
                            {self.max_period}").get(
                            self.monitor).dropna()

                        self.loop_fill(self.init)
                        self.algo(self.init)
            except zmq.error.Again:
                pass
            except KeyboardInterrupt:
                self.kill_sockets()
                break
            except Exception:
                self.kill_sockets()
                raise Exception

    def kill_sockets(self):
        self.sub.close()
        self.ctx.term()

    def algo(self, frame):
        # arr = frame
        if self.ema.v1[-1] > self.ema3.v1[-1] > self.ema4.v1[-1]:
            print("yay...place trade now....")
        else:
            print("No trade mehn....")
