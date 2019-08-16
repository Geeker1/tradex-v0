from tradex.strategy.indicators import Indicator
import talib
# from tradex.patterns.oneliner import Hammer, InvertedHammer
# from tradex.patterns.doubleliner import Engulfing,\
#     Harami, HaramiCross, PiercingDarkCloud
# from tradex.patterns.multiliner import MorningStar, EveningStar
from backtest.broker import ForexBroker as Broker
import pandas as pd
# import time
# import numpy as np

c = (
    "\033[0m",  # End of color
    "\033[36m",  # Cyan
    "\033[91m",  # Red
    "\033[35m",  # Magenta
)


class Strat2:

    def __init__(self, frame):

        self.rsi = Indicator('rsi', talib.RSI)
        self.ema200 = Indicator('ema200', talib.EMA, timeperiod=200)
        self.ema100 = Indicator('ema100', talib.EMA, timeperiod=100)
        self.ema50 = Indicator('ema50', talib.EMA, timeperiod=50)
        self.ema20 = Indicator('ema20', talib.EMA, timeperiod=20)
        self.stoch = Indicator(
            'stoch', talib.STOCH, lis=['high', 'low', 'close'], no=2)
        self.macd = Indicator('macd',
            talib.MACD, no=3, fastperiod=6, slowperiod=13, signalperiod=4
        )
        self.adx = Indicator(
            'adx', talib.ADX, lis=['high', 'low', 'close'])

        self.new = pd.DataFrame()

        self.broker = Broker()

        self.datagen = self.create_generator(frame.dropna())

    def create_generator(self, frame):
        for index, value in frame.iterrows():
            yield pd.DataFrame(value).transpose()

    def run(self):
        count = 0
        while True:
            try:
                count += 1
                if self.broker.trades > 20:
                    print("Finished trading after 50 moves")
                    break
                n = next(self.datagen)
                print("Current count", count)
                self.new = self.new.append(n)
                self.check()
                self.update_indicators(self.new)
                self.algorithm()
            except StopIteration:
                print("Trade has ended, check wins and losses...")
                return

    def update_indicators(self, val):
        self.ema200.update(val)
        self.ema100.update(val)
        self.ema50.update(val)
        self.ema20.update(val)
        self.rsi.update(val)
        self.stoch.update(val)
        self.macd.update(val)
        self.adx.update(val)

    def verify_stochastic_bullish(self, v):
        try:
            if (
                v.v1[-1] < v.v2[-1] and
                v.v1[-3] >= v.v2[-3]
            ):
                return True
        except Exception:
            pass
        return False

    def verify_stochastic_bearish(self, v):
        try:
            if(
                v.v1[-1] > v.v2[-1] and
                v.v1[-3] <= v.v2[-3]
            ):
                return True
        except Exception:
            pass
        return False

    def verify_rsi_bullish(self, rsi):
        if(
            rsi.v1[-1] > rsi.v1[-2]
        ):
            return True
        return False

    def verify_rsi_bearish(self, rsi):
        if(
            rsi.v1[-1] < rsi.v1[-2]
        ):
            return True
        return False

    def confirm_bear_patterns(self):
        if(
            talib.CDLENGULFING(
                self.new.open, self.new.high, self.new.low, self.new.close
            )[-1] == -100 or
            talib.CDLEVENINGSTAR(
                self.new.open, self.new.high, self.new.low, self.new.close
            )[-1] == 100 or
            talib.CDLEVENINGDOJISTAR(
                self.new.open, self.new.high, self.new.low, self.new.close
            )[-1] == 100 or
            talib.CDLDARKCLOUDCOVER(
                self.new.open, self.new.high, self.new.low, self.new.close
            )[-1] == 100
        ):
            return True
        return False

    def confirm_bull_patterns(self):
        if(
            talib.CDLENGULFING(
                self.new.open, self.new.high, self.new.low, self.new.close
            )[-1] == 100 or
            talib.CDLMORNINGSTAR(
                self.new.open, self.new.high, self.new.low, self.new.close
            )[-1] == 100 or
            talib.CDLMORNINGDOJISTAR(
                self.new.open, self.new.high, self.new.low, self.new.close
            )[-1] == 100 or
            talib.CDLPIERCING(
                self.new.open, self.new.high, self.new.low, self.new.close
            )[-1] == 100
        ):
            return True
        return False

    def confirm_bull_macd(self, mac):
        hist = mac.v3[-3:]
        if(
            (hist[1] < (hist[0] and hist[2])) or
            (hist[0] < hist[1] and hist[2] >= 0) or
            (hist[1] < 0 and hist[2] >= 0)
        ):
            return True
        return False

    def confirm_bear_macd(self, mac):
        hist = mac.v3[-3:]
        if (
            (hist[1] > (hist[0] and hist[2])) or
            (hist[0] > hist[1] and hist[2] <= 0) or
            (hist[1] > 0 and hist[2] <= 0)
        ):
            return True
        return False

    def algorithm(self):
        if self.adx.v1[-1] >= 25:
            if (
                self.verify_stochastic_bearish(self.stoch) and
                self.verify_rsi_bearish(self.rsi) and
                self.confirm_bear_macd(self.macd) and
                self.confirm_bear_patterns()
            ):
                self.broker.create_order(
                    'sell',
                    self.new.iloc[-1].close,
                    self.new.index[-1]
                )

            elif(
                self.verify_stochastic_bullish(self.stoch) and
                self.verify_rsi_bullish(self.rsi) and
                self.confirm_bull_macd(self.macd) and
                self.confirm_bull_patterns()
            ):
                self.broker.create_order(
                    'buy',
                    self.new.iloc[-1].close,
                    self.new.index[-1],
                )
                print(
                    c[1] + "Bullish trade found placing now...." + c[0],
                    "\n"
                )
            else:
                print("No Trade to place....", "\n")
        else:
            print("No Trade to place....", "\n")

    def check(self):
        self.broker.verify_order(
            self.new.iloc[-1].high,
            self.new.iloc[-1].low,
            self.new.index[-1])
