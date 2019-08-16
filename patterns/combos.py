import talib
import numpy as np


class Base:
    def __init__(self, array, indicator_array=None, indicator_list=None):

        self.array = array
        self.iarray = indicator_array
        self.ilist = indicator_list
        self.o, self.h, self.l, self.c = self.get_ohlc(array)

    def check_status(self, open_x, close):
        if open_x > close:
            return "Bearish"
        elif open_x < close:
            return "Bullish"
        elif open_x == close:
            return "Indecisive"

    def get_ohlc(self, array):
        return [array[:, x] for x in range(4)]

    def get_size(self, open, close):
        return abs(open - close)

    def bear_marubozu_gravestone(self, *args):
        def logic(r):
            if (
                np.all(self.array[loc[-1]] == self.array[-2])
                and np.all(self.array[loc2[-1]] == self.array[-1])
                # (self.array[-2][3] < r[0] and self.array[-2][0] > r[0]) and
                # (self.array[-1][3] < r[1] and self.array[-2][1] > r[0])
            ):
                return 1
            return 0

        mar = talib.CDLMARUBOZU(self.o, self.h, self.l, self.c)
        grave = talib.CDLGRAVESTONEDOJI(self.o, self.h, self.l, self.c)

        try:
            loc, loc2 = np.where(mar == -100)[0], np.where(grave == 100)[0]
            if (loc.size or loc2.size) == 0 or (len(self.array) < 2):
                return 0
        except Exception:
            return 0

        finally:
            if self.ilist is None:
                r = self.iarray[-2:]
                return logic(r)

            for i in self.ilist:
                r = i[-2:]
                return logic(r)

    def bear_engulfing_touch(self, *args):
        def logic(idx):
            if (
                np.all(self.array[idx[-1]] == self.array[-1])
                and self.h[-1] != self.o[-1]
                and self.h[-2] != self.o[-2]
            ):
                return 1
            return 0

        engulf = talib.CDLENGULFING(self.o, self.h, self.l, self.c)

        try:
            idx = np.where(engulf == -100)[0]
            if idx.size == 0 or len(self.array) < 2:
                return 0
        except Exception:
            return 0
        finally:
            if self.ilist is None:
                return logic(idx)

    def bear_hammer_inverse(self, *args):
        def logic(x):
            nonlocal o
            if (
                x - 1 in idx
                and x - 2 in idx
                and self.check_status(self.array[x][0], self.array[x][-1]) == "Bearish"
                and self.check_status(self.array[x - 1][0], self.array[x - 1][-1])
                == "Bearish"
                and self.check_status(self.array[x - 2][0], self.array[x - 2][-1])
                == "Bearish"
            ):
                o.append(x)

        ham = talib.CDLHAMMER(self.o, self.h, self.l, self.c)
        t = talib.CDLINVERTEDHAMMER(self.o, self.h, self.l, self.c)
        idx = np.where(ham == 100)[0]
        idx1 = np.where(t == 100)[0]

        o = []
        for x in idx1:
            try:
                logic(x)
            except Exception:
                continue

        a = np.zeros(len(self.o))
        a[o] = 1
        return a

    def bear_marubozu_dragonfly_gravestone(self, *args):
        def logic(x):
            nonlocal o
            if (
                x - 1 in idx
                and x - 2 in idx
                and self.check_status(self.array[x][0], self.array[x][-1]) == "Bearish"
                and self.check_status(self.array[x - 1][0], self.array[x - 1][-1])
                == "Bearish"
                and self.check_status(self.array[x - 2][0], self.array[x - 2][-1])
                == "Bearish"
            ):
                o.append(x)

        ham = talib.CDLHAMMER(self.o, self.h, self.l, self.c)
        t = talib.CDLINVERTEDHAMMER(self.o, self.h, self.l, self.c)
        idx = np.where(ham == 100)[0]
        idx1 = np.where(t == 100)[0]

        o = []
        for x in idx1:
            try:
                logic(x)
            except Exception:
                continue
        a = np.zeros(len(self.o))
        a[o] = 1
        return a

    def bull_marubozu_dragonfly(self, *args):

        ham = talib.CDLMARUBOZU(self.o, self.h, self.l, self.c)
        dra = talib.CDLDRAGONFLYDOJI(self.o, self.h, self.l, self.c)

        idx = np.where(ham == 100)[0]
        idx2 = np.where(dra == 100)[0]

        o = []
        for x in idx2:
            try:
                if x - 1 in idx and self.array[x][0] == self.array[x][-1]:
                    o.append(x)
            except Exception:
                continue
        a = np.zeros(len(self.o))
        a[o] = 1
        return a

    def bull_engulfing_touch(self, *args):
        eng = talib.CDLENGULFING(self.o, self.h, self.l, self.c)
        idx = np.where(eng == 100)[0]
        return idx

    def bull_inverse_hammer(self, *args):

        ham = talib.CDLINVERTEDHAMMER(self.o, self.h, self.l, self.c)
        ham1 = talib.CDLHAMMER(self.o, self.h, self.l, self.c)
        idx = np.where(ham == 100)[0]
        idx1 = np.where(ham1 == 100)[0]

        o = []
        for x in idx1:
            try:
                if (
                    (x - 1 and x - 2) in idx
                    and self.check_status(self.array[x][0], self.array[x][-1])
                    == "Bullish"
                    and self.check_status(self.array[x - 1][0], self.array[x - 1][-1])
                    == "Bullish"
                    and self.check_status(self.array[x - 2][0], self.array[x - 2][-1])
                    == "Bullish"
                ):
                    o.append(x)
            except Exception:
                continue

        a = np.zeros(len(self.o))
        a[o] = 1
        return a

    def bull_marubozu_gravestone_dragonfly(self, *args):
        ham = talib.CDLMARUBOZU(self.o, self.h, self.l, self.c)
        gra = talib.CDLGRAVESTONEDOJI(self.o, self.h, self.l, self.c)
        dra = talib.CDLDRAGONFLYDOJI(self.o, self.h, self.l, self.c)

        idx = np.where(ham == 100)[0]
        idx2 = np.where(gra == 100)[0]
        idx3 = np.where(dra == 100)[0]

        o = []
        for x in idx3:
            try:
                if (
                    x - 1 in idx2
                    and x - 2 in idx
                    and self.array[x - 2][0] == self.array[x - 2][-1]
                    and self.array[x - 1][0] == self.array[x - 1][-1]
                ):
                    o.append(x)
            except Exception:
                continue
        a = np.zeros(len(self.o))
        a[o] = 1
        return a

    def bear_marubozu_touch_doji(self, *args):
        ham = talib.CDLMARUBOZU(self.o, self.h, self.l, self.c)
        doji = talib.CDLDOJI(self.o, self.h, self.l, self.c)
        idx = np.where(ham == 100)[0]
        idx1 = np.where(doji == 100)[0]

        o = []
        for x in idx1:
            try:
                if (
                    x - 1 in idx
                    and self.array[x - 1][1] != self.array[x - 1][-1]
                    and self.array[x - 1][2] == self.array[x - 1][0]
                ):
                    o.append(x)
            except Exception:
                pass
        a = np.zeros(len(self.o))
        a[o] = 1
        return a

    def bear_marubozu_up_cross_snr(self, *args):
        ham = talib.CDLMARUBOZU(self.o, self.h, self.l, self.c)
        idx = np.where(ham == 100)[0]

        o = []
        for x in idx:
            if True:
                o.append(x)
        a = np.zeros(len(self.o))
        a[o] = 1
        return a

    def bear_rMarubozu_gMarubozu_red_bottom_wick(self, *args):

        mar = talib.CDLMARUBOZU(self.o, self.h, self.l, self.c)
        eng = talib.CDLENGULFING(self.o, self.h, self.l, self.c)
        idx = np.where(mar == -100)[0]
        idx3 = np.where(eng == -100)[0]

        o = []

        for x in idx3:
            if x - 2 in idx:
                o.append(x)

        a = np.zeros(len(self.o))
        a[o] = 1
        return a

    def bear_marubozu_dragonfly(self, *args):

        ham = talib.CDLMARUBOZU(self.o, self.h, self.l, self.c)
        dragon = talib.CDLDRAGONFLYDOJI(self.o, self.h, self.l, self.c)
        idx = np.where(ham == -100)[0]
        idx1 = np.where(dragon == 100)[0]

        o = []
        for x in idx1:
            if x - 1 in idx and self.array[x][0] == self.array[x][-1]:
                o.append(x)
        a = np.zeros(len(self.o))
        a[o] = 1
        return a

    def bull_marubozu_leg_touch_doji(self, *args):

        ham = talib.CDLMARUBOZU(self.o, self.h, self.l, self.c)
        doji = talib.CDLDOJI(self.o, self.h, self.l, self.c)
        idx = np.where(ham == -100)[0]
        idx1 = np.where(doji == 100)[0]

        o = []
        for x in idx1:
            try:
                if (
                    x - 1 in idx
                    and self.array[x - 1][2] != self.array[x - 1][-1]
                    and self.array[x - 1][1] == self.array[x - 1][0]
                ):
                    o.append(x)
            except Exception:
                pass
        a = np.zeros(len(self.o))
        a[o] = 1
        return a

    def bull_marubozu_leg_cross(self, *args):
        pass

    def bull_gMarubozu_rMarubozu_green_top_wick(self, *args):

        mar = talib.CDLMARUBOZU(self.o, self.h, self.l, self.c)
        eng = talib.CDLENGULFING(self.o, self.h, self.l, self.c)
        idx = np.where(mar == 100)[0]
        idx3 = np.where(eng == 100)[0]

        o = []

        for x in idx3:
            if x - 2 in idx:
                o.append(x)

        a = np.zeros(len(self.o))
        a[o] = 1
        return a

    def bull_marubozu_gravestone(self, *args):

        ham = talib.CDLMARUBOZU(self.o, self.h, self.l, self.c)
        grave = talib.CDLGRAVESTONEDOJI(self.o, self.h, self.l, self.c)
        idx = np.where(ham == 100)[0]
        idx1 = np.where(grave == 100)[0]

        o = []
        for x in idx1:
            try:
                if (
                    x - 1 in idx
                    and self.array[x][0] == self.array[x][-1]
                    and self.array[x - 1][-1] == self.array[x][-1]
                    and self.array[x][2] == self.array[x][-1]
                ):
                    o.append(x)
            except Exception:
                pass
        a = np.zeros(len(self.o))
        a[o] = 1
        return a

    def bear_invertedHammer_marubozu_rHammer(self, *args):
        ham = talib.CDLINVERTEDHAMMER(self.o, self.h, self.l, self.c)
        mar = talib.CDLMARUBOZU(self.o, self.h, self.l, self.c)
        red = talib.CDLHAMMER(self.o, self.h, self.l, self.c)

        idx = np.where(ham == 100)[0]
        idx1 = np.where(mar == 100)[0]
        idx2 = np.where(red == 100)[0]

        o = []
        for x in idx2:
            try:
                if (
                    x - 1 in idx1
                    and x - 2 in idx
                    and self.check_status(self.array[x - 2][0], self.array[x - 2][-1])
                    == "Bullish"
                    and self.check_status(self.array[x][0], self.array[x][-1]) == "Bearish"
                ):
                    o.append(x)
            except Exception:
                pass
        a = np.zeros(len(self.o))
        a[o] = 1
        return a

    def bear_shootingStar_gravestoneThrice(self, *args):
        ham = talib.CDLSHOOTINGSTAR(self.o, self.h, self.l, self.c)
        grave = talib.CDLGRAVESTONEDOJI(self.o, self.h, self.l, self.c)

        idx1 = np.where(ham == -100)[0]
        idx2 = np.where(grave == 100)[0]

        o = []

        for x in idx2:
            try:
                if (
                    x - 1 in idx2
                    and x - 2 in idx2
                    and x - 3 in idx1
                    and self.check_status(self.array[x - 3][0], self.array[x - 3][-1])
                    == "Bullish"
                ):
                    o.append(x)
            except Exception:
                pass

        a = np.zeros(len(self.o))
        a[o] = 1
        return a

    def bear_GinverseHammer_gravestone_RinverseHammer(self, *args):
        ham = talib.CDLSHOOTINGSTAR(self.o, self.h, self.l, self.c)
        grave = talib.CDLGRAVESTONEDOJI(self.o, self.h, self.l, self.c)

        idx1 = np.where(ham == -100)[0]
        idx2 = np.where(grave == 100)[0]

        o = []

        for x in idx1:
            try:
                if (
                    x - 2 in idx1
                    and x - 1 in idx2
                    and self.check_status(self.array[x - 2][0], self.array[x - 2][-1])
                    == "Bullish"
                    and self.check_status(self.array[x][0], self.array[x][-1]) == "Bearish"
                ):
                    o.append(x)
            except Exception:
                pass

        a = np.zeros(len(self.o))
        a[o] = 1
        return a

    def bear_greenBody_gravestone_Dragonfly_Takuri(self, *args):

        dra = talib.CDLDRAGONFLYDOJI(self.o, self.h, self.l, self.c)
        grave = talib.CDLGRAVESTONEDOJI(self.o, self.h, self.l, self.c)
        taku = talib.CDLTAKURI(self.o, self.h, self.l, self.c)

        idx1 = np.where(grave == 100)[0]
        idx2 = np.where(dra == 100)[0]
        idx3 = np.where(taku == 100)[0]

        o = []

        for x in idx3:
            if (
                x - 1 in idx2
                and x - 2 in idx1
                and self.check_status(self.array[x - 3][0], self.array[x - 3][-1])
                == "Bullish"
                and self.check_status(self.array[x][0], self.array[x][-1]) == "Bearish"
            ):
                o.append(x)

        a = np.zeros(len(self.o))
        a[o] = 1
        return a

    def bull_redBody_downWick_rMarubozu_GinverseHammer(self, *args):
        pass

    def bull_rHammer_dragonflyThrice(self, *args):
        pass

    def bull_rHammer_dragonfly_gHammer(self, *args):
        pass

    def bull_redBody_dragonfly_gravestone_GinverseHammer(self, *args):
        pass

    def bear_Rmarubozu_Takuri_Rmarubozu(self, *args):

        mar = talib.CDLMARUBOZU(self.o, self.h, self.l, self.c)
        ham = talib.CDLHAMMER(self.o, self.h, self.l, self.c)

        idx = np.where(mar == -100)[0]
        idx1 = np.where(ham == 100)[0]

        o = []

        for x in idx:
            if (
                x - 1 in idx1
                and x - 2 in idx
                and self.check_status(self.array[x - 2][0], self.array[x - 2][-1])
                == "Bearish"
            ):
                o.append(x)
        a = np.zeros(len(self.o))
        a[o] = 1
        return a

    def bear_Gmarubozu_invertedHammer_Ghammer(self, *args):

        mar = talib.CDLMARUBOZU(self.o, self.h, self.l, self.c)
        ham = talib.CDLHAMMER(self.o, self.h, self.l, self.c)
        inv = talib.CDLSHOOTINGSTAR(self.o, self.h, self.l, self.c)

        idx = np.where(mar == 100)[0]
        idx1 = np.where(ham == 100)[0]
        idx2 = np.where(inv == 100)[0]

        o = []

        for x in idx1:
            if (
                x - 1 in idx2
                and x - 2 in idx
                and self.check_status(self.array[x - 1][0], self.array[x - 1][-1])
                == "Bullish"
                and self.check_status(self.array[x][0], self.array[x][-1]) == "Bullish"
            ):
                o.append(x)
        a = np.zeros(len(self.o))
        a[o] = 1
        return a

    def bear_GmarubozuTwice_gravestone(self, *args):

        mar = talib.CDLMARUBOZU(self.o, self.h, self.l, self.c)
        grave = talib.CDLGRAVESTONEDOJI(self.o, self.h, self.l, self.c)

        idx = np.where(mar == 100)[0]
        idx1 = np.where(grave == 100)[0]

        o = []

        for x in idx1:
            if x - 1 in idx and x - 2 in idx:
                o.append(x)
        a = np.zeros(len(self.o))
        a[o] = 1
        return a

    def bear_RinvertedHammer_Marubozu_doji(self, *args):

        mar = talib.CDLMARUBOZU(self.o, self.h, self.l, self.c)
        inv = talib.CDLINVERTEDHAMMER(self.o, self.h, self.l, self.c)
        doji = talib.CDLDOJI(self.o, self.h, self.l, self.c)

        idx = np.where(mar == 100)[0]
        idx1 = np.where(inv == 100)[0]
        idx2 = np.where(doji == 100)[0]

        o = []

        for x in idx2:
            if (
                x - 1 in idx
                and x - 2 in idx1
                and self.check_status(self.array[x - 2][0], self.array[x - 2][-1])
                == "Bearish"
            ):
                o.append(x)
        a = np.zeros(len(self.o))
        a[o] = 1
        return a

    def bull_marubozu_shootingStar_Marubozu(self, *args):

        mar = talib.CDLMARUBOZU(self.o, self.h, self.l, self.c)
        star = talib.CDLSHOOTINGSTAR(self.o, self.h, self.l, self.c)

        idx = np.where(mar == 100)[0]
        idx1 = np.where(star == -100)[0]

        o = []
        for x in idx:
            if x - 1 in idx1 and x - 2 in idx:
                o.append(x)
        a = np.zeros(len(self.o))
        a[o] = 1
        return a

    def bull_Rmarubozu_Rhammer_RinvertedHammer(self, *args):

        mar = talib.CDLMARUBOZU(self.o, self.h, self.l, self.c)
        ham = talib.CDLHAMMER(self.o, self.h, self.l, self.c)
        inv = talib.CDLINVERTEDHAMMER(self.o, self.h, self.l, self.c)

        idx = np.where(mar == -100)[0]
        idx1 = np.where(ham == 100)[0]
        idx2 = np.where(inv == 100)[0]

        o = []

        for x in idx2:
            if (
                x - 1 in idx1
                and x - 2 in idx
                and self.check_status(self.array[x - 1][0], self.array[x - 1][-1])
                == "Bearish"
                and self.check_status(self.array[x][0], self.array[x][-1]) == "Bearish"
            ):
                o.append(x)

        a = np.zeros(len(self.o))
        a[o] = 1
        return a

    def bullRmarubozuTwice_Dragonfly(self, *args):

        mar = talib.CDLMARUBOZU(self.o, self.h, self.l, self.c)
        dra = talib.CDLDRAGONFLYDOJI(self.o, self.h, self.l, self.c)

        idx = np.where(mar == -100)[0]
        idx1 = np.where(dra == 100)[0]

        o = []

        for x in idx1:
            if x - 1 in idx and x - 2 in idx:
                o.append(x)
        a = np.zeros(len(self.o))
        a[o] = 1
        return a

    def bull_Gtakuri_Rmarubozu_doji(self, *args):

        hang = talib.CDLTAKURI(self.o, self.h, self.l, self.c)
        mar = talib.CDLMARUBOZU(self.o, self.h, self.l, self.c)
        star = talib.CDLDOJISTAR(self.o, self.h, self.l, self.c)

        idx = np.where(hang == 100)[0]
        idx1 = np.where(mar == -100)[0]
        idx2 = np.where(star == 100)[0]

        o = []

        for x in idx2:
            if (
                x - 1 in idx1
                and x - 2 in idx
                and self.check_status(self.array[x - 2][0], self.array[x - 2][-1])
                == "Bullish"
            ):
                o.append(x)
        a = np.zeros(len(self.o))
        a[o] = 1
        return a

    def bear_RmarubozuTwice_gravestone(self, *args):

        mar = talib.CDLMARUBOZU(self.o, self.h, self.l, self.c)
        grave = talib.CDLGRAVESTONEDOJI(self.o, self.h, self.l, self.c)

        idx = np.where(mar == -100)[0]
        idx2 = np.where(grave == 100)[0]

        o = []

        for x in idx2:
            if x - 1 in idx and x - 2 in idx:
                o.append(x)

        a = np.zeros(len(self.o))
        a[o] = 1
        return a

    def bear_GbodyUpWick_GinvertedHammer_GinvertedHammer(self, *args):

        shoot = talib.CDLSHOOTINGSTAR(self.o, self.h, self.l, self.c)

        idx = np.where(shoot == -100)[0]
        o = []

        for x in idx:
            try:
                if (
                    self.check_status(self.array[x - 1][0], self.array[x - 1][-1])
                    == "Bullish"
                    and self.array[x - 1][1] != self.array[x - 1][-1]
                ) and (
                    self.check_status(self.array[x + 1][0], self.array[x + 1][-1])
                    == "Bullish"
                    and self.get_size(self.array[x + 1][0], self.array[x + 1][-1])
                    < self.get_size(self.array[x][0], self.array[x][-1])
                    and self.array[x + 1][1] != self.array[x + 1][-1]
                ):
                    o.append(x + 1)
            except Exception:
                pass

        a = np.zeros(len(self.o))
        a[o] = 1
        return a

    def bear_twoGreens_shootingStar(self, *args):

        shoot = talib.CDLSHOOTINGSTAR(self.o, self.h, self.l, self.c)

        idx = np.where(shoot == -100)[0]

        o = []

        for x in idx:
            try:
                if (
                    self.check_status(self.array[x - 2][0], self.array[x - 2][-1])
                    == "Bullish"
                    and self.check_status(self.array[x - 1][0], self.array[x - 1][-1])
                    == "Bullish"
                ):
                    o.append(x)
            except Exception:
                pass

        a = np.zeros(len(self.o))
        a[o] = 1
        return a

    def bear_Takuri_redBody_longLegged_redBody(self, *args):

        tak = talib.CDLHAMMER(self.o, self.h, self.l, self.c)
        long = talib.CDLLONGLEGGEDDOJI(self.o, self.h, self.l, self.c)

        idx = np.where(tak == 100)[0]
        idx2 = np.where(long == 100)[0]

        o = []

        for x in idx:
            try:
                if (
                    self.check_status(self.array[x + 1][0], self.array[x + 1][-1])
                    == "Bearish"
                    and self.check_status(self.array[x + 3][0], self.array[x + 3][-1])
                    == "Bearish"
                    and x + 2 in idx2
                ):
                    o.append(x + 3)
            except Exception:
                pass
        a = np.zeros(len(self.o))
        a[o] = 1
        return a

    def bull_MarubozuTwice_Dragonfly(self, *args):
        pass

    def bull_RhammerThrice(self, *args):

        hammer = talib.CDLHAMMER(self.o, self.h, self.l, self.c)

        idx = np.where(hammer == 100)[0]

        o = []

        for x in idx:
            try:
                if (
                    self.check_status(self.array[x - 2][0], self.array[x - 2][-1])
                    == "Bearish"
                    and self.check_status(self.array[x - 1][0], self.array[x - 1][-1])
                    == "Bearish"
                    and self.check_status(self.array[x][0], self.array[x][-1]) == "Bullish"
                    and self.array[x][0] == self.array[x - 1][-1]
                    and self.array[x][-1]
                    > ((self.array[x - 1][0] + self.array[x - 1][-1]) / 2)
                ):
                    o.append(x)
            except Exception:
                pass

        a = np.zeros(len(self.o))
        a[o] = 1
        return a

    def bull_RinvertedHammer_Rhammer_Gtakuri(self, *args):
        pass

    def bull_RinvertedHammer_SpinningTop_LongDoji_GHammer(self, *args):
        pass
