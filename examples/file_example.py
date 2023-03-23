"""
Upload one or multiple .csv files, load and combine in a single pandas DataFrame, and display the data.

"""
from typing import List

import solara
from awesome_solara.components.file_input import FileInput, FileInfo
import pandas as pd


@solara.component
def Page():
    df, set_df = solara.use_state(pd.DataFrame())

    def on_file(file_info: List[FileInfo]):
        if file_info:
            dfs = [pd.read_csv(f["file_obj"]) for f in file_info]
            set_df(pd.concat(dfs))

        # file info is an empty list
        else:
            set_df(pd.DataFrame())

    file_upload = FileInput(accept=".csv", on_file=on_file, lazy=True, multiple=True)
    dataframe = solara.DataFrame(df)
