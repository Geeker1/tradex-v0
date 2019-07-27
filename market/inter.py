
################# REGULAR PYTHON IMPORTS ##################
import pickle
import os


################# LIBRARY IMPORTS ##################

import zmq
import pandas as pd
import influxdb as db

################# Object IMPORTS ##################
from tradex.market.base import MarketPair
from tradex.market.fetch_history_hst import parse_hst
from tradex.market.fetch_history_api import fetch_missing_data_fill_database
from tradex.market.fetch_history_data import fetch_hist_data
from influxdb.exceptions import InfluxDBClientError
from zmq.error import ContextTerminated

from tradex.config import MT4_PATH


class MarketParser(MarketPair):

    def __init__(self, pair, router_port=None, sub_port=None):
        super().__init__(
            pair=pair, router_port=router_port,
            sub_port=sub_port)

        if not pair.startswith("frx"):
            self.database_name = pair
        else:
            self.database_name = pair.replace('frx', '')

        # Sets the name of hst file name in case we need to fetch
        # from hst archive...
        self.pair_hst_file = self.database_name + '1.hst'

        # sets the client of market pair from where we would get
        # minute data
        self.client = db.DataFrameClient(
            host='localhost', port=8086, database=self.database_name)

    def init(self):
        try:
            self.M1 = self.initials()[-10000:]
            self.M1 = super().fill_missing_indexes_values(self.M1)
            self.M5 = super().resample_frame('5T', self.M1)
            self.M15 = super().resample_frame('15T', self.M1)
            self.H1 = super().resample_frame('1H', self.M1)
            self.H4 = super().resample_frame('4H', self.M1)
            self.D1 = super().resample_frame('1D', self.M1)
        except TypeError:
            print("None received..... class does not need to run....")

    def fetch_history_parse(self, year_val=None, range_1=None, range_2=None):
        """
            This method returns a dataframe containing parsed data from
            the imported parse_hst function and raises a FileNotFoundError
            if the path to the file does not exist....
        """

        _path = os.path.join(MT4_PATH, self.pair_hst_file)
        if os.path.exists(_path):
            return parse_hst(_path, year_val, range1=range_1, range2=range_2)

        self.shutdown_sockets()
        raise FileNotFoundError(
            '''The file was not found on this device, try changing paths...'''
        )

    def initials(self):

        _now = pd.Timestamp.now('UTC')

        try:
            _M1 = self.client.query(
                f'select * from {self.database_name}'
            )[f'{self.database_name}']

            # DONT REMOVE THIS BLOCK NO MATTER HOW SMART YOU ARE....
            # weekends = ['Friday', 'Saturday', 'Sunday']
            # if _now.day_name() in weekends:
            #     print(
            #         "Weekend has arrived can't run your class anymore...")
            #     self.shutdown_sockets()
            #     return None

            # YOUR ORIGINAL DATABASE GETS REPLACED IF REMOVED....

            _loop_frame = fetch_missing_data_fill_database(
                self.database_name,
                start=int(_M1.index[-1].timestamp()),
                end=int(_now.timestamp())
            )

            self.client.write_points(
                _loop_frame, f'{self.database_name}', protocol='json')

            _M1 = _M1.append(_loop_frame).sort_index(axis=0)

            return _M1[['open', 'high', 'low', 'close']]

        except InfluxDBClientError:

            # This error occurs because a database was not found...
            # In case of any other influx error well LOL !!!!!
            print(
                'Database error, >>>>> \
                Creating new database \nFetching Data from sources \
                as replacement'
            )

            init = pd.DataFrame()

            func_list = [
                self.get_history_histdata,
                self.get_history_binary_api,
                self.get_history_metatrader
            ]

            for function in func_list:
                try:
                    frame = function()
                    if frame is not None:
                        init = init.append(frame)
                        self.client.create_database(
                            f'{self.database_name}')
                        self.client.write_points(
                            init, f'{self.database_name}', protocol='json')
                        return init
                except Exception:
                    pass

            if len(init) == 0:
                raise Exception(
                    "Frame is still zero after trying all functions"
                )

        except KeyError:
            self.shutdown_sockets()
            self.client.drop_database(self.database_name)
            return self.initials()
            raise KeyError(
                "Database was not correctly implemented....,\
                maybe you created database and didn't write to it,\
                check/ping websocket conn"
            )

        except Exception:
            self.shutdown_sockets()
            raise Exception

    def get_history_metatrader(self):
        now = pd.Timestamp.utcnow()
        prev = now - pd.Timedelta(weeks=12)
        now, prev = int(now.timestamp()), int(prev.timestamp())
        try:
            frame = self.fetch_history_parse(range_1=prev, range_2=now)
            return frame
        except Exception:
            pass

    def get_history_binary_api(self):
        now = pd.Timestamp.utcnow()
        prev = now - pd.Timedelta(weeks=12)
        now, prev = int(now.timestamp()), int(prev.timestamp())

        try:
            frame = fetch_missing_data_fill_database(
                self.database_name, start=now, end=prev)
            return frame
        except Exception:
            pass

    def get_history_histdata(self):
        now = pd.Timestamp.utcnow()
        prev = now - pd.Timedelta(weeks=12)
        date_range = pd.date_range(start=prev, end=now, freq='1T')
        months = []

        for stamp in date_range:
            if stamp.month not in months:
                months.append(stamp.month)

        try:
            frame = fetch_hist_data('EURUSD', now.year, months)
            return frame
        except Exception:
            pass

    def validate_tick_crossing(self):
        """

        This method is called when the tick value in self.df_tick crosses the
        minute mark....
        It checks for all frames except M1 if their time mark has been passed,
        creates a data range and then resamples the
        1min data based on the range
        to that frame's time,and appends returned
        data to original

        """

        pivot_time = self.M1.index[-1]
        time_range = None

        for val in ['M5', 'M15']:
            if pivot_time.minute in time_range[val]:
                pass

        for valx in ['H1', 'H4']:
            if pivot_time.hour in time_range[valx] and pivot_time.minute == 0:
                pass

        for valx in ['D1']:
            if pivot_time.hour == 0 and pivot_time.minute == 0:
                pass
        pass

    """

    #####################################################################

            This is the main logic and would be responsible for receiving
            data and passing to strategy manager class

    #####################################################################


    """

    def main_logic(self):
        """

        The main logic method is the backbone of the whole code
        and is what actually sends
        our code to the strategy class for signal creation....
        It also has a kill option that kills the socket
        and everything in it, terminating the process.

        It receives data from pull socket when tick data crosses minute mark
        and tries to resample data if anyone has crossed its mark, then it
        calles the validate function that checks for strategy
        frame conditions set initially in Init function...and
        tries to call strategy class if anyone is met....

        """

        print('\n', '\t\t ##### Polling for data on pull socket #####')
        while True:
            try:
                msg = self.pull_socket.recv()
                if msg != '':
                    if msg == b'kill':
                        print('killing logic thread... Killing now')
                        self.shutdown_sockets()
                        raise ContextTerminated
                    frame = pickle.loads(msg)
                    self.M1 = self.M1.append(frame)
                    print(self.M1.iloc[-1])
                    # self.validate_tick_crossing()

            except zmq.error.Again:
                pass
            except ValueError:
                pass
            except KeyboardInterrupt:
                self.pull_socket.close()
                self.context.term()
            except ContextTerminated:
                break
