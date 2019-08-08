from tradex.strategy.indicators import Indicator
import talib
from tradex.patterns.oneliner import Hammer, InvertedHammer
from tradex.patterns.doubleliner import Engulfing,\
    Harami, HaramiCross, PiercingDarkCloud
from tradex.patterns.multiliner import MorningStar, EveningStar
from backtest.broker import Broker
import pandas as pd
import time
import numpy as np

c = (
    "\033[0m",  # End of color
    "\033[36m",  # Cyan
    "\033[91m",  # Red
    "\033[35m",  # Magenta
)


class Connector:

    def __init__(self, frame):

        self.ema100 = Indicator('ema100', talib.EMA, timeperiod=100)
        self.ema50 = Indicator('ema50', talib.EMA, timeperiod=50)
        self.ema20 = Indicator('ema20', talib.EMA, timeperiod=20)
        self.hammer = Hammer
        self.invertedhammer = InvertedHammer
        self.haram = Harami

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
                n = next(self.datagen)
                print("Current count", count)
                self.new = self.new.append(n)
                self.check()
                time.sleep(0.001)
                self.update_indicators(self.new)
                self.algorithm()
            except StopIteration:
                print("Trade has ended, check wins and losses...")
                return

    def update_indicators(self, val):
        self.ema50.update(val)
        self.ema20.update(val)
        self.ema100.update(val)

    def algorithm(self):
        if self.ema20.v1[-1] > self.ema50.v1[-1] > self.ema100.v1[-1]:
            ham = self.haram(self.new).iterate()[-1]
            if (
                ham == 1 and
                (not self.ema20.v1[-2] >= self.ema50.v1[-2] >=
                    self.ema100.v1[-2])
            ):
                self.broker.increase_trades()
                setattr(self, 'trade', (self.new.iloc[-1].close, 'buy'))
                print(
                    c[1] + "Bullish trade found placing now...." + c[0], "\n")
                time.sleep(5)
                return
            print("No trade to place...", "\n")
        elif self.ema100.v1[-1] > self.ema50.v1[-1] > self.ema20.v1[-1]:
            ham = self.haram(self.new).iterate()[-1]
            if (
                ham == -1 and
                (not self.ema100.v1[-1] <= self.ema50.v1[-2] <=
                    self.ema20.v1[-2])
            ):
                self.broker.increase_trades()
                setattr(self, 'trade', (self.new.iloc[-1].close, 'sell'))
                print(
                    c[2] + "Bearish trade found placing now...." + c[0], "\n")
                time.sleep(5)
                return
            print("No trade to place...", "\n")
        else:
            print("No trade to place...", "\n")

    def check(self):
        try:
            o = getattr(self, 'trade')
        except AttributeError:
            return
        else:
            if o[1] == 'buy':
                if self.new.iloc[-1].close > o[0]:
                    self.broker.increase_amount()
                elif self.new.iloc[-1].close < o[0]:
                    self.broker.reduce_amount()
                else:
                    self.broker.update_stale()

            elif o[1] == 'sell':
                if self.new.iloc[-1].close < o[0]:
                    self.broker.increase_amount()
                elif self.new.iloc[-1].close > o[0]:
                    self.broker.reduce_amount()
                else:
                    self.broker.update_stale()

            delattr(self, 'trade')


class Strat2:

    def __init__(self, frame):

        self.rsi = Indicator('rsi', talib.RSI)
        self.ema50 = Indicator('ema50', talib.EMA, timeperiod=100)
        self.ema20 = Indicator('ema20', talib.EMA, timeperiod=50)
        self.stoch = Indicator(
            'stoch', talib.STOCH, lis=['high', 'low', 'close'], no=2)
        self.macd = Indicator('macd', talib.MACD, no=3)
        self.adx = Indicator(
            'adx', talib.ADX, lis=['high', 'low', 'close'])

        self.new = pd.DataFrame()
        self.hammer = Hammer
        self.engulf = Engulfing
        self.morn = MorningStar
        self.eve = EveningStar
        self.cross = HaramiCross
        self.haram = Harami
        self.cloud = PiercingDarkCloud

        self.broker = Broker()
        self.bull = 0
        self.bear = 0

        self.records = []
        self.t_frames = dict(sell=[], buy=[])
        self.win_frames = dict(sell=[], buy=[])

        self.datagen = self.create_generator(frame.dropna())

    def create_generator(self, frame):
        for index, value in frame.iterrows():
            yield pd.DataFrame(value).transpose()

    def run(self):
        count = 0
        while True:
            try:
                count += 1
                if self.broker.trades > 50:
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
        self.ema50.update(val)
        self.ema20.update(val)
        self.rsi.update(val)
        self.stoch.update(val)
        self.macd.update(val)
        self.adx.update(val)

    def verify_stochastic_bullish(self, v):
        if (
            v.v1[-1] < v.v2[-1] and
            20 <= v.v1[-1] <= 30 and
            (
                not(v.v1[-2] < v.v2[-2]) or
                (v.v1[-2] == v.v2[-2])
            )
        ):
            return True
        return False

    def verify_stochastic_bearish(self, v):
        if(
            v.v1[-1] > v.v2[-1] and
            70 <= v.v1[-1] >= 80 and
            (
                not(v.v1[-2] > v.v2[-2]) or
                (v.v1[-2] == v.v2[-2])
            )
        ):
            return True
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
            np.any(self.engulf(self.new).iterate()[-1:] == -1) or
            np.any(self.eve(self.new).iterate()[-1:] == 1) or
            np.any(self.cloud(self.new).iterate()[-1:] == -1)
            # np.any(self.haram(self.new).iterate()[-1:] == -1) or
            # np.any(self.cross(self.new).iterate()[-1:] == -1)
        ):
            return True
        return False

    def confirm_bull_patterns(self):
        if(
            # np.any(self.hammer(self.new).iterate()[-1:] == 1) or
            np.any(self.engulf(self.new).iterate()[-1:] == 1) or
            np.any(self.morn(self.new).iterate()[-1:] == 1) or
            np.any(self.cloud(self.new).iterate()[-1:] == 1)
            # np.any(self.haram(self.new).iterate()[-1:] == 1) or
            # np.any(self.cross(self.new).iterate()[-1:] == 1)
        ):
            return True
        return False

    def confirm_bull_macd(self, mac):
        if (
            mac.v1[-1] > mac.v2[-1] and
            (
                not(mac.v1[-2] > mac.v2[-2]) or
                mac.v1[-2] == mac.v2[-2]
            )
        ):
            return True
        return False

    def confirm_bear_macd(self, mac):
        if (
            mac.v1[-1] < mac.v2[-1] and
            (
                not(mac.v1[-2] < mac.v2[-2]) or
                mac.v1[-2] == mac.v2[-2]
            )
        ):
            return True
        return False

    def algorithm(self):
        if self.adx.v1[-1] >= 25:
            if (
                # self.ema20.v1[-1] > self.ema50.v1[-1] and
                # not(self.ema20.v1[-2] > self.ema50.v1[-2]) or
                # self.ema50.v1[-2] == self.ema20.v1[-2] and
                # self.verify_stochastic_bullish(self.stoch) and
                self.confirm_bull_patterns()
                # self.confirm_bull_macd(self.macd) and
                # self.verify_rsi_bullish(self.rsi)
            ):
                self.broker.increase_trades()
                self.bull += 1
                setattr(self, 'trade', (self.new.iloc[-1].close, 'buy'))
                print(
                    c[1] + "Bullish trade found placing now...." + c[0],
                    "\n")
            elif (
                # self.ema50.v1[-1] > self.ema20.v1[-1] and
                # not(self.ema50.v1[-2] > self.ema20.v1[-2]) or
                # self.ema50.v1[-2] == self.ema20.v1[-2] and
                # self.verify_stochastic_bearish(self.stoch) and
                self.confirm_bear_patterns()
                # self.confirm_bear_macd(self.macd) and
                # self.verify_rsi_bearish(self.rsi)
            ):
                self.broker.increase_trades()
                self.bear += 1
                setattr(self, 'trade', (self.new.iloc[-1].close, 'sell'))
                print(
                    c[2] + "Bearish trade found placing now...." + c[0], "\n")
            else:
                print("No trade to place...", "\n")
        else:
            print("No trade to place...", "\n")

    def check(self):
        try:
            o = getattr(self, 'trade')
        except AttributeError:
            return
        else:
            if o[1] == 'buy':
                if self.new.iloc[-1].close > o[0]:
                    self.broker.increase_amount()
                    self.records.append(('buy', 'win'))
                    self.win_frames['buy'].append(self.new[-4:])
                elif self.new.iloc[-1].close < o[0]:
                    self.records.append(('buy', 'loss'))
                    self.t_frames['buy'].append(self.new[-4:])
                    self.broker.reduce_amount()
                else:
                    self.broker.update_stale()

            elif o[1] == 'sell':
                if self.new.iloc[-1].close < o[0]:
                    self.broker.increase_amount()
                    self.records.append(('sell', 'win'))
                    self.win_frames['sell'].append(self.new[-4:])
                elif self.new.iloc[-1].close > o[0]:
                    self.broker.reduce_amount()
                    self.records.append(('sell', 'loss'))
                    self.t_frames['sell'].append(self.new[-4:])
                else:
                    self.broker.update_stale()

            delattr(self, 'trade')
















