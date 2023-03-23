"""
Reactive FileInput widget inspired by the solara FileDrop widget.
Currently hardcoded to be limited to one file.

"""


import threading
from typing import cast, Optional, Callable, List

import solara
import solara.hooks as hooks
from solara.components.file_drop import FileInfo
from ipyvuetify.extra import FileInput as ExtraFileInput


@solara.component
def FileInput(
    label: str = "",
    on_total_progress: Optional[Callable[[float], None]] = None,
    on_file: Optional[Callable[[List[FileInfo]], None]] = None,
    accept: str = "",
    multiple: bool = True,
    lazy: bool = True,
    **kwargs
):
    """ """
    file_info, set_file_info = solara.use_state(None)
    wired_files, set_wired_files = solara.use_state(cast(Optional[List[FileInfo]], []))

    file_input = ExtraFileInput.element(
        label=label,
        on_total_progress=on_total_progress,
        on_file_info=set_file_info,
        accept=accept,
        multiple=multiple,
        **kwargs
    )

    def wire_files() -> None:
        if not file_info:
            set_wired_files([])

        real = cast(ExtraFileInput, solara.get_widget(file_input))

        # workaround for @observe being cleared
        real.version += 1
        real.reset_stats()

        set_wired_files(cast(List[FileInfo], real.get_files()))

    solara.use_effect(wire_files, [file_info])

    def handle_file(cancel: threading.Event) -> None:
        if not on_file:
            return
        if not wired_files:
            on_file([])
        if lazy:
            for f_info in wired_files:
                f_info["data"] = None
        else:
            for f_info in wired_files:
                f_info["data"] = f_info["file_obj"].read()

        on_file(wired_files)

    result: solara.Result = hooks.use_thread(handle_file, [wired_files])
    if result.error:
        raise result.error

    return file_input
