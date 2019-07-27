import os
import pandas as pd


def parse_to_integer(value):
    try:
        new = os.getenv(value)
        if new is None:
            raise EnvironmentError("Could not get the required key.....")
        conv_int = int(new)
        return conv_int
    except ValueError:
        return new
    raise Exception("Function is never to reach this block....")
