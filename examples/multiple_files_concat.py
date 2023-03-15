"""
Adaptation of the Todo example.
Users can add new FileInputItems / ListItem which each has a file input widget.
Currently the state of the FileInput widget is not saved in the FileInputItem, so when adding a
new item to the list does not move the already loaded FileInputWidget down.

"""


import solara
import reacton.ipyvuetify as rv
from typing import Callable, List, Optional, Literal, get_args
from awesome_solara.components.fileinput_handler import FileInput, FileInfo
from dataclasses import dataclass, replace
import pandas as pd

FILE_TYPES = Literal["csv", "tsv"]


@dataclass(frozen=True)
class FileInputItem:
    name: str
    file_type: FILE_TYPES
    df: Optional[pd.DataFrame]


@solara.component
def FileInputListItem(
    file_input_item: FileInputItem,
    on_item_change: Callable[[FileInputItem], None],
    on_delete: Callable[[], None],
):
    def on_file_type(value: FILE_TYPES):
        print(value)
        on_item_change(replace(file_input_item, file_type=value))

    def on_file(file_info: List[FileInfo]):
        if len(file_info) == 0:
            on_item_change(replace(file_input_item, df=None))
        elif len(file_info) == 1:
            SEPARATORS = {"csv": ",", "tsv": "\t"}
            # works, no RuntimeError: asyncio.run() cannot be called from a running event loop
            df = pd.read_csv(file_info[0]["file_obj"], sep=SEPARATORS[file_input_item.file_type])
            on_item_change(replace(file_input_item, df=df))
        else:
            raise ValueError("Expected 1 file, got {}".format(len(file_info)))

    def on_change_name(name: str):
        on_item_change(replace(file_input_item, name=name))

    with rv.ListItem() as main:
        with rv.Btn(icon=True) as button_delete:
            rv.Icon(children=["mdi-delete"])
        rv.use_event(button_delete, "click", lambda *ignore_events: on_delete())
        solara.Text(file_input_item.name)
        file_input = FileInput(
            label="Upload a file",
            accept=".csv",
            multple=False,
            on_file=on_file,
            lazy=True,
        )
        solara.Select(
            label="File type",
            values=list(get_args(FILE_TYPES)),
            value=file_input_item.file_type,
            on_value=on_file_type,
        )

        rv.Icon(children=["mdi-done"])
        if file_input_item.df is not None:
            solara.Success("", dense=True)
        else:
            print("warning name", file_input_item.name)
            solara.Warning("", dense=True)


@solara.component
def NewItem(on_add: Callable[[FileInputItem], None]):
    new_text, set_new_text = solara.use_state("")

    def on_click(*ignore_events):
        if new_text:
            on_add(FileInputItem(name=new_text, file_type="csv", df=None))
            set_new_text("")

    # v.BtnWithClick
    with solara.Row() as main:
        rv.BtnWithClick(children="Add", on_click=on_click)
        with rv.Btn(icon=True) as button_delete:
            rv.Icon(children=["mdi-plus"])

        # with rv.Btn(icon=True) as button_ad da *ignore_events: on_add(FileInputItem(name="New Item", df=None)))
        rv.TextField(label="File name", v_model=new_text, on_v_model=set_new_text)


@solara.component
def FileApp(items: List[FileInputItem]):
    items, set_items = solara.use_state(items)

    def on_new_item(new_item: FileInputItem):
        new_items = [new_item, *items]
        set_items(new_items)

    dfs = [item.df for item in items if item.df is not None]
    names = [item.name for item in items if item.df is not None]
    if dfs:
        concat_df = pd.concat(dfs, axis=1, names=names)
    else:
        concat_df = pd.DataFrame()

    with rv.Container() as main:
        # add_btn = rv.Btn(children=["Add file"])
        NewItem(on_new_item)
        for index, item in enumerate(items):

            def on_item_change(changed_item, index=index):
                new_items = items.copy()
                new_items[index] = changed_item
                set_items(new_items)

            def on_delete(index=index):
                new_items = items.copy()
                # del new_items[index]
                new_items.pop(index)
                set_items(new_items)

            FileInputListItem(item, on_item_change, on_delete)

        solara.DataFrame(concat_df)
    return main


page = FileApp(items=[FileInputItem(name="empty", df=None, file_type="csv")])
