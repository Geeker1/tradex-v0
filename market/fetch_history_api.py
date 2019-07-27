import zmq
import json
import pandas as pd
from tradex.market.remote import Binary
from tradex.market.clear_database import main
from influxdb.exceptions import InfluxDBClientError
from tradex.config import INTERMED_ROUTER
import influxdb as db
import numpy as np


def Parse_History_Candle_To_DataFrame(json_list):

    def retrack(x):
        x = pd.Timestamp.utcfromtimestamp(x).tz_localize('UTC')
        return x

    hist = pd.DataFrame(json_list)
    hist.index = hist.epoch.apply(retrack)
    del hist['epoch']
    hist = hist[['open', 'high', 'low', 'close']]
    hist.index.name = 'time'

    return hist


def fetch_history_from_api(identity, data=None, port=INTERMED_ROUTER):

    ctx = zmq.Context()
    req = ctx.socket(zmq.REQ)
    req.setsockopt_string(zmq.IDENTITY, f"{identity}")
    req.connect(f'tcp://localhost:{port}')
    if data is not None:
        req.send_json(data)
    else:
        raise Exception("Error...Data is not meant to be a None object")

    try:
        msg = req.recv_json()
        print(msg)
    except json.JSONDecodeError:
        req.close()
        ctx.term()
        return pd.DataFrame()
    except KeyboardInterrupt:
        req.close()
        ctx.term()
        return pd.DataFrame()

    return Parse_History_Candle_To_DataFrame(msg['candles'])


def fetch_missing_data_fill_database(
        pair, port=INTERMED_ROUTER, start=None, end=None):
    """
    There are three main conditions this function fulfills.....

    1. IF NO DATABASE FOR THAT PAIR... It fetches data for a
    particular time range , creates a new database and saves the
    fetched data in that database, then returns fetched data

    2. IF THERE IS A DATABASE.... It checks in database to make sure
    there are no loopholes, if any is found it fetches dat DATA
    and saves the loop data in database, then returns the fetched data

    3. IF ["start" and "end"] VARIABLES do not default to None for
    that pair it fetches for data with regards to that time-range
    of start/end and returns it....

    """

    prefix = pair if pair == 'R_50' else 'frx' + pair
    empty = pd.DataFrame()
    ctx = zmq.Context()
    req = ctx.socket(zmq.REQ)
    req.setsockopt_string(zmq.IDENTITY, f'{pair}1')
    req.connect(f"tcp://localhost:{port}")

    def return_val(*args):
        nonlocal req, empty
        get_dict = Binary.populate_history_schema(*args, 'candles')
        req.send_json(get_dict)
        try:
            msg = req.recv_json()
            frame = Parse_History_Candle_To_DataFrame(msg['candles'])
            empty = empty.append(frame)
            print(msg)
        except json.JSONDecodeError:
            print(
                """Error decoding response sent from router,
                closing sockets and exiting""")
            raise Exception("Websocket is not responding...check why")

    def loop_and_fetch(gen):
        while True:
            try:
                n = next(gen)
                return_val(*n, prefix)
            except StopIteration:
                if len(empty) == 0:
                    raise Exception("Empty frame returned.....")
                break

    # CONDITION 3
    # I set it here to run before CONDITION 1/2
    if (start and end) is not None:
        gen = yield_partition(start, end)
        loop_and_fetch(gen)
        return empty

    # CONDITION 1
    try:
        client = db.DataFrameClient(host='localhost', port=8086, database=pair)
        empty = empty.append(
            client.query(f'select * from {pair}')[f'{pair}']
        )
        missing = return_missing_timestamps(empty)
        gen = return_stamp_interval(np.array(missing, dtype=np.int64))
        loop_and_fetch(gen)
        print("fetched from database")

    # CONDITION 2
    except InfluxDBClientError:

        now = pd.Timestamp.utcnow()
        prev = now - pd.Timedelta(days=10)
        # prev = now - pd.Timedelta(weeks=6)
        i, e = int(prev.timestamp()), int(now.timestamp())
        gen = yield_partition(i, e)
        loop_and_fetch(gen)
        client.create_database(f'{pair}')

    # Code Cleanup and deallocation
    finally:
        client.write_points(empty, f'{pair}', protocol='json')
        client.close()
        req.close()
        ctx.term()

    print("FETCHED DATA SUCCESSFULLY.....")

    return empty


def yield_partition(*args):
    b, e = args[0], args[1]
    const = 5000 * 60
    for x in range(b, e, const):
        if (x + const) < e:
            yield (x, x + const)
        elif (x + const) > e:
            yield (x, e)


def return_stamp_interval(missing_stamp):
    start_end = []
    for index, stamp in enumerate(missing_stamp):
        if (index - 1) == -1:
            start_end.append(stamp)
            if missing_stamp[-1] == stamp:
                start_end.append(stamp)
                for x in yield_partition(*start_end):
                    yield x
            continue

        val = stamp - missing_stamp[index - 1]
        if val > 60:
            start_end.append(missing_stamp[index - 1])
            for x in yield_partition(*start_end):
                yield x

            start_end.clear()
            start_end.append(stamp)

            if len(missing_stamp) - 1 == index:
                start_end.append(stamp)
                for x in yield_partition(*start_end):
                    yield x

        if len(missing_stamp) - 1 == index and val == 60:
            start_end.append(stamp)
            for x in yield_partition(*start_end):
                yield x


def return_missing_timestamps(frame):

    missing_stamps = []
    date_range = pd.date_range(frame.index[0], frame.index[-1], freq='1T')
    for date in date_range:
        if date not in frame.index and \
                date.day_name not in ['Saturday', 'Sunday']:
            missing_stamps.append(int(date.timestamp()))
    print("Lenght of missing stamps are ", len(missing_stamps))
    return missing_stamps


if __name__ == '__main__':
    fetch_missing_data_fill_database('R_50')
