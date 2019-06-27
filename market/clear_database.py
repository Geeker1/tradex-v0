



import sys
import os

from influxdb import DataFrameClient
from tradex.config import MARKET_PAIRS



def main(pair,all_=None):
	df = DataFrameClient(host='localhost',port=8086)
	database = df.get_list_database()

	lis = [i for x in database for i in x.values() if i in MARKET_PAIRS]

	if all_:
		for x in lis:
			df.drop_database(x)
		return 'Finished'

	elif pair in lis:
		df.drop_database(pair)
		return
	


if __name__ == '__main__':
	leno = sys.argv[1] if sys.argv[1] else None
	all_ = sys.argv[2] if len(sys.argv) > 2 else None
	main(leno,all_)