import tensorflow as tf
import sys
import pandas as pd
import numpy as np


def available_versions():
    print(f"Tensorflow Version: {tf.__version__}")
    print(f"Pandas Version: {pd.__version__}")
    print(f"Numpy Version: {np.__version__}")
    print(f"System Version: {sys.version}")
