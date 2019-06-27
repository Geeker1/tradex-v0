
# import numpy as np



class Strategy1:

	"""This class implements the basic strategy of SMA and MACD oscillators"""
    
    def __init__(self,other):
        
        self.market = other


    def loop(self):
    	""" This code is called for each timeframe and does the implementation"""
        pass

    def handle_binary(self):
		"""
		 This function is only called if the class initiates binary options 
		 instead of forex"""
        pass

    def handle_forex(self):
    	""" This method is only called when forex is initiated instead of binary options"""
        pass

    def algorithm(self):
    	""" This method implements the algorithm to handle how the class deals with data"""
        pass