"""
Test for group view and model.

This module provides a test for group view.
"""

from qtdraw.widget.group_view import GroupView
from qtdraw.widget.group_model import GroupModel
from qtdraw.util.qt_event_util import get_qt_application

# ================================================== main
if __name__ == "__main__":
    site = {  # header: (type, option, default).
        "name": ("check", None, "untitled"),
        "name_check": ("bool", None, True),
        "name_actor": ("actor", None, ""),
        "label": ("check", None, "label"),
        "label_check": ("bool", None, False),
        "label_actor": ("actor", None, ""),
        "margin": ("int", (0, "*"), "3"),
        "position": ("list", ((3,), [""], 4), "[0,0,0]"),
        "cell": ("ilist", ((3,)), "[0,0,0]"),
        "size": ("float", (0.0, "*", 3), "0.1"),
        "color": ("color", None, "darkseagreen"),
        "opacity": ("float", (0.0, 1.0, 2), "1.0"),
        "shape": ("sympy", ["x", "y", "z", "r"], "1"),
        "combo": ("combo", ["x", "y", "z", "abs"], "abs"),
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
            "0.10500000000000001",
            "darkgrey",
            "1.0",
            "z",
            "x",
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
            "0.10500000000000001",
            "darkgrey",
            "1.0",
            "x y",
            "x",
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
            "0.10500000000000001",
            "darkgrey",
            "1.0",
            "z x",
            "x",
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
            "0.10500000000000001",
            "darkgrey",
            "1.0",
            "y z",
            "x",
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
            "0.10500000000000001",
            "darkgrey",
            "1.0",
            "3z",
            "x",
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
            "0.10500000000000001",
            "darkgrey",
            "1.0",
            "z",
            "x",
        ],
        ["icon", True, "", "S", False, "", "7", "[0.0,0.0,1.2]", "[0,0,0]", "0.56", "cantaloupe", "1.0", "z", "x"],
    ]

    app = get_qt_application()

    model = GroupModel("site", site)
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

    view = GroupView(model)
    view.resize(1200, 400)
    view.expandAll()
    view.selectionChanged.connect(show_select_change)

    view.show()

    app.exec()
