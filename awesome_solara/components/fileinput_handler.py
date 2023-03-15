import threading

import solara
from ipyvuetify.extra import FileInput as ExtraFileInput
from typing import cast, Optional, Callable, TypedDict, List
from solara.components.file_drop import FileInfo
from solara.lab import Reactive

import solara.hooks as hooks


class ReactiveEvent(Reactive):
    def trigger(self):
        self.set(not self.get())


@solara.component
def FileInput(
    label: str = "",
    on_total_progress: Optional[Callable[[float], None]] = None,
    on_file: Optional[Callable[[List[FileInfo]], None]] = None,
    accept: str = "",
    multiple: bool = True,
    lazy: bool = True,
    clear: Optional[Reactive[bool]] = None,
    **kwargs
):

    file_info, set_file_info = solara.use_state(cast(Optional[List[FileInfo]], None))

    f_input = ExtraFileInput.element(label=label, on_total_progress=on_total_progress, accept=accept, multiple=multiple, **kwargs)  # type: ignore

    # from: https://maartenbreddels.medium.com/advance-your-ipywidget-app-development-with-reacton-6734a5607d69
    def attach_handler():
        widget = solara.get_widget(f_input)

        def on_change(event):
            if event.name == "file_info":
                set_file_info(event.owner.get_files())

        def cleanup():
            widget.unobserve(on_change, names="file_info")

        widget.observe(on_change, names="file_info")

        return cleanup

    solara.use_effect(attach_handler)

    # bind clear to widget.clear()
    # but we re not in the render context so this does not work
    if clear is not None:
        clear.subscribe(lambda x: solara.get_widget(f_input).clear())

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
