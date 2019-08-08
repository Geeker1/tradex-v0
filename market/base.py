
################# REGULAR PYTHON IMPORTS ##################
import pickle

################# LIBRARY IMPORTS ##################

import zmq
import pandas as pd
import numpy as np

################# Object IMPORTS ##################

# from zmq.error import ContextTerminated

from tradex.config import M_PUSH_PORTS, M_SUB_PORT


class MarketPair:

    # NOTE: DO NOT INHERIT FROM BASE CLASS DIRECTLY !!!!....

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

        3. router_port :== This is the router no, the class connects
        to and sends confirmation message to, before starting sub socket

        4. sub_port :== This is the subscription port no that
        the class's sub socket connects to fr receiving subscription
        messages

        """
        try:
            # Define push port and delimiter
            self._push_port = M_PUSH_PORTS[pair]
            self.string_delimiter = string_delimiter

            # Create the context for push and pull sockets...
            self.context = zmq.Context()

            # Create the push and pull sockets
            self.push = self.context.socket(zmq.PUSH)
            self.pull_socket = self.context.socket(zmq.PULL)

            # Bind on pull, connect on push
            self.push.bind(f'tcp://*:{self._push_port}')
            self.pull_socket.connect(f'tcp://localhost:{self._push_port}')

            # set market pair name, note this value is used in
            # subscribing for messages sent on sub socket....
            self.pair_name = pair

            # initial tick frame set to empty values,
            # this value changes every second/nth-second
            self.df_tick = pd.DataFrame(
                {}, index=pd.to_datetime([]), columns=['Bid', 'Ask']
            )
        except Exception:
            self.shutdown_sockets()
            raise Exception(
                "Error while trying to setup base class values")

    @staticmethod
    def fill_missing_indexes_values(frame):
        # This class takes a dataframe, creates a date range that
        # spans through the first and last index values of dataframe
        # with a freq of 1T, loops via date range and for each date value
        # verifies if not in frame's index, creates a nan series and
        # appends to original frame, after loooping returns new frame

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
            # and return NAN series if any, else it gets
            # captured data and computes open,high,low,close values
            # creates new series containing new values and returns it

            if x['open'].isna().any():  # Keep track of this potential bug
                return pd.Series(
                    np.array([np.NAN, np.NAN, np.NAN, np.NAN]),
                    index=index)

            init = x['open'][0]
            last = x['close'][-1]
            new_max = x[['high', 'low']].max().max()
            new_min = x[['high', 'low']].min().min()

            return pd.Series([init, new_max, new_min, last], index=index)

            # Not hoping for this error though but just in case...
            raise(Exception('Na Mad Error wey dey here so....'))

        return frame.resample(time_interval).apply(kl)

    def shutdown_sockets(self):
        # closes bound push and pull sockets
        # then closes context
        self.pull_socket.close()
        self.push.close()
        self.context.term()

    """

    #####################################################################

        The start function defined by start();
        It connects MARKETCLIENT with the router connnector, through
        router port no
        The main aim of this class is to keep on appending tick frames
        till the tick crosses minute mark then computes tick data to be
        resampled, pickle dumps it and sends it through push socket

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
