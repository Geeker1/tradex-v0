import pandas as pd
import numpy as np


from patterns.base import BasePattern


df = pd.DataFrame(
    {
        "open": [30.000, 18.000, 20.000],
        "high": [18.000, 15.000, 33.000],
        "low": [33.000, 15.000, 18.000],
        "close": [20.000, 18.000, 30.000],
    },
    index=pd.to_datetime(["2012-11-1", "2012-11-2", "2012-11-3"]),
)


class MorningStar(BasePattern):
    def confirm_pattern(self, *args):
        pt_open, pt_high, pt_low, pt_close = args[0]
        mt_open, mt_high, mt_low, mt_close = args[1]
        rt_open, rt_high, rt_low, rt_close = args[2]
        mt_cond = args[3]

        pt_candle_size = pt_open - pt_close
        rt_candle_size = rt_close - rt_open
        pt_middle = (pt_close + pt_open) / 2
        rt_middle = (rt_close + rt_open) / 2

        # Check that size of middle candlestick is greater
        # than left or right candlestick and return 0

        if (
            abs(mt_close - mt_open) > (
                pt_candle_size or rt_candle_size
            )
        ):
            return 0

        # Verify that there are long wicks and return 0

        if (
            (pt_high - pt_open) + (pt_close - pt_low) >
            (pt_open - pt_middle) or
            (rt_high - rt_close) + (rt_open - rt_low) >
            (rt_close - rt_middle)
        ):
            return 0

        if (
            rt_close >= pt_middle and
            pt_open >= rt_middle and
            rt_open == pt_close
        ):
            if (
                mt_cond == "Bullish" or
                mt_cond == "Indecisive"
            ):
                if (
                    mt_close < (
                        pt_middle and rt_middle
                    ) and
                    (mt_high and mt_close) < (pt_middle or rt_middle) and
                    (mt_high - mt_close <= mt_open - mt_low)
                ):
                    return 1
            elif mt_cond == "Bearish":
                return 0
                # if (
                #     mt_open < (
                #         pt_middle and rt_middle
                #     ) and
                #     (mt_high and mt_open) >= (pt_middle or rt_middle) and
                #     mt_high - mt_open <= mt_close - mt_low
                # ):
                #     return 1
        return 0

    def iterate(self):
        self.truth = []
        ad = self.df
        for x, y in enumerate(ad):

            if x - 1 == -1 or x - 2 == -1:
                self.truth.append(0)
                continue

            previous = ad[x - 2]
            last = ad[x - 1]
            current = y

            p_op, p_high, p_low, p_close = previous
            l_op, l_high, l_low, l_close = last

            c_op, c_high, c_low, c_close = current

            pt = self.f(p_op, p_close)
            lt = self.f(l_op, l_close)
            ct = self.f(c_op, c_close)

            # This block below was the only thing I changed
            if pt == "Bearish" and ct == "Bullish":
                integer = self.confirm_pattern(
                    (p_op, p_high, p_low, p_close),
                    (l_op, l_high, l_low, l_close),
                    (c_op, c_high, c_low, c_close),
                    lt,
                )

                self.truth.append(integer)
            else:
                self.truth.append(0)

        return np.array(self.truth)


class EveningStar(BasePattern):
    def confirm_pattern(self, *args):
        pt_open, pt_high, pt_low, pt_close = args[0]
        mt_open, mt_high, mt_low, mt_close = args[1]
        rt_open, rt_high, rt_low, rt_close = args[2]
        mt_cond = args[3]

        pt_candle_size = pt_close - pt_open
        rt_candle_size = rt_open - rt_close
        pt_middle = (pt_close + pt_open) / 2
        rt_middle = (rt_close + rt_open) / 2

        # Check that size of middle candlestick is greater
        # than left or right candlestick and return 0

        if (
            abs(mt_close - mt_open) > (
                pt_candle_size or rt_candle_size
            )
        ):
            return 0

        # Verify that there are  long wicks and return 0

        if (
            (pt_high - pt_close) + (pt_open - pt_low) >
            (pt_close - pt_middle) or
            (rt_high - rt_open) + (rt_close - rt_low) >
            (rt_open - rt_middle)
        ):
            return 0

        if (
            rt_close <= pt_middle and
            pt_close >= rt_middle and
            rt_open == pt_close
        ):
            if (
                mt_cond == "Bearish" or
                mt_cond == "Indecisive"
            ):
                if (
                    mt_close > (
                        pt_middle and rt_middle
                    ) and
                    (mt_close and mt_low) > (pt_middle or rt_middle) and
                    (mt_close - mt_low <= mt_high - mt_open)
                ):
                    return 1
            elif mt_cond == "Bullish":
                return 0
                # if (
                #     mt_open > (
                #         pt_middle and rt_middle
                #     ) and
                #     mt_open - mt_low >= (pt_middle or rt_middle) and
                #     mt_open - mt_low <= mt_high - mt_close
                # ):
                #     return 1
        return 0

    def iterate(self):
        self.truth = []
        ad = self.df
        for x, y in enumerate(ad):

            if x - 1 == -1 or x - 2 == -1:
                self.truth.append(0)
                continue

            prev = ad[x - 2]
            last = ad[x - 1]
            current = y

            p_op, p_high, p_low, p_close = prev
            l_op, l_high, l_low, l_close = last
            c_op, c_high, c_low, c_close = current

            pt = self.f(p_op, p_close)
            lt = self.f(l_op, l_close)
            ct = self.f(c_op, c_close)

            # This block below was the only thing I changed
            if pt == "Bullish" and ct == "Bearish":
                integer = self.confirm_pattern(
                    (p_op, p_high, p_low, p_close),
                    (l_op, l_high, l_low, l_close),
                    (c_op, c_high, c_low, c_close),
                    lt,
                )

                self.truth.append(integer)
            else:
                self.truth.append(0)

        return np.array(self.truth)
