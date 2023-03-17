import solara.components.echarts
from pyecharts.charts import Bar, Line
import pyecharts.options as opts

import json

#%%

bar = Bar()
bar.add_xaxis(["shirts", "cardigans", "chiffons", "trousers", "heels", "socks"])
bar.add_yaxis("Merchant A", [5, 20, 36, 10, 75, 90])

#%%
x_data = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
y_data = [820, 932, 901, 934, 1290, 1330, 1320]

line = (
    Line()
    .set_global_opts(
        tooltip_opts=opts.TooltipOpts(is_show=False),
        xaxis_opts=opts.AxisOpts(type_="category"),
        yaxis_opts=opts.AxisOpts(
            type_="value",
            axistick_opts=opts.AxisTickOpts(is_show=True),
            splitline_opts=opts.SplitLineOpts(is_show=True),
        ),
    )
    .add_xaxis(xaxis_data=x_data)
    .add_yaxis(
        series_name="",
        y_axis=y_data,
        symbol="emptyCircle",
        is_symbol_show=True,
        label_opts=opts.LabelOpts(is_show=False),
    )
)

#%%
options = {}
options["bars"] = json.loads(bar.dump_options())
options["line"] = json.loads(line.dump_options())

#%%

@solara.component
def Page():
    option, set_option = solara.use_state("bars")
    click_data, set_click_data = solara.use_state(None)
    mouseover_data, set_mouseover_data = solara.use_state(None)
    mouseout_data, set_mouseout_data = solara.use_state(None)

    with solara.VBox() as main:
        with solara.Card("Echarts"):
            with solara.ToggleButtonsSingle("bars", on_value=set_option):
                solara.Button("bars")
                solara.Button("line")
            solara.FigureEcharts(
                option=options[option],
                on_click=set_click_data,
                on_mouseover=set_mouseover_data,
                on_mouseout=set_mouseout_data,
            )
        with solara.Card("Event data"):
            solara.Markdown(f"**Click data**: {click_data}")
            solara.Markdown(f"**Mouseover data**: {mouseover_data}")
            solara.Markdown(f"**Mouseout data**: {mouseout_data}")

    return main
