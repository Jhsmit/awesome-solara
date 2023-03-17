"""
Two side-by-side plotly figures, with sliders to control the frequency of the sine wave.
Lef hand side redraws the figure upon slider change, right hand side updates the data.


"""
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from awesome_solara.components.misc import FigurePlotly as FigurePlotlyUpdate

import solara

x = np.linspace(0, 2, 1000)

FREQ_INITIAL = 2.0
FREQ_MIN = 0.
FREQ_MAX = 20


title = "Interactive sine wave"


def make_figure():
    fig = go.Figure(layout=go.Layout(title=title))
    fig.add_trace(go.Scatter(x=x, y=np.sin(x * 2), name='sine wave'))

    return fig


@solara.component
def PlotlyRedraw():
    freq, set_freq = solara.use_state(FREQ_INITIAL)
    y = np.sin(x * freq)

    with solara.VBox() as main:
        solara.FloatSlider("Frequency", value=freq, on_value=set_freq, min=FREQ_MIN, max=FREQ_MAX)
        fig = px.line(x=x, y=y, title=title)

        solara.FigurePlotly(fig, dependencies=[freq])
    return main


@solara.component
def PlotlyUpdate():

    fig = solara.use_memo(make_figure, [])
    freq, set_freq = solara.use_state(FREQ_INITIAL)
    update, set_update = solara.use_state({})

    #
    def new_data(value):
        y = np.sin(x * value)
        set_update({'data': [{'y': y}]})
        set_freq(value)

    with solara.VBox() as main:
        solara.FloatSlider("Frequency", value=freq, on_value=new_data, min=FREQ_MIN, max=FREQ_MAX)

        FigurePlotlyUpdate(fig, update=update)
    return main


@solara.component
def Page():

    option, set_option = solara.use_state("redraw")

    with solara.VBox() as main:
        with solara.Card("Plotly"):
            with solara.ToggleButtonsSingle(option, on_value=set_option):
                solara.Button("redraw")
                solara.Button("update")
            if option == "redraw":
                PlotlyRedraw()
            elif option == "update":
                PlotlyUpdate()
