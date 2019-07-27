import time
import json
import zmq
import sys
import pandas as pd
import websocket
from tradex.config import INFLUXDB_PORT, INTERMED_ROUTER
from tradex.market.base import MarketPair
from tradex.reuse import parse_to_integer
from tradex.market.fetch_history_api import fetch_missing_data_fill_database
import influxdb as db
from influxdb.exceptions import InfluxDBClientError

prefix = "frx"


class Binary(MarketPair):

    BinaryRouterNo = parse_to_integer("BinaryRouter")

    """ prefix is appended to actual market pair because we only want
    to subscribe/fetch data with that prefix attached to get the right values
    """
    def __init__(self, pair, sub_port=None):
        super().__init__(
            pair=prefix + pair,
            router_port=self.BinaryRouterNo, sub_port=sub_port)

        self.database_name = pair

        self.client = db.DataFrameClient(
            host='localhost', port=INFLUXDB_PORT,
            database=self.database_name
        )


    def init(self):
        try:
            self.M10 = self.initials()[-10000:]
        except TypeError:
            print("None received..... class does not need to run....")

    @staticmethod
    def populate_history_schema(start, end, market, style):

        market_history = {
            "ticks_history": market,
            "end": f"{end}",
            "start": start,
            "style": style,
            "adjust_start_time": 1
        }

        return market_history

    def initials(self):

        # Reason for replacing the prefix is because I want this class and
        # MetaTrader class to make use of the same database for querying
        # Market value of same pair...

        _now = pd.Timestamp.utcnow()

        try:
            _M1 = self.client.query(
                f'select * from {self.database_name}'
            )[f'{self.database_name}']

            # DONT REMOVE THIS BLOCK NO MATTER HOW SMART YOU ARE....
            weekends = ['Friday', 'Saturday', 'Sunday']
            if _now.day_name() in weekends:
                print(
                    "Weekend has arrived can't run your class anymore...")
                self.shutdown_sockets()
                return None

            # YOUR ORIGINAL DATABASE GETS REPLACED IF REMOVED....

            _loop_frame = fetch_missing_data_fill_database(
                start=int(_M1.index[-1].timestamp()),
                end=int(_now.timestamp())
            )

            _M1 = _M1.append(_loop_frame).sort_index(axis=0)
            
            return _M1[['open', 'high', 'low', 'close']]

        except InfluxDBClientError:
            print(
                'Database error, >>>>> \
                Creating new database \nFetching Data from sources \
                as replacement'
            )

            init = pd.DataFrame()

            func_list = [
                self.get_history_histdata,
                self.get_history_binary_api,
                # self.get_history_metatrader
            ]

            for function in func_list:
                frame = function()
                if frame not None:
                    init = init.append(frame)
                    self.client.create_database(
                        f'{self.database_name}')
                    self.client.write_points(
                        _M1, f'{self.database_name}', protocol='json')
                    return init

            if len(init) == 0:
                self.shutdown_sockets()
                raise Exception(
                    "Frame is still zero after trying all functions"
                )


        except KeyError:
            self.shutdown_sockets()
            raise KeyError(
                "Database was not correctly implemented...., check web conn")

        except Exception:
            self.shutdown_sockets()
            raise Exception()
