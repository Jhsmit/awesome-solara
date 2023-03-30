import solara
from solara.alias import rv as v

@solara.component
def Page():

    with solara.AppBar():
        solara.Button("Submit")

    solara.Title("I am the title")
    with solara.Card():
        solara.Markdown("# Welcome")
    with solara.Card():
        solara.Button("Hello")

    with solara.ColumnsResponsive([2, 7, 3]):
        solara.Button("Btn1", block=True) # use block=True to make the button fill the width
        solara.Button("Btn2", block=True)
        solara.Button("Btn3", block=True, style_='background-color: red;')

    vepc1 = v.ExpansionPanel(children=[
        v.ExpansionPanelHeader(children=['item1']),
        v.ExpansionPanelContent(children=['First Text'])])

    vepc2 = v.ExpansionPanel(children=[
        v.ExpansionPanelHeader(children=['item2']),
        v.ExpansionPanelContent(children=['Second Text'])])

    vep = v.ExpansionPanels(children=[vepc1, vepc2])
    vl = v.Layout(class_='pa-4', children=[vep])

    _file_list = [
        {"name": "file1.txt", "icon": "mdi-file", "subtitle": "banana"},
        {"name": "file2.pdf", "icon": "mdi-file-pdf", "subtitle": "pear"},
        {"name": "filasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasweasefaseasesefe3.png", "icon": "mdi-file-image", "subtitle": "apple"}
    ]

    file_list, set_file_list = solara.use_state(_file_list)

    list_items = []
    for idx, file in enumerate(file_list):
        # delete_icon = v.ListItemIcon(right=True, children=[v.Icon(children=['mdi-delete'])])

        def on_delete(idx=idx):
            new_items = file_list.copy()
            del new_items[idx]
            set_file_list(new_items)

        delete_btn = solara.IconButton(color='primary', small=True, rounded=True, icon_name='mdi-delete',
                          on_click=lambda *args: on_delete())

        list_item = v.ListItem(class_="two--line",
            children=[
                v.ListItemIcon(left=True, children=[v.Icon(children=[file['icon']])]),
                v.ListItemTitle(children=[file['name']]),
                v.ListItemSubtitle(children=[file["subtitle"]]),
                delete_btn
            ]
        )
        list_items.append(list_item)

    v.List(children=list_items, class_='mx-auto', max_width=500)


v.ListItemContent

solara.ListItem