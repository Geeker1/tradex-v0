import pandas as pd

from tradex.market.base import MarketPair
from tradex.market.metatrader import MarketParser
from tradex.config import MOCK_SUB_PORT, MOCK_ROUTER_PORT
# import zmq


class MockedMarketPair(MarketPair):

    def __init__(self, pair, sub=MOCK_SUB_PORT, router=MOCK_ROUTER_PORT):

        super().__init__(
            pair=pair, sub_port=sub, router_port=router
        )

        self.M1 = pd.DataFrame(
            {'open': [1.4567], 'high': [3.4567],
                'low': [0.9800], 'close': [1.4532]}
            , index=pd.to_datetime(['2019-09-08 01:00:00'])
        )

    def logic_contained(self):

        MarketParser.main_logic(self)

    def validate_resampling(self):
        pass

class MockedRemotePair(MarketPair):
    pass
