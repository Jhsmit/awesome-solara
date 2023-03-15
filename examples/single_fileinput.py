import solara
import reacton.ipyvuetify as rv
from typing import Callable, List, Optional, Literal, get_args
from awesome_solara.components.fileinput_handler import FileInput, FileInfo
from dataclasses import dataclass, replace
import pandas as pd
from awesome_solara.components.fileinput_handler import ReactiveEvent

FILE_TYPES = Literal["csv", "tsv"]

print("asdf")


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
    name, set_name = solara.use_state("")
    file_type, set_file_type = solara.use_state("csv")
    df, set_df = solara.use_state(pd.DataFrame())

    clear = ReactiveEvent(False)

    # has no problems with ascync
    def on_file(file_info: List[FileInfo]):
        if len(file_info) == 0:
            set_df(pd.DataFrame())
        elif len(file_info) == 1:
            df = pd.read_csv(file_info[0]["file_obj"])
            print(df)
            set_df(df)
        else:
            raise ValueError("Expected 1 file, got {}".format(len(file_info)))

    def on_click(*events):
        """Should add a new `FileInputItem` and clear the file input widget"""
        if df.empty:
            return

        on_add(FileInputItem(name=name, file_type=file_type, df=df))

        # clear the fileinput widget
        clear.trigger()

    print("my df", df)

    # v.BtnWithClick
    with solara.Row() as main:
        rv.BtnWithClick(children="Add", on_click=on_click)
        solara.InputText(label="File name", value=name, on_value=set_name)
        solara.Select(
            label="file format",
            values=list(get_args(FILE_TYPES)),
            value=file_type,
            on_value=set_file_type,
        )
        file_input = FileInput(
            label="Upload a file",
            accept=".csv",
            multple=False,
            on_file=on_file,
            lazy=True,
            clear=clear,
        )

        if df.empty:
            solara.Warning("", dense=True)
        else:
            solara.Success("", dense=True)


@solara.component
def NewItemAsyncIORunTimeError(on_add: Callable[[FileInputItem], None]):
    name, set_name = solara.use_state("")
    file_type, set_file_type = solara.use_state("csv")
    file_info, set_file_info = solara.use_state([])
    df, set_df = solara.use_state(pd.DataFrame())

    def on_click(*ignore_events):
        if not name:
            return
        if not file_info:
            return

        # TODO multiple readers
        df = pd.read_csv(file_info[0]["file_obj"])
        set_df(df)

    # v.BtnWithClick
    with solara.Row() as main:
        rv.BtnWithClick(children="Add", on_click=on_click)
        solara.InputText(label="File name", value=name, on_value=set_name)
        solara.Select(
            label="file format",
            values=list(get_args(FILE_TYPES)),
            value=file_type,
            on_value=set_file_type,
        )
        file_input = FileInput(
            label="Upload a file",
            accept=".csv",
            multple=False,
            on_file=set_file_info,
            lazy=True,
        )


@solara.component
def FileApp(items: List[FileInputItem]):
    items, set_items = solara.use_state(items)

    def on_new_item(new_item: FileInputItem):
        new_items = [new_item, *items]
        names = [item.name for item in new_items]
        print("new names", names)
        dfs = [item.df for item in new_items]
        print(dfs)
        set_items(new_items)

    with rv.Container() as main:
        # add_btn = rv.Btn(children=["Add file"])
        # NewItem(on_new_item)
        NewItemAsyncIORunTimeError(on_new_item)


        # add items here such that user can see and delete them.
        # for index, item in enumerate(items):
        #     def on_item_change(changed_item, index=index):
        #         new_items = items.copy()
        #         new_items[index] = changed_item
        #         set_items(new_items)
        #
        #     def on_delete(index=index):
        #         new_items = items.copy()
        #         #del new_items[index]
        #         new_items.pop(index)
        #         set_items(new_items)
        #
        #     FileInputListItem(item, on_item_change, on_delete)

    # combine results and pass to rest of the app / display
    # ...

    return main


page = FileApp(items=[FileInputItem(name="empty", df=None, file_type="csv")])
