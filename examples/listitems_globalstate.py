import dataclasses
from functools import partial
from typing import List, Callable

import solara
from solara.alias import rv
from solara.lab import Reactive

from awesome_solara.misc import reactive_factory

FILE_LIST = [
    {"name": "file1.txt", "icon": "mdi-file", "subtitle": "banana"},
    {"name": "file2.pdf", "icon": "mdi-file-pdf", "subtitle": "pear"},
    {"name": "asdf.png", "icon": "mdi-file-image", "subtitle": "apple"}
]


@dataclasses.dataclass
class BooleanList():
    bools: Reactive[List[bool]] = dataclasses.field(default_factory=reactive_factory(list))

    def toggle(self, idx: int) -> None:
        new_bools = self.bools.value.copy()
        new_bools[idx] = not new_bools[idx]
        self.bools.value = new_bools

    def get(self, idx: int) -> bool:
        return self.bools.value[idx]

    def delete(self, idx: int) -> None:
        new_bools = self.bools.value.copy()
        del new_bools[idx]
        self.bools.value = new_bools


bools = BooleanList(Reactive([False] * len(FILE_LIST)))


@dataclasses.dataclass
class GlobalState():
    bools: BooleanList = dataclasses.field(default=bools)


@solara.component
def ListFileItem(file: dict, idx: int, on_delete: Callable[[int], None]):
    def on_toggle(value):
        bools.toggle(idx)

    with rv.ListItem() as main:
        rv.ListItemIcon(left=True, children=[rv.Icon(children=[file['icon']])])
        rv.ListItemTitle(children=[file['name']])
        rv.ListItemSubtitle(children=[file["subtitle"]])
        with rv.Btn(icon=True) as button_delete:
            rv.Icon(children=["mdi-delete"])
        rv.use_event(button_delete, "click", lambda *ignore_events: on_delete(idx))
        with rv.ListItemAction() as action:
            solara.Checkbox(value=bools.get(idx), on_value=on_toggle)

    return main


@solara.component
def Page():
    file_list, set_file_list = solara.use_state(FILE_LIST)

    def on_delete(idx):
        print(idx)
        new_items = file_list.copy()
        new_items.pop(idx)
        set_file_list(new_items)
        bools.delete(idx)

    with rv.List(max_width=500) as main:
        for idx, file in enumerate(file_list):
            ListFileItem(file, idx, on_delete)

