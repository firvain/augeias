import sys

import numpy as np
import pandas as pd
import tensorflow as tf


def available_versions():
    print(f"Tensorflow Version: {tf.__version__}")
    print(f"Pandas Version: {pd.__version__}")
    print(f"Numpy Version: {np.__version__}")
    print(f"System Version: {sys.version}")
