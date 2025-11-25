"""
Test for group view and model.

This module provides a test for group view.
"""

from qtdraw.widget.qt_event_util import get_qt_application
from qtdraw.widget.custom_widget import Panel
from qtdraw.widget.group_view import GroupView
from qtdraw.widget.group_model import GroupModel

site = {  # header: (type, option, default).
    "name": ("check", {}, "untitled"),
    "name_check": ("bool", {}, True),
    "name_actor": ("actor", {}, ""),
    "label": ("check", {}, "label"),
    "label_check": ("bool", {}, False),
    "label_actor": ("actor", {}, ""),
    "margin": ("int", {"min": 0, "max": "*"}, "3"),
    "position": ("list_float", {"shape": (3,), "var": [""], "digit": 4}, "[0,0,0]"),
    "cell": ("list_int", {"shape": (3,)}, "[0,0,0]"),
    "size": ("float", {"min": 0.0, "max": "*", "digit": 3}, "0.1"),
    "color": ("color", {}, "darkseagreen"),
    "shape": ("math", {"var": ["x", "y", "z", "r"]}, "1"),
    "combo": ("combo", ["x", "y", "z", "abs"], "abs"),
    "opacity": ("float", {"min": 0.0, "max": 1.0, "digit": 2}, "1.0"),
}

model_list = [
    [
        "mod",
        True,
        "",
        "S",
        False,
        "",
        "1",
        "[0.0, 0.0, 0.0]",
        "[0,0,0]",
        "0.105",
        "darkgrey",
        "z/sqrt(2)",
        "x",
        "1.0",
    ],
    [
        "mod",
        True,
        "",
        "S",
        False,
        "",
        "2",
        "[1.0, 0.0, 0.0]",
        "[0,0,0]",
        "0.105",
        "darkgrey",
        "x y",
        "x",
        "1.0",
    ],
    [
        "mod",
        True,
        "",
        "S",
        False,
        "",
        "3",
        "[2.0, 0.0, 0.0]",
        "[0,0,0]",
        "0.105",
        "darkgrey",
        "z x",
        "x",
        "1.0",
    ],
    [
        "mod",
        True,
        "",
        "S",
        False,
        "",
        "4",
        "[3.0, 0.0, 0.0]",
        "[0,0,0]",
        "0.105",
        "darkgrey",
        "y z",
        "x",
        "1.0",
    ],
    [
        "mod",
        True,
        "",
        "S",
        False,
        "",
        "5",
        "[4.0, 0.0, 0.0]",
        "[0,0,0]",
        "0.105",
        "darkgrey",
        "3z",
        "x",
        "1.0",
    ],
    [
        "mod",
        True,
        "",
        "S",
        False,
        "",
        "6",
        "[5.0, 0.0, 0.0]",
        "[0,0,0]",
        "0.105",
        "darkgrey",
        "z",
        "x",
        "1.0",
    ],
    ["icon", True, "", "S", False, "", "7", "[0.0,0.0,1.2]", "[0,0,0]", "0.56", "cantaloupe", "z", "x", "1.0"],
]

# ================================================== main
if __name__ == "__main__":
    use_delegate = True

    app = get_qt_application()

    widget = Panel()

    model = GroupModel(widget, name="site", column_info=site)
    model.dataModified.connect(lambda n, r, i: print("modified:", n, r, model.show_index(i)))
    model.dataRemoved.connect(lambda n, r, i: print(" removed:", n, r, model.show_index(i)))
    model.checkChanged.connect(lambda n, r, i: print("   check:", n, r, model.show_index(i)))

    def show_select_change(name, deselect, select):
        if deselect is not None:
            print("=== deselect", name)
            for i in deselect:
                print(" ", i)
        if select is not None:
            print("=== select", name)
            for i in select:
                print(" ", i)
            print("==========")

    model.set_data(model_list)

    index = model.index(0, 0)
    model.set_row_data(model.index(2, 0, index), 2, "add")

    view = GroupView(widget, model=model, use_delegate=use_delegate)
    view.expandAll()
    view.selectionChanged.connect(show_select_change)

    widget.layout.addWidget(view)
    widget.resize(1000, 400)
    widget.show()

    app.exec()
