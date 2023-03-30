import solara
from typing import cast, Optional
from solara.alias import rv

solara.MarkdownIt
@solara.component
def Page():
    show_code, set_show_code = solara.use_state(False)
    print('show', show_code)
    solara.Button("Open dialog", on_click=lambda *args: set_show_code(True))

    with rv.Dialog(v_model=show_code, on_v_model=set_show_code) as diag:
        with rv.Sheet():
            solara.Info("Hello world")
            solara.Button("Close dialog", on_click=lambda *args: set_show_code(False))

