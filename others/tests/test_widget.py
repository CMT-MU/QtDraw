"""
Test for widgets.

This module provides a test for widgets.
"""

import sympy as sp
from PySide6.QtWidgets import QWidget
from qtdraw.util.qt_event_util import get_qt_application
from qtdraw.widget.custom_widget import Layout, Label, ColorLabel, LineEdit, Button, Combo, Spin, DSpin, Check, ColorSelector


# ==================================================
def test_widget():
    app = get_qt_application()

    color1 = ColorLabel(None, "strawberry")
    color2 = ColorLabel(None, "coolwarm")
    color_select1 = ColorSelector(None, "strawberry", color_type="color")
    color_select2 = ColorSelector(None, "coolwarm", color_type="color_both")
    label = Label(None, "label", True)
    check = Check(None, "check")
    button = Button(None, "button")
    combo = Combo(None, ["a", "b", "c"])
    spin = Spin(None, 0, 5)
    dspin = DSpin(None, 1.0, 2.0, 0.1)
    edit1 = LineEdit(None, "text")
    edit2 = LineEdit(None, "0", validator=("int", (-1, 3)))  # opt = min, max
    edit3 = LineEdit(None, "0.1", validator=("float", (-1, 3, 4)))  # min, max, digit
    edit4 = LineEdit(None, "sqrt(3)", validator=("sympy_float", 4))  # digt
    edit5 = LineEdit(None, "[1,2,3]", validator=("ilist", ((3,))))  # shape
    edit6 = LineEdit(None, "[1.0,2,3]", validator=("list", ((3,), [""], 4)))  # shape, var, digit
    m = sp.Matrix([[1, 2, 3], [4, 5, 6]])
    text1 = r"\frac{\sqrt{3}}{2}(x^2-y^2)"
    text2 = r"\begin{bmatrix} 1 & 2 \\ 3 & 4 \end{bmatrix}"
    text3 = r"\left[\begin{array}{cc} 1 & 2 \\ 3 & 4 \end{array}\right]"
    text4 = r"f'(x) =\lim _{h\rightarrow 0}\dfrac{f(x+h) - f(x) }{h}"
    text5 = sp.latex(m)
    mlabel1 = Label(None, text1, color="red", math=True)
    mlabel2 = Label(None, text2, color="red", math=True)
    mlabel3 = Label(None, text3, color="red", math=True)
    mlabel4 = Label(None, text4, color="red", math=True)
    mlabel5 = Label(None, text5, color="red", math=True)

    obj = [
        color1,  # color.
        color2,  # colormap.
        color_select1,  # color selector.
        color_select2,  #  colormap selector.
        label,  # label.
        check,  # check.
        button,  # button.
        combo,  #  comobo.
        spin,  # spin.
        dspin,  # float spin.
        edit1,  # edit.
        edit2,  # edit for int.
        edit3,  # edit for float.
        edit4,
        edit5,
        edit6,
        mlabel1,
        mlabel2,
        mlabel3,
        mlabel4,
        mlabel5,
    ]

    widget = QWidget()
    widget.resize(800, 100)
    layout = Layout(widget)
    layout.setContentsMargins(10, 10, 10, 10)
    layout.setHorizontalSpacing(10)
    layout.setVerticalSpacing(10)
    for i, o in enumerate(obj):
        layout.addWidget(o, i // 4, i % 4)

    color_select1.currentTextChanged.connect(lambda c: print(c))
    color_select2.currentTextChanged.connect(lambda c: print(c))
    check.toggled.connect(lambda c: print(c))
    button.clicked.connect(lambda c: print(c))
    combo.currentTextChanged.connect(lambda c: print(c))
    edit1.returnPressed.connect(lambda: print(edit1.text(), edit1.raw_text()))
    edit2.returnPressed.connect(lambda: print(edit2.text(), edit2.raw_text()))
    edit3.returnPressed.connect(lambda: print(edit3.text(), edit3.raw_text()))
    edit4.returnPressed.connect(lambda: print(edit4.text(), edit4.raw_text()))
    edit5.returnPressed.connect(lambda: print(edit5.text(), edit5.raw_text()))
    edit6.returnPressed.connect(lambda: print(edit6.text(), edit6.raw_text()))

    widget.show()

    app.exec()


# ================================================== main
test_widget()
