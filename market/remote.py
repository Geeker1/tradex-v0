from tradex.market.inter import MarketParser
from tradex.reuse import parse_to_integer

prefix = "frx"


class Binary(MarketParser):

    BinaryRouterNo = parse_to_integer("BinaryRouter")

    """ prefix is appended to actual market pair because we only want
    to subscribe/fetch data with that prefix attached to get the right values
    """

    def __init__(self, pair, sub_port=None):

        super().__init__(
            pair=prefix + pair,
            router_port=self.BinaryRouterNo, sub_port=sub_port)
