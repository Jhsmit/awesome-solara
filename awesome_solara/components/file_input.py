"""
Reactive FileInput widget inspired by the solara FileDrop widget.
Currently hardcoded to be limited to one file.

"""


import threading
import typing
from typing import cast, Optional, Callable

import solara
import solara.hooks as hooks
from solara.components.file_drop import FileInfo
from ipyvuetify.extra import FileInput as ExtraFileInput


@solara.component
def FileInput(
    label="Drop file here",
    on_total_progress: Optional[Callable[[float], None]] = None,
    on_file: Optional[Callable[[FileInfo], None]] = None,
    accept="",
    lazy: bool = True,
    **kwargs
):
    """ """
    file_info, set_file_info = solara.use_state(None)
    wired_files, set_wired_files = solara.use_state(cast(Optional[typing.List[FileInfo]], None))

    file_input = ExtraFileInput.element(label=label, on_total_progress=on_total_progress, on_file_info=set_file_info, accept=accept, multiple=False, **kwargs)  # type: ignore

    def wire_files():
        if not file_info:
            return

        real = cast(ExtraFileInput, solara.get_widget(file_input))

        # workaround for @observe being cleared
        real.version += 1
        real.reset_stats()

        set_wired_files(cast(typing.List[FileInfo], real.get_files()))

    solara.use_effect(wire_files, [file_info])

    def handle_file(cancel: threading.Event):
        if not wired_files:
            return
        if on_file:
            if not lazy:
                wired_files[0]["data"] = wired_files[0]["file_obj"].read()
            else:
                wired_files[0]["data"] = None
            on_file(wired_files[0])

    result: solara.Result = hooks.use_thread(handle_file, [wired_files])
    if result.error:
        raise result.error

    return file_input
