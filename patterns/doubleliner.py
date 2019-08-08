from patterns.base import BasePattern
import numpy as np
# import numpy as np


class TwoLinePattern(BasePattern):

    f"""
    This class determines multiple candlesticks and
    if they match a peculiar pattern or not
    appends 1 or 0 depending on if condition is true or not

    Methods:

        iterate() : >>> This method loops through array of candle bars
        and tries to determine if
        it falls as a pattern or not

        confirm_bull_pattern(): >>> This method receives open,high,low,
        close values and tries to output
        if the pattern indicates upward movement

        confirm_bear_pattern(): >>> This method receives open,high,low,close
        values and tries to output
        if the pattern indicates downward movement

    """

    def confirm_bull_pattern(self, *args):
        pass

    def confirm_bear_pattern(self):
        pass

    def iterate(self):
        self.truth = []
        ad = self.df
        for x, y in enumerate(ad):
            if x - 1 == -1:
                self.truth.append(0)
                continue

            last = ad[x - 1]
            current = y

            l_op, l_high, l_low, l_close = last
            c_op, c_high, c_low, c_close = current

            lt = self.f(l_op, l_close)
            ct = self.f(c_op, c_close)

            if lt == "Bearish" and ct == "Bullish":
                integer = self.confirm_bull_pattern(
                    (l_op, l_high, l_low, l_close),
                    (c_op, c_high, c_low, c_close),
                )

                self.truth.append(integer)
            elif lt == "Bullish" and ct == "Bearish":
                integer = self.confirm_bear_pattern(
                    (l_op, l_high, l_low, l_close),
                    (c_op, c_high, c_low, c_close),
                )

                self.truth.append(integer)

            else:
                self.truth.append(0)

        return np.array(self.truth)


class Harami(TwoLinePattern):
    def confirm_bull_pattern(self, *args):
        lt_open, _, _, lt_close = args[0]
        rt_open, rt_high, rt_low, rt_close = args[1]

        if (
            (lt_open > rt_high and lt_open > rt_close) and
            (lt_close < rt_low and lt_close < rt_open)
        ):
            return 1

        return 0

    def confirm_bear_pattern(self, *args):
        lt_open, _, _, lt_close = args[0]
        rt_open, rt_high, rt_low, rt_close = args[1]

        if (
            (lt_close > rt_open and lt_close > rt_high) and
            (lt_open < rt_close and lt_open < rt_low)
        ):
            return -1

        return 0


class HaramiCross(TwoLinePattern):
    def confirm_bull_pattern(self, *args):
        lt_open, _, _, lt_close = args[0]
        _, rt_high, rt_low, _ = args[1]

        if (lt_open > rt_high) and (lt_close < rt_low):
            return 1

        return 0

    def confirm_bear_pattern(self, *args):
        lt_open, _, _, lt_close = args[0]
        _, rt_high, rt_low, _ = args[1]

        if (lt_close > rt_high) and (lt_open < rt_low):
            return -1

        return 0

    def iterate(self):
        self.truth = []
        ad = self.df
        for x, y in enumerate(ad):

            if x - 1 == -1:
                self.truth.append(0)
                continue

            last = ad[x - 1]
            current = y

            l_op, l_high, l_low, l_close = last
            c_op, c_high, c_low, c_close = current

            lt = self.f(l_op, l_close)
            ct = self.f(c_op, c_close)

            # This block below was the only thing I changed
            if lt == "Bearish" and ct == "Indecisive":
                integer = self.confirm_bull_pattern(
                    (l_op, l_high, l_low, l_close),
                    (c_op, c_high, c_low, c_close),
                )

                self.truth.append(integer)
            elif lt == "Bullish" and ct == "Indecisive":
                integer = self.confirm_bear_pattern(
                    (l_op, l_high, l_low, l_close),
                    (c_op, c_high, c_low, c_close),
                )
                self.truth.append(integer)
            else:
                self.truth.append(0)

        return np.array(self.truth)


class Engulfing(TwoLinePattern):
    def confirm_bull_pattern(self, *args):
        lt_open, _, _, lt_close = args[0]
        rt_open, _, _, rt_close = args[1]

        # print("Confirming bull pattern")
        # print("left side is....", self.f(lt_open, lt_close))
        # print("Right side is...", self.f(rt_open, rt_close), "\n")

        if(
            rt_close < lt_open and
            rt_open == lt_close and
            1 < (abs(rt_open - rt_close) / abs(lt_open - lt_close)) <= 2.5
        ):
            return 1

        return 0

    def confirm_bear_pattern(self, *args):
        lt_open, _, _, lt_close = args[0]
        rt_open, _, _, rt_close = args[1]

        # print("Confirming bear pattern")
        # print("left side is....", self.f(lt_open, lt_close))
        # print("Right side is...", self.f(rt_open, rt_close), "\n")

        if(
            rt_close > lt_open and
            rt_open == lt_close and
            1 < (abs(rt_open - rt_close) / abs(lt_open - lt_close)) <= 2.5
        ):
            return -1

        return 0


class PiercingDarkCloud(TwoLinePattern):
    def confirm_bull_pattern(self, *args):
        lt_open, _, _, lt_close = args[0]
        rt_open, _, _, rt_close = args[1]

        lt_middle = 0.5 * (lt_open + lt_close)

        # print("left side is....", self.f(lt_open, lt_close))
        # print("Right side is...", self.f(rt_open, rt_close), "\n")

        if (
            rt_open < lt_close and
            (
                rt_close > lt_middle or
                lt_middle > rt_close > lt_close
            ) and
            rt_close < lt_open
        ):
            return 1

        return 0

    def confirm_bear_pattern(self, *args):
        lt_open, _, _, lt_close = args[0]
        rt_open, _, _, rt_close = args[1]

        lt_middle = 0.5 * (lt_open + lt_close)

        # print("left side is....", self.f(lt_open, lt_close))
        # print("Right side is...", self.f(rt_open, rt_close), "\n")

        if (
            rt_open > lt_close and
            (
                (rt_close < lt_middle) or
                lt_middle > rt_close < lt_close
            ) and
            rt_close > lt_open
        ):
            return -1

        return 0
