

import pytest

from tradex.market.clear_database import main

# class Hello(object):
# 	def __init__(self, arg=None):
# 		self.arg = arg
		

# def func(x):
# 	return x + 1

# def f():
# 	raise SystemExit(1)

# def test_exit():
# 	with pytest.raises(SystemExit):
# 		f()


# def test_answer():
# 	assert func(4) == 5

# def test_rot():
# 	assert func(2) == 5


#################### USING FIXTURES ######################


# @pytest.fixture
# def connection():
# 	ad = Hello('EURUSD')
# 	yield ad
# 	del ad

# def test_ehlo(connection):

# 	assert connection.arg == 'Finished'


""" NOTE if you want to use fixtures across other function in same module,
you can change scope to module and save code in conftest.py 

Pytest automaticallly detects it...

E.g 

@pytest.fixture(scope="module")
def connection():
	from tradex.market.clear_database import main
	return main('EURUSD',True)


### Doing like this 

"""