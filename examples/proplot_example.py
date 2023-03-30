import solara
from typing import cast, Optional
from pathlib import Path

# monkey patch server.patch
from solara.server.patch import FakeIPython
FakeIPython.magic = lambda *args: None

import proplot as pplt
pplt.switch_backend('agg')
from matplotlib.figure import Figure

@solara.component
def Proplot():
    fig, ax = pplt.subplots()

    ax.plot([1, 2, 3], [1, 4, 9])
    return solara.FigureMatplotlib(fig)


@solara.component
def Matplotlib():
    # do this instead of plt.figure()
    fig = Figure()
    ax = fig.subplots()
    ax.plot([1, 2, 3], [1, 4, 9])
    with solara.Card() as main:
        solara.FigureMatplotlib(fig)

    return main

@solara.component
def Page():
    with solara.Row():
        Proplot()
        Matplotlib()