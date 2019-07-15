

import pytest
from tradex.patterns.base import BasePattern
# from tradex.patterns.doubleliner import TwoLinePattern,\
# Tweezer,Harami,HaramiCross,Engulfing,PiercingDarkCloud

# from tradex.patterns.oneliner import Doji,\
# GravestoneDoji,DragonFlyDoji,Hammer,InvertedHammer,Pinbar,InvertedPinbar

# from tradex.patterns.multiliner import MorningStar,EveningStar
import pandas as pd


#################### JUST TESTED THE BASE PATTERN ##########################


@pytest.fixture
def setup_base_pattern():

    frame = pd.DataFrame(
        {'open': [1.2356, 1.9089, 3.4567],
         'high': [1.4589, 1.2356, 1.8970],
         'low': [1.4589, 1.2356, 1.8970],
         'close': [2.3456, 5.6079, 0.9870]},
            index=pd.to_datetime(['2012-11-1', '2012-11-2', '2012-11-3']))
    base = BasePattern(frame)

    return base


def test_base_methods(setup_base_pattern):

    assert setup_base_pattern.f(1.2390, 2.3495) == 'Bullish'
    assert (BasePattern.confirm_market_pressure(

        'Bullish', 2.3900, 1.2356, 1.9089, 3.4567, 2.3458
        )) in ['Bullish', 'Bearish', 'Indecisive']
    assert type(BasePattern.append_conditions(
        1.9089, 3.4567, 2.3458, 'Bullish'
        )) == list



