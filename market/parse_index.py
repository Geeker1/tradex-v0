import time
import struct
import pandas as pd
import pickle


frame = {
    'time': [],
        'open': [],
        'high': [],
        'low': [],
        'close': [],
        'volume': [],
        'spread': [],
        'real_volume': [],
}

year_range = [2014, 2015, 2016, 2017, 2018, 2019, 2020]


def parse_hst(file, year_val=None, range1=None, range2=None):
    global year_range, frame

    header = 148
    body = 60

    index_f = header
    index_last = 208

    statement = 'year >= int(year_val)'
    if range1 or range2:
        statement = 'range1 <= parsed_data[0] <= range2'

    with open(file, 'rb') as f:
        data = f.read()

    while True:
        try:
            b_data = data[index_f:index_last]
            parsed_data = struct.unpack('<Q4dqiq', b_data)
            date = time.gmtime(parsed_data[0])
            year = date.tm_year
            if (eval(statement)):
                frame['time'].append(
                    pd.Timestamp.fromtimestamp(parsed_data[0]))
                frame['open'].append(parsed_data[1])
                frame['high'].append(parsed_data[2])
                frame['low'].append(parsed_data[3])
                frame['close'].append(parsed_data[4])
                frame['volume'].append(parsed_data[5])
                frame['spread'].append(parsed_data[6])
                frame['real_volume'].append(parsed_data[7])
        except OSError:
            pass
        except struct.error:
            break
        except OverflowError:
            pass
        except KeyboardInterrupt:
            break

        index_f += 60
        index_last += 60

    df = pd.DataFrame(frame)
    df.index = pd.to_datetime(df['time'])
    df = df.sort_index(axis=0)

    # print('\n','\t\t','#'*10,'Pandas DataFrame','#'*10,'\n')

    return df[['open', 'high', 'low', 'close']]


if __name__ == '__main__':
    file = sys.argv[1] if len(sys.argv) > 1 else '2018.hcc'
    year = sys.argv[2] if len(sys.argv) > 2 else 2018
    parse_hst(file, year)
