
################# Object IMPORTS ##################

from tradex.market.inter import MarketParser

from tradex.reuse import parse_to_integer


class MetaTrader(MarketParser):

    MetaRouterNo = parse_to_integer("MetaRouter")

    def __init__(self, pair, router=None, sub=None):

        super().__init__(
            pair=pair, router_port=self.MetaRouterNo,
            sub_port=sub
        )
