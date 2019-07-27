
################# REGULAR PYTHON IMPORTS ##################
import pickle
import os


################# LIBRARY IMPORTS ##################

import zmq
import pandas as pd
import influxdb as db
import numpy as np

################# Object IMPORTS ##################

from tradex.market.fetch_history_hst import parse_hst
from influxdb.exceptions import InfluxDBClientError
from zmq.error import ContextTerminated

from tradex.config import MT4_PATH, M_PUSH_PORTS,\
    M_SUB_PORT


class MarketPair:

    ##############  NOTE: DO NOT! INHERIT FROM BASE CLASS DIRECTLY.... ########

    def __init__(
        self, pair, string_delimiter=';',
            router_port=None, sub_port=None):

        self.sub_port = sub_port
        self.router_port = router_port

        """
        This is class is base class of Market Pairs

        [INIT VALUES]

        1. pair :== This is the name of market pair and it
        is passed as string to init function

        2. port :== This is the port that market pair runs on and
        should be unique to the specific market pair
        so as not to have more than one pair running in the system...

        """
        try:
            self._push_port = M_PUSH_PORTS[pair]
            self.string_delimiter = string_delimiter

            self.context = zmq.Context()
            # Create the push and pull sockets
            self.push = self.context.socket(zmq.PUSH)
            self.pull_socket = self.context.socket(zmq.PULL)

            # Bind on pull, connect on push
            self.push.bind(f'tcp://*:{self._push_port}')
            self.pull_socket.connect(f'tcp://localhost:{self._push_port}')

            self.pair_name = pair

            self.df_tick = pd.DataFrame(
                {}, index=pd.to_datetime([]), columns=['Bid', 'Ask']
            )
        except Exception:
            print("Error.....")
            self.shutdown_sockets()
            raise Exception

    @staticmethod
    def fill_missing_indexes_values(frame):
        date_range = pd.date_range(frame.index[0], frame.index[-1], freq='1T')
        for date in date_range:
            if date not in frame.index:
                ser = pd.Series(
                    np.array([np.NAN, np.NAN, np.NAN, np.NAN]),
                    index=['open', 'high', 'low', 'close'],
                    name=date, dtype=np.float64)
                frame = frame.append(ser)
        return frame.sort_index(axis=0)

    @staticmethod
    def resample_frame(time_interval, frame):
        """
                Returns DataFrame containing resampled data

                [NOTE] : This method depends solely on the ["self.M1"]
                attribute to be a DataFrame containing correct
                time values for it to work
                Anything short of that and it does not work,
                so the self.M1 must be a DataFrame
                with uniform values for it to work....
        """
        index = ['open', 'high', 'low', 'close']

        def kl(x, *args):

            # Check for missing/NAN values in resampled data
            # and return NAN series if any

            if x['open'].isna().any():  # Keep track of this potential bug
                return pd.Series(
                    np.array([np.NAN, np.NAN, np.NAN, np.NAN]),
                    index=index)

            init = x['open'][0]
            last = x['close'][-1]
            new_max = x[['high', 'low']].max().max()
            new_min = x[['high', 'low']].min().min()

            if (last - init) >= 0:
                high = new_max
                low = new_min
            elif (last - init) < 0:
                high = new_min
                low = new_max

            return pd.Series([init, high, low, last], index=index)

            raise(Exception('Na Mad Error wey dey here so....'))

        return frame.resample(time_interval).apply(kl)

    def shutdown_sockets(self):
        self.pull_socket.close()
        self.push.close()
        self.context.term()

    """

    #####################################################################

            The start function defined by start();
            It connects MARKETCLIENT with the METATRADER 4 connnector;
            It parses data received and sends it on a push socket to ==
            thread based function that analyses data received and
            sends to strategy manager for signal...

    #####################################################################


    """

    def start(self):

        router = self.router_port
        sub = M_SUB_PORT if self.sub_port is None else self.sub_port

        _context = zmq.Context()
        req_socket = self.context.socket(zmq.REQ)
        req_socket.connect(f"tcp://localhost:{router}")

        req_socket.send_string("EURUSD")
        print("Sent data to router socket....")
        msg = req_socket.recv_string()
        if msg == "ok":
            print(
                "Ok message received....closing \
                socket and waiting for data"
            )
        req_socket.close()

        _subscribe = _context.socket(zmq.SUB)
        _subscribe.connect(
            f'tcp://localhost:{sub}'
        )

        _subscribe.setsockopt_string(zmq.SUBSCRIBE, self.pair_name)

        print('\n', '\t\t ##### receiving data and sending #####')

        while True:
            try:
                msg = _subscribe.recv_string(zmq.DONTWAIT)
                if msg != '':
                    print(msg.split(" "))
                    _symbol, _data = msg.split(" ")
                    if _data == 'kill':
                        print('Received killing code... Killing now')
                        self.push.send(b'kill')
                        self.push.close()
                        _subscribe.close()
                        _context.term()
                        break
                    _bid, _ask, _timestamp = _data.split(self.string_delimiter)

                    self.df_tick = self.df_tick.append(
                        pd.DataFrame({
                            'Bid': [float(_bid)], 'Ask': [float(_ask)]
                        },
                            index=pd.to_datetime(
                                [pd.Timestamp.fromtimestamp(
                                    float(_timestamp))])
                        ))

                    print('Received message .... ', msg)

                    last_last_val = self.df_tick.index[-2]
                    last_val = self.df_tick.index[-1]

                    if last_val.minute - last_last_val.minute == 1:
                        range_1 = str(
                            last_last_val.replace(
                                second=0, microsecond=0))

                        range_2 = str(last_last_val)

                        dump_data = pickle.dumps(
                            self.df_tick.loc[range_1:range_2]['Bid'].resample(
                                '1Min').ohlc()
                        )

                        self.push.send(dump_data)

            except zmq.error.Again:
                pass
            except ValueError:
                print("Value Error..... Bug Found...Test code!!!")
                pass
            except IndexError:
                continue
            except KeyboardInterrupt:
                _subscribe.close()
                _context.term()


class MarketParser(MarketPair):

    def __init__(self,pair,router_port,sub_port):
        super().__init__(pair=pair,
                         router_port=router_port, sub_port=sub_port)

        self.database_name = pair

        self.client = db.DataFrameClient(
            host='localhost', port=8086, database=self.database_name)

        """ Query DataBase for values,
        if No Database get raw or remote data"""

        self.init()

    def init(self):
        self.M1 = self.initials()[-10000:]
        self.M1 = MarketParser.fill_missing_indexes_values(self.M1)
        self.M5 = MarketParser.resample_frame('5T', self.M1)
        self.M15 = MarketParser.resample_frame('15T', self.M1)
        self.H1 = MarketParser.resample_frame('1H', self.M1)
        self.H4 = MarketParser.resample_frame('4H', self.M1)
        self.D1 = MarketParser.resample_frame('1D', self.M1)

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

            # This error occurs because a database was not found...
            # In case of any other influx error check code well
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
                if frame is not None:
                    init = init.append(frame)
                    self.client.create_database(
                        f'{self.database_name}')
                    self.client.write_points(
                        _M1, f'{self.database_name}', protocol='json')
                    return init

            if len(init) == 0:
                raise Exception(
                    "Frame is still zero after trying all functions"
                )

        except KeyError:
            self.shutdown_sockets()
            raise KeyError(
                "Database was not correctly implemented \
                ...., check/ping websocket conn")

        except Exception:
            self.shutdown_sockets()
            raise Exception

    # def get_history_metatrader(self):
    #     now = pd.Timestamp.utcnow()
    #     prev = now - pd.Timedelta(weeks=12)
    #     now, prev = int(now.timestamp()), int(prev.timestamp())
    #     try:
    #         frame = self.fetch_history_parse(range_1=prev, range_2=now)
    #         return frame
    #     except Exception:
    #         pass

    def get_history_binary_api(self):
        now = pd.Timestamp.utcnow()
        prev = now - pd.Timedelta(weeks=12)
        now, prev = int(now.timestamp()), int(prev.timestamp())

        try:
            frame = fetch_missing_data_fill_database(
                'EURUSD', start=now, end=prev)
            return frame
        except Exception:
            pass

    def get_history_histdata(self):
        now = pd.Timestamp.utcnow()
        prev = now - pd.Timedelta(weeks=12)
        date_range = pd.date_range(start=prev,end=now,freq='1T')
        months = []

        for stamp in date_range:
            if stamp.month not in months:
                months.append(stamp.month)
        
        try:
            frame = fetch_hist_data('EURUSD',now.year,months)
            return frame
        except Exception as e:
            pass






