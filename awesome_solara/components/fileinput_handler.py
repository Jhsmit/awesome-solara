import threading

import reacton.ipyvuetify as rv
import solara
from ipyvuetify.extra import FileInput as ExtraFileInput
from typing import cast, Optional, Callable, TypedDict, List
from solara.components.file_drop import FileInfo

import pandas as pd
from io import BytesIO

import solara.hooks as hooks


@solara.component
def FileInput(label: str ="",
    on_total_progress: Optional[Callable[[float], None]] = None,
    on_file: Optional[Callable[[List[FileInfo]], None]] = None,
    accept: str = "",
    multiple: bool = True,
    lazy: bool = True, **kwargs):

    file_info, set_file_info = solara.use_state(cast(Optional[List[FileInfo]], None))

    f_input = ExtraFileInput.element(label=label, on_total_progress=on_total_progress, accept=accept, multiple=multiple, **kwargs) # type: ignore

    #from: https://maartenbreddels.medium.com/advance-your-ipywidget-app-development-with-reacton-6734a5607d69
    def attach_handler():
        widget = solara.get_widget(f_input)

        def on_change(event):
            if event.name == 'file_info':
                set_file_info(event.owner.get_files())

        def cleanup():
            widget.unobserve(on_change, names='file_info')

        widget.observe(on_change, names="file_info")

        return cleanup

    solara.use_effect(attach_handler)

    def handle_file(cancel: threading.Event):
        if not file_info:
            on_file([])
        elif on_file:
            if lazy:
                for f_info in file_info:
                    f_info["data"] = None
            else:
                for f_info in file_info:
                    f_info["data"] = f_info["file_obj"].read()

            on_file(file_info)


    # why do we need threaded? because of asyncio.run() in file_obj  ?
    result: solara.Result = hooks.use_thread(handle_file, [file_info])

    return f_input

