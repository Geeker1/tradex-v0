import numpy as np


class Indicator:
    """This Indicator is a wrapper for Talib indicator library,
    You just have to specify the number of values the indicator returns
    and the number of frames ['open','high','low','close'] in this
    order, and the Talib function, then pass in default arguments
    for that Talib function and it just gets passed in as kwargs...

    NOTE: Only pass in correct arguments to kwargs..else
    you would receive an error as all kwargs args are passed into
    the talib function straight up....

    It returns in this numeric order --> v1,v2,...vn
    Depending on the number of return u pass....
    You can now access attributes by calling them directly..

    NOTE: The no of returns must match what the indicator actually returns
    else you would receive another error as the arguments to unpack,
    might be too small or large....

    NOTE: The returned values must be a numpy array as appends to
    a numpy array expects a numpy as array as second argument..

    NOTE: The returned values matches exactly what the talib function
    returns but in an ascending order --> v1,v2...vn
    so if talib.MACD returns [macd,hist,signal] as 3 returns
    then the equivalent v1,v2,v3 would match this exactly"""

    def __init__(self, name, func, lis=['close'], no=1, **kwargs):
        """BIG WARNING "no" argument must be greater than 0 and an integer
        No matter what...!!!"""

        self.r = no
        self.func = func
        self.kwargs = kwargs
        self.name = name
        self.lis = lis

        if no > 1:
            for i in range(1, no + 1):
                exec(f"self.v{i} = np.array([], dtype=np.float64)")
        else:
            self.v1 = np.array([], dtype=np.float64)

    def update(self, args, u=False):
        _r = [args[x].values for x in args[self.lis].columns]
        #  Logic for if no. of returns is specified as only 1
        if self.r == 1:
            arr = self.func(*_r, **self.kwargs)
            arr = arr if u else arr[-1]
            self.v1 = np.append(self.v1, arr)
            return

        # Logic for if no. of returns is > 1
        exec(f"a = self.func(*_r, **self.kwargs)")
        for x, y in enumerate(eval("a")):
            y = y if u else y[-1]
            exec(f"self.v{x + 1} = np.append(self.v{x + 1},y)")

    def __repr__(self):
        return f"<custom {self.name} indicator {hex(id(self))}>"
