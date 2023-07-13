# %%
# from __future__ import annotations
from dataclasses import dataclass, field
from functools import reduce
import itertools
from operator import and_
from typing import Callable, Optional, Type, TypeVar, Union, cast
import uuid
import polars as pl
import pandas as pd
import numpy as np
import solara
import plotly.graph_objs as go

from solara.alias import rv

T = TypeVar("T")


def not_none(*args: Optional[T]) -> Optional[T]:
    """Returns the first `not None` argument"""
    for a in args:
        if a is not None:
            return a


def distribute_samples(N: int, p: int) -> np.ndarray:
    # copilot generated
    # generate p-1 random numbers between 0 and N
    splits = np.sort(np.random.choice(N, p - 1, replace=False))
    # calculate the differences between the splits
    diffs = np.diff(np.concatenate(([0], splits, [N])))
    return diffs


def rng_normal(size: int) -> np.ndarray:
    return np.random.normal(
        loc=np.random.uniform(0, 10), scale=np.random.uniform(0.5, 1.5), size=size
    )


def generate_column_data(n_pops: int, n_samples: int) -> np.ndarray:
    """Generate random data for a given number of populations and samples.

    Args:
        n_pops (int): Number of populations.
        n_samples (int): Number of samples.

    Returns:
        np.ndarray: Random data.
    """

    # split the total number of samples randomly into the populations
    pop_sizes = distribute_samples(n_samples, n_pops)

    data = [rng_normal(size) for size in pop_sizes]

    arr = np.concatenate(data)
    np.random.shuffle(arr)
    return arr


# %%
@dataclass
class FilterItem:
    name: str
    min: Optional[float] = field(default=None)
    max: Optional[float] = field(default=None)

    def as_expr(self) -> list[pl.Expr]:
        expr = []
        if self.min is not None:
            expr.append(pl.col(self.name) >= self.min)
        if self.max is not None:
            expr.append(pl.col(self.name) <= self.max)
        return expr


# %%
N = 1000
NAMES = list("abcdef")
DATAFRAME = pl.DataFrame({k: generate_column_data(np.random.randint(2, 5), N) for k in NAMES})
DEFAULT_FILTERS = [
    FilterItem("a", min=2, max=8),
    FilterItem("b", min=1),
]
# %%

N_STEP = 1000


def create_histogram(
    data, xbins, arange: tuple[float, float], xrange: tuple[Optional[float], Optional[float]]
) -> go.Figure:
    hist_trace = go.Histogram(x=data, xbins=xbins)

    layout = go.Layout(
        modebar_remove=[
            "lasso2d",
            "select2d",
            "zoom2d",
            "pan2d",
            "zoomIn2d",
            "zoomOut2d",
            "autoScale2d",
            "resetScale2d",
        ],
        xaxis=dict(
            range=arange,
            type="linear",
        ),
        yaxis=dict(
            type="linear",
        ),
    )

    # Create a figure with the histogram trace and layout
    fig = go.Figure(data=[hist_trace], layout=layout)
    fig.update_layout(dragmode=False, selectdirection="h")

    fig.add_vrect(
        editable=False,
        x0=arange[0],
        x1=xrange[0] if xrange[0] is not None else arange[0],
        fillcolor="gray",
        opacity=0.5,
        layer="above",
        line_width=0,
    )
    fig.add_vrect(
        editable=False,
        x0=xrange[1] if xrange[1] is not None else arange[1],
        x1=arange[1],
        fillcolor="gray",
        opacity=0.5,
        layer="above",
        line_width=0,
    )

    return fig


@solara.component
def RangeInputField(
    label: str,
    value: Union[float, int],
    vtype: Union[Type[float], Type[int]],
    on_value: Optional[Callable[[Union[float, int, None]], None]] = None,
    vmin: Union[float, int, None] = None,
    vmax: Union[float, int, None] = None,
):
    """Input field for a float value with a range slider."""

    if vmin is not None and vmax is not None and vmin >= vmax:
        raise ValueError("vmin must be smaller than vmax")

    error, set_error = solara.use_state(False)
    message, set_message = solara.use_state("")

    def inputtext_cb(new_value: str):
        try:
            value = vtype(new_value)

        except ValueError:
            if vtype == int:
                set_message("Input must be an integer")
            else:
                set_message("Input must be a number")
            set_error(True)
            return
        if vmin is not None and value < vmin:
            set_message(f"Input must be >= {vmin}")
            set_error(True)
            return
        if vmax is not None and value > vmax:
            set_message(f"Input must be <= {vmax}")
            set_error(True)
            return
        set_error(False)
        set_message("")
        on_value(value)

    with solara.Row():
        solara.InputText(
            label=label,
            value=value,
            error=error,
            message=message,
            on_value=inputtext_cb,
        )
        solara.IconButton(icon_name="mdi-restore", on_click=lambda *args: on_value(vmin or vmax))


@solara.component
def FigurePlotlyShapes(
    fig: go.Figure,
    shapes: dict,
    dependencies=None,
):
    from plotly.graph_objs._figurewidget import FigureWidget

    fig_element = FigureWidget.element()

    def update_data():
        fig_widget: FigureWidget = solara.get_widget(fig_element)
        fig_widget.layout = fig.layout

        length = len(fig_widget.data)
        fig_widget.add_traces(fig.data)
        data = list(fig_widget.data)
        fig_widget.data = data[length:]

    def update_shapes():
        if shapes:
            fig_widget: FigureWidget = solara.get_widget(fig_element)
            fig_widget.update_shapes(**shapes)

    solara.use_effect(update_data, dependencies or fig)
    solara.use_effect(update_shapes, shapes)

    return fig_element


@solara.component
def EditFilterDialog(
    filter_item: solara.Reactive[FilterItem],
    data: np.ndarray,
    on_close: Callable[[], None],
):
    def bin_data():
        data_f = data[~np.isnan(data)]
        counts, binspace = np.histogram(data_f, bins="fd")
        xbins = {"start": binspace[0], "end": binspace[-1], "size": binspace[1] - binspace[0]}
        arange = 2 * binspace[0] - 0.05 * binspace[-1], 1.05 * binspace[-1] - binspace[0]

        return data_f, xbins, arange

    data_f, xbins, arange = solara.use_memo(bin_data, [])

    xr_default = (
        not_none(filter_item.value.min, arange[0]),
        not_none(filter_item.value.max, arange[1]),
    )

    xrange, set_xrange = solara.use_state(xr_default)
    shapes, set_shapes = solara.use_state({})

    def make_figure():
        return create_histogram(data_f, xbins, arange, xrange)

    fig = solara.use_memo(make_figure, [])

    show_slider, set_show_slider = solara.use_state(True)

    def update_xmin(value):
        set_xrange((value, xrange[1]))
        d = {"patch": dict(x0=arange[0], x1=value), "selector": 0}
        set_shapes(d)

    def update_xmax(value):
        set_xrange((xrange[0], value))
        d = {"patch": dict(x0=value, x1=arange[1]), "selector": 1}
        set_shapes(d)

    def on_slider(value: tuple[float, float]):
        if value[0] != xrange[0]:
            d = {"patch": dict(x0=arange[0], x1=value[0]), "selector": 0}
        elif value[1] != xrange[1]:
            d = {"patch": dict(x0=value[1], x1=arange[1]), "selector": 1}
        else:
            return
        set_shapes(d)
        set_xrange(value)

    with solara.Card(f"Filter: {filter_item.value.name}"):
        FigurePlotlyShapes(fig, shapes=shapes)
        step = (arange[1] - arange[0]) / N_STEP
        with solara.Row():
            with solara.Tooltip("Disable slider to prevent threshold value rounding."):
                rv.Switch(v_model=show_slider, on_v_model=set_show_slider)
            if show_slider:
                solara.SliderRangeFloat(
                    label="",
                    min=arange[0],
                    max=arange[1],
                    value=xrange,
                    step=step,
                    on_value=on_slider,
                )
        with solara.Row():
            RangeInputField(
                label="Min",
                value=xrange[0],
                vtype=float,
                on_value=update_xmin,
                vmin=arange[0],
            )
            RangeInputField(
                label="Max",
                value=xrange[1],
                vtype=float,
                on_value=update_xmax,
                vmax=arange[1],
            )

        def on_save():
            new_filter = FilterItem(
                filter_item.value.name,
                min=xrange[0],
                max=xrange[1],
            )
            filter_item.set(new_filter)
            on_close()

        with solara.CardActions():
            rv.Spacer()
            solara.Button("Save", icon_name="mdi-content-save", on_click=on_save)
            solara.Button("Close", icon_name="mdi-window-close", on_click=on_close)


@solara.component
def FilterListItem(
    filter_item: solara.Reactive[FilterItem], data: np.ndarray, on_delete: Callable[[], None]
):
    edit, set_edit = solara.use_state(False)
    with rv.ListItem():  # move to filterlistitem component
        rv.ListItemAvatar(children=[rv.Icon(children=["mdi-filter"])])
        rv.ListItemTitle(children=[filter_item.value.name])
        # TODO multi line
        rv.ListItemSubtitle(children=[f"{filter_item.value.min} - {filter_item.value.max}"])

        solara.IconButton(
            color="secondary",
            small=True,
            rounded=True,
            icon_name="mdi-delete",
            on_click=on_delete,
        )

        solara.IconButton(
            color="secondary",
            small=True,
            rounded=True,
            icon_name="mdi-pencil",
            on_click=lambda: set_edit(True),
        )

    with rv.Dialog(v_model=edit, max_width=750, on_v_model=set_edit):
        EditFilterDialog(
            filter_item,
            data,
            on_close=lambda: set_edit(False),
        ).key(uuid.uuid4().hex)


@solara.component
def Page():
    filters = solara.use_reactive(DEFAULT_FILTERS)
    new_filter_name, set_new_filter_name = solara.use_state(cast(str, None))

    def filter_dataframe() -> pl.DataFrame:
        f_exprs = list(itertools.chain(*(f.as_expr() for f in filters.value)))
        if f_exprs:
            return DATAFRAME.filter(reduce(and_, f_exprs))
        else:
            return DATAFRAME

    filtered_df = solara.use_memo(filter_dataframe, [filters.value])

    def add_filter():
        item = FilterItem(name=new_filter_name)
        new_filters = filters.value.copy()
        new_filters.append(item)
        filters.set(new_filters)

    with solara.Card(title="Filters"):
        with rv.List(dense=False):
            for idx, flt in enumerate(filters.value):

                def on_delete(idx=idx):
                    new_filters = filters.value.copy()
                    del new_filters[idx]
                    filters.set(new_filters)

                FilterListItem(
                    solara.lab.Ref(filters.fields[idx]),
                    DATAFRAME[flt.name].to_numpy().base,
                    on_delete,
                )

        solara.Select(
            label="Filter attribute",
            value=new_filter_name,
            values=[name for name in NAMES if name not in [f.name for f in filters.value]],
            on_value=set_new_filter_name,
        )
        solara.Button("Add filter", on_click=lambda: add_filter(), block=True)
        solara.Info("Number of rows: " + str(len(filtered_df)))

        # awaits https://github.com/widgetti/solara/pull/195 for direct polars support
        solara.DataFrame(
            pd.DataFrame({col: filtered_df[col].to_numpy().base for col in filtered_df.columns})
        )
