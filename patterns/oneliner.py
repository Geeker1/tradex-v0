from patterns.base import BasePattern

import numpy as np


class Doji(BasePattern):

    """
    This class determines if the candle bars are dojis,
    appends 1 or 0 depending on if condition is true or not

    Methods:

        iterate() : >>> This method loops through array of
        candle bars and tries to determine if
        it falls as a pattern or not
    """

    def iterate(self):
        self.truth = []
        ad = self.df
        for x in ad:
            op, _, _, close = x[0], x[1], x[2], x[3]
            if op == close:
                self.truth.append(1)
            else:
                self.truth.append(0)
        return np.array(self.truth)


class GravestoneDoji(BasePattern):

    f"""
    This class determines if the candle bars are dojis,
    appends 1 or 0 depending on if condition is true or not

    Methods:

        iterate() : >>> This method loops through array of
                        candle bars and tries to determine if
                        it falls as a pattern or not

        confirm_pattern(): >>> This method receives
        open,high,low,close values and tries to output if
        it falls as Pattern or not...

    """

    def confirm_pattern(self, op, high, low, close):
        if abs(op - high) / abs(op - low) > 3:
            return -1
        return 0

    def iterate(self):
        truth = []
        ad = self.df
        for x in ad:
            op, high, low, close = x[0], x[1], x[2], x[3]
            if op == close:
                integer = self.confirm_pattern(op, high, low, close)
                truth.append(integer)
            else:
                truth.append(0)

        return np.array(truth)


class DragonFlyDoji(GravestoneDoji):
    def confirm_pattern(self, op, high, low, close):
        if abs(op - low) / abs(op - high) > 3:
            return 1
        return 0


class Hammer(BasePattern):
    def confirm_pattern(self, leg, body, direction):
        if round(leg / body) == 2:
            return direction[-1]
        return 0

    def iterate(self):
        self.truth = []
        ad = self.df
        for x in ad:
            op, high, low, close = x[0], x[1], x[2], x[3]
            real = abs(op - close)
            candle = self.f(op, close)

            if candle == "Bearish":
                if abs(op - low) != 0:
                    self.truth.append(0)
                    continue
                integer = self.confirm_pattern(
                    abs(close - high), real, ("Bearish", -1))
                self.truth.append(integer)

            elif candle == "Bullish":
                if abs(high - close) != 0:
                    self.truth.append(0)
                    continue
                integer = self.confirm_pattern(
                    abs(op - low), real, ("Bullish", 1))
                self.truth.append(integer)

            elif candle == "Indecisive":
                self.truth.append(0)

        return np.array(self.truth)


class InvertedHammer(BasePattern):
    def confirm_pattern(self, up, body, direction):
        if round(up / body) == 2:
            return direction[-1]
        return 0

    def iterate(self):
        self.truth = []
        ad = self.df
        for x in ad:
            op, high, low, close = x[0], x[1], x[2], x[3]
            real = abs(op - close)
            func = self.f(op, close)
            direction = func

            if direction == "Bearish":
                if abs(close - high) != 0:
                    self.truth.append(0)
                    continue
                integer = self.confirm_pattern(
                    abs(op - low), real, ("Bearish", -1))
                self.truth.append(integer)

            elif direction == "Bullish":
                if abs(op - low) != 0:
                    self.truth.append(0)
                    continue
                integer = self.confirm_pattern(
                    abs(close - high), real, ("Bullish", 1))
                self.truth.append(integer)

            elif direction == "Indecisive":
                self.truth.append(0)

        return np.array(self.truth)


class Pinbar(BasePattern):
    def confirm_pattern(self, up, leg, body, direction):
        if body / up <= 3 and body / up >= 1.8 and leg / body >= 2:
            return direction[-1]
        return 0

    def iterate(self):
        self.truth = []
        ad = self.df
        for x in ad:
            op, high, low, close = x[0], x[1], x[2], x[3]

            real = abs(op - close)
            candle = self.f(op, close)
            if candle == "Bearish":
                integer = self.confirm_pattern(
                    abs(op - low), abs(close - high), real, ("Bearish", -1)
                )
                self.truth.append(integer)

            elif candle == "Bullish":
                integer = self.confirm_pattern(
                    abs(close - high), abs(op - low), real, ("Bullish", 1)
                )
                self.truth.append(integer)

            elif candle == "Indecisive":
                self.truth.append(0)
        return np.array(self.truth)


class InvertedPinbar(Pinbar):
    def confirm_pattern(self, up, leg, body, direction):
        if (
            round(body / leg) <= 3 and
            body / leg >= 1.8 and
            round(up / body) >= 2
        ):
            return direction[-1]
        return 0
