from typing import Callable, Any, Optional

import solara


@solara.component
def FigurePlotly(
    fig,
    on_selection: Callable[[Any], None] = None,
    on_deselect: Callable[[Any], None] = None,
    on_click: Callable[[Any], None] = None,
    on_hover: Callable[[Any], None] = None,
    on_unhover: Callable[[Any], None] = None,
    update: Optional[dict] = None,
    dependencies=None,
):
    from plotly.graph_objs._figurewidget import FigureWidget

    def on_points_callback(data):
        if data:
            event_type = data["event_type"]
            if event_type == "plotly_click":
                if on_click:
                    on_click(data)
            elif event_type == "plotly_hover":
                if on_hover:
                    on_hover(data)
            elif event_type == "plotly_unhover":
                if on_unhover:
                    on_unhover(data)
            elif event_type == "plotly_selected":
                if on_selection:
                    on_selection(data)
            elif event_type == "plotly_deselect":
                if on_deselect:
                    on_deselect(data)

    fig_element = FigureWidget.element(on__js2py_pointsCallback=on_points_callback)

    def update_data():
        fig_widget: FigureWidget = solara.get_widget(fig_element)
        fig_widget.layout = fig.layout

        length = len(fig_widget.data)
        fig_widget.add_traces(fig.data)
        data = list(fig_widget.data)
        fig_widget.data = data[length:]

    solara.use_effect(update_data, dependencies or fig)

    # use event?
    def _update():
        if update:
            fig_widget: FigureWidget = solara.get_widget(fig_element)
            fig_widget.update(update)

    if update is not None:
        solara.use_effect(_update, [update])

    return fig_element

