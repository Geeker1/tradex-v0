

import sys

from influxdb import DataFrameClient
from tradex.config import MARKET_PAIRS


def main(pair=None, logic=None):
    df = DataFrameClient(host='localhost', port=8086)
    database = df.get_list_database()

    lis = [i for x in database for i in x.values() if i in MARKET_PAIRS]

    if logic:
        for x in lis:
            df.drop_database(x)
        return 'Finished'

    elif pair in lis:
        df.drop_database(pair)
        return


if __name__ == '__main__':
    truth = sys.argv[1] if sys.argv[1] else None
    logic = sys.argv[2] if len(sys.argv) > 2 else None
    main(truth, logic)
