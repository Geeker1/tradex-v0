import numpy as np


class BasePattern:

    DIRECTION = (("Bearish", -1), ("Bullish", 1), ("Indecisive", 0))

    """ This is the base class for all Candlestick patterns, note
     that all patterns created here inherit from this class

     Parameters:

     The Base Class accepts only one parameter which must
     be a Pandas DataFrame or Numpy Array

     Numpy array >>>>
         Must be a Numpy array with a shape of (?,4) and order
         >>>>>>>  open,high,low,close

     Pandas DataFrame of order >>>>>>>
         open,high,low,close

     """

    columns = ['open', 'high', 'low', 'close']

    def __init__(self, array_x):
        try:
            self.df = array_x[self.columns].values
        except AttributeError:
            try:
                assert type(array_x) == np.ndarray
                assert len(array_x.shape) == 2
                assert array_x.shape[-1] == 4
                self.df = array_x
            except AssertionError as e:
                print(
                    "Values passed did not meet requirement,\
                    It must be a Dataframe or Numpy Array"
                )
                raise e(
                    "Could not determine if the\
                    value was a valid array"
                )

        self._index = len(self.df)

    def f(self, open_x, close):
        if open_x > close:
            return "Bearish"
        elif open_x < close:
            return "Bullish"
        elif open_x == close:
            return "Indecisive"

    @staticmethod
    def confirm_market_pressure(market_condition, real_body, open_x, high, low, close):

        if market_condition == "Bearish":
            up = abs(close - high)
            down = abs(low - open_x)
            market = "Bearish"
            signal = BasePattern.append_conditions(up, down, real_body, market)
            signal.append(market)

        elif market_condition == "Bullish":
            up = abs(open_x - low)
            down = abs(high - close)
            market = "Bullish"
            signal = BasePattern.append_conditions(up, down, real_body, market)
            signal.append(market)

        elif market_condition == "Indecisive":
            up = abs(low - open_x)
            down = abs(high - open_x)
            market = "Indecisive"
            signal = BasePattern.append_conditions(up, down, real_body, market)
            signal.append(market)

        if signal.count("Bullish") > 1:
            return "Bullish"
        elif signal.count("Bearish") > 1:
            return "Bearish"
        else:
            return "Indecisive"

        return None

    @staticmethod
    def append_conditions(up, down, real, market):
        s = []
        if up > down:
            s.append("Bullish")
            if up > real:
                s.append("Bullish")
            s.append(market)
        elif up < down:
            s.append("Bearish")
            if down > real:
                s.append("Bearish")
            s.append(market)
        elif up == down:
            s.append(market)
            s.append(market)
        return s
