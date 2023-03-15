import pandas as pd
import numpy as np
import string
from pathlib import Path

#%%

nrows = [10, 15, 20]
for nr in nrows:
    data = {
        "a": np.random.rand(nr),
        "b": np.random.rand(nr),
        "cat": np.random.choice(list(string.ascii_lowercase), nr),
    }
    df = pd.DataFrame(data)
    df.to_csv(f"data_len_{nr}.csv")

#%%
