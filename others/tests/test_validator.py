"""
Test for validators.

This module provides a test for validators.
"""

from qtdraw.util.qt_event_util import get_qt_application
from qtdraw.widget.custom_widget import Panel, Label, LineEdit, Button


# ==================================================
def test_validator():
    app = get_qt_application()

    val_opt = [(-1, 4), (-0.5, 1.5, 3), 3, ["x", "y"], (2, 3), ((2, 3), None, 3)]
    val = ["int", "float", "sympy_float", "sympy", "ilist", "list"]

    panel = Panel()
    lbl = []
    editor = []
    push = Button(None, "show text")
    for i in range(len(val_opt)):
        lbl.append(Label(None, val[i]))
    editor1 = LineEdit(None, "0", (val[0], val_opt[0]))
    editor2 = LineEdit(None, "0", (val[1], val_opt[1]))
    editor3 = LineEdit(None, "0", (val[2], val_opt[2]))
    editor4 = LineEdit(None, "0", (val[3], val_opt[3]))
    editor5 = LineEdit(None, "[[1,2,3],[4,5,6]]", (val[4], val_opt[4]))
    editor6 = LineEdit(None, "[[1,2,3],[4,5,6]]", (val[5], val_opt[5]))
    editor = [editor1, editor2, editor3, editor4, editor5, editor6]

    for i, (l, e) in enumerate(zip(lbl, editor)):
        panel.layout.addWidget(l, i, 0)
        panel.layout.addWidget(e, i, 1)
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
