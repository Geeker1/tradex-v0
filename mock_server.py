import zmq
from tradex.config import MOCK_SUB_PORT, MOCK_ROUTER_PORT
import time
from tradex.market.clear_database import main as mo
from tradex.market.fetch_history_hst import parse_hst
from tradex.tests.mocked_classes import MockedMarketPair
from datetime import datetime, timedelta
from threading import Thread
import pandas as pd
from threading import Thread
import logging


def publish(port=MOCK_SUB_PORT):

    context = zmq.Context()
    publish = context.socket(zmq.PUB)
    publish.bind(f'tcp://*:{port}')

    now = datetime.now()
    term = now + timedelta(minutes=1, seconds=10)

    while datetime.now() < term:

        try:
            time_int = pd.Timestamp.now('UTC').timestamp()
            publish.send_string(
                f'EURUSD 1.9023;1.9879;{time_int}'
            )
            print('Moving on.....')
            time.sleep(1)
        except KeyboardInterrupt:
            publish.close()
            context.term()

    publish.send_string('EURUSD kill')

    publish.close()
    context.term()


def req_response():
    ctx = zmq.Context()
    sock = ctx.socket(zmq.ROUTER)
    sock.bind(f'tcp://*:{MOCK_ROUTER_PORT}')

    msg = sock.recv_multipart()
    sock.send_multipart([msg[0], b"", b"ok"])
    logging.info("Successfully sent message to receiver socket....")

    sock.close()
    ctx.term()
    logging.info("Breaking out of function....all successful....")
