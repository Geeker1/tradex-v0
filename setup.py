from distutils.core import setup
from Cython.Build import cythonize


setup(name='tradex',
      packages=[
        "tradex",
        "tradex.engine",
        "tradex.backtest",
        "tradex.patterns",
        "tradex.strategy",
        "tradex.market"
      ],
      ext_modules=cythonize("**/*.pyx")
      )
