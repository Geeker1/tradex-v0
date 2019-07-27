import pytest
from tradex.market.clear_database import main
from tradex.market.fetch_history_hst import parse_hst
from mocked_classes import MockedMarketPair

import pandas as pd
import os
from tradex.mock_server import publish, req_response
from threading import Thread
from tradex.market.metatrader import MarketParser
import logging


@pytest.fixture
def initials_exception():
    main('EURUSD', True)
    x = MarketParser('EURUSD')

    yield x

    main('EURUSD', True)


@pytest.fixture
def mock_server(request):

    x = MockedMarketPair('EURUSD')
    proc = Thread(target=publish)
    proc1 = Thread(target=x.start)
    proc2 = Thread(target=x.logic_contained)
    proc3 = Thread(target=req_response)

    proc.start()
    proc3.start()
    proc1.start()
    proc2.start()

    proc.join()
    proc3.join()
    proc1.join()
    proc2.join()
    # x.shutdown_sockets()

    def cleanup():
        nonlocal proc, proc2, proc1, proc3
        print("tearing down context")

        del proc
        del proc1
        del proc2
        del proc3

        print(f'\n Finally closed... hoping for no Errors')

    request.addfinalizer(cleanup)

    logging.info("Tearing down whole context")

    return x


################  TEST FUNCTIONS FOR MARKET SUB-PACKAGE ###################


def test_data_checks(mock_server):

    assert len(mock_server.M1) >= 2
    assert len(mock_server.df_tick) >= 3


def test_market_type_checks(initials_exception):

    c = [initials_exception.M5, initials_exception.M15,
         initials_exception.H1, initials_exception.H4, initials_exception.D1]

    rt_dict = initials_exception.__dict__

    for frames in c:
        assert frames is not None


#################  TESTING FOR TYPE ERRORS AND OTHER CHECKS ON parse_hst #######################

def test_fetch_hst_type_checks():
    with pytest.raises(TypeError):
        parse_hst()

    with pytest.raises(FileNotFoundError):
        parse_hst('lefkoef')


def test_assert_return_type():

    with open('test.txt', 'wb') as fp:
        fp.write(b'Hello world')

    assert type(parse_hst('test.txt')) == pd.core.frame.DataFrame
    os.remove('test.txt')

