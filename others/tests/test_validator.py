"""
Test for validators.

This module provides a test for validators.
"""

from qtdraw.widget.qt_event_util import get_qt_application
from qtdraw.widget.custom_widget import Panel, Label, LineEdit, Button


# ==================================================
def test_validator():
    app = get_qt_application()

    panel = Panel()
    panel.resize(800, 100)
    panel.layout.setContentsMargins(10, 10, 10, 10)
    panel.layout.setHorizontalSpacing(10)
    panel.layout.setVerticalSpacing(10)

    val = [
        "int (-1,4)",
        "float (-0.5,1.5,3)",
        "list_float (3,), 3",
        "list_int ((3,), [x,y])",
        "list_int (2,3)",
        "list_float (2,3), 3",
        "math ((3,), [x,y])",
    ]
    txt = ["0", "0", "[0,0,0]", "[0,0,0]", "[[1,2,3],[4,5,6]]", "[[1,2,3],[4,5,6]]", "[2/3,sin(x),cos(y)]"]

    lbl = []
    editor = []
    push = Button(panel, text="show text")
    for i in range(len(val)):
        lbl.append(Label(text=val[i]))
    editor1 = LineEdit(panel, text=txt[0], validator=("int", {"min": -1, "max": 4}))
    editor2 = LineEdit(panel, text=txt[1], validator=("float", {"min": -0.5, "max": 1.5, "digit": 3}))
    editor3 = LineEdit(panel, text=txt[2], validator=("list_float", {"shape": (3,), "digit": 3}))
    editor4 = LineEdit(panel, text=txt[3], validator=("list_int", {"shape": (3,), "var": ["x", "y"]}))
    editor5 = LineEdit(panel, text=txt[4], validator=("list_int", {"shape": (2, 3)}))
    editor6 = LineEdit(panel, text=txt[5], validator=("list_float", {"shape": (2, 3), "digit": 3}))
    editor7 = LineEdit(panel, text=txt[6], validator=("math", {"shape": (3,), "var": ["x", "y"]}))
    editor = [editor1, editor2, editor3, editor4, editor5, editor6, editor7]

    for i, (l, e) in enumerate(zip(lbl, editor)):
        v = Label(panel, text=txt[i])
        panel.layout.addWidget(l, i, 0)
        panel.layout.addWidget(v, i, 1)
        panel.layout.addWidget(e, i, 2)
        panel.layout.addWidget(push, len(editor), 0, 1, 2)

    editor1.returnPressed.connect(lambda: print(editor1.text()))
    editor2.returnPressed.connect(lambda: print(editor2.text()))
    editor3.returnPressed.connect(lambda: print(editor3.text()))
    editor4.returnPressed.connect(lambda: print(editor4.text()))
    editor5.returnPressed.connect(lambda: print(editor5.text()))
    editor6.returnPressed.connect(lambda: print(editor6.text()))

    def show():
        for i, e in enumerate(editor):
            print(i, ":", e.text())

    push.clicked.connect(show)

    panel.show()

    app.exec()


# ================================================== main
test_validator()
