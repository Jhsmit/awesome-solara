import time
import numpy as np


def some_task(param=3) -> int:
    time.sleep(np.random.randint(2, 4) / 10)
    return param * 2
