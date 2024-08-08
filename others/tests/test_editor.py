"""
Test for editor.

This module provides a test for editor.
"""

from qtdraw.util.qt_event_util import get_qt_application
from qtdraw.widget.custom_widget import Panel, Button, Label, Editor

if __name__ == "__main__":
    app = get_qt_application()

    val_opt = [(-1, 4), (-0.5, 1.5, 3), 3, ["x", "y"], (2, 3), ((2, 3), None, 3), None]
    val = ["int", "float", "sympy_float", "sympy", "ilist", "list", "math"]

    panel = Panel()

    push = Button(None, "show text")
    lbl = [
        Label(None, i)
        for i in [
            "editor (int) [-1,4]",
            "editor (sympy_float) 5",
            "editor (sympy) [x,y,z]",
        ]
    ]
    editor1 = Editor(None, "1", ("int", (-1, 4)))
    editor2 = Editor(None, "sqrt(3)", ("sympy_float", 5))
    editor3 = Editor(None, "x sin(x)", ("sympy", ["x", "y", "z"]))

    panel.layout.setContentsMargins(10, 10, 10, 10)
    for no, i in enumerate(lbl):
        panel.layout.addWidget(i, no + 1, 0)
    panel.layout.addWidget(push, 0, 0, 1, 2)
    panel.layout.addWidget(editor1, 1, 1)
    panel.layout.addWidget(editor2, 2, 1)
    panel.layout.addWidget(editor3, 3, 1)

    def show():
        for no, i in enumerate([editor1, editor2, editor3]):
            print(no + 1, ":", f"text: '{i.text()}', raw: '{i.raw_text()}'")

    push.clicked.connect(show)
    editor1.returnPressed.connect(lambda data: print(f"text: '{editor1.text()}', raw: '{data}'"))
    editor2.returnPressed.connect(lambda data: print(f"text: '{editor2.text()}', raw: '{data}'"))
    editor3.returnPressed.connect(lambda data: print(f"text: '{editor3.text()}', raw: '{data}'"))

    panel.show()

    app.exec()
