import solara
from bokeh.io import output_notebook
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
import ipywidgets as ipw
from jupyter_bokeh import BokehModel
import numpy as np


rng = np.random.default_rng()
# prepare some data
data = {'x_values': [1, 2, 3, 4, 5],
        'y_values': rng.random(5)}
# create ColumnDataSource based on dict
source = ColumnDataSource(data=data)

# create a new plot with a title and axis labels
p = figure(title="Simple line example", x_axis_label='x', y_axis_label='y')
# add a line renderer with legend and line thickness to the plot
renderer = p.line(x='x_values', y='y_values', source=source, legend_label="Temp.", line_width=2)

w = ipw.VBox([
    BokehModel(p),

])

@solara.component
def Page():
    # output_notebook() # uncomment, solara run, comment, solara autoreload, ???, profit
    def on_click():
        print('new data')
        data = {'x_values': [1, 2, 3, 4, 5],
                'y_values': rng.random(5)}
        source.data = data

    with solara.Card("Bokeh"):
        solara.Button(label="Click me", on_click=on_click)
        solara.display(w)