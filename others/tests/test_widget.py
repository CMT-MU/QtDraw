"""
Test for widgets.

This module provides a test for widgets.
"""

from qtdraw.widget.qt_event_util import get_qt_application
from qtdraw.widget.custom_widget import (
    Panel,
    Label,
    MathWidget,
    ColorSelector,
    Button,
    Combo,
    Spin,
    DSpin,
    Check,
    LineEdit,
    Editor,
)


# ==================================================
def test_widget():
    app = get_qt_application()

    widget = Panel()
    widget.resize(800, 100)
    widget.layout.setContentsMargins(10, 10, 10, 10)
    widget.layout.setHorizontalSpacing(10)
    widget.layout.setVerticalSpacing(10)

    bold = False

    label1 = Label(widget, text="Normal Label")
    label2 = Label(widget, text="Bold Label", bold=True)
    label3 = Label(widget, text="Red Label", color="red")
    label4 = Label(widget, text="Large Blue", color="blue", size=18)
    latex = r"\int_0^\infty e^{-x^2}\,dx = \frac{\sqrt{\pi}}{2}"
    latex = "[\\frac{2}{3},\\sin{\\left(x\\right)},\\cos{\\left(y\\right)}]"
    label5 = MathWidget(widget, text=latex, color="green")
    label6 = MathWidget(widget, text="xyz", color="green")
    label9 = ColorSelector(widget, current="strawberry", color_type="color", bold=bold)
    label9.currentTextChanged.connect(lambda c: print(c))
    label10 = ColorSelector(widget, current="coolwarm", color_type="color_both", bold=bold)
    label10.currentTextChanged.connect(lambda c: print(c))
    label12 = Button(widget, text="button", toggle=True, bold=bold)
    label12.clicked.connect(lambda c: print(c))
    label13 = Combo(widget, item=["a", "b", "c"], bold=bold)
    label13.currentTextChanged.connect(lambda c: print(c))
    label14 = Check(widget, text="check", bold=bold)
    label14.toggled.connect(lambda c: print(c))
    label15 = Spin(widget, minimum=0, maximum=5, bold=bold)
    label15.valueChanged.connect(lambda c: print(c))
    label16 = DSpin(widget, minimum=1.0, maximum=2.0, step=0.1, bold=bold)
    label16.valueChanged.connect(lambda c: print(c))

    edit1 = LineEdit(widget, text="text", bold=bold)
    edit1.set_read_only(True)
    edit1.returnPressed.connect(lambda: print("display =", edit1.text(), "raw =", edit1.raw_text()))
    edit2 = LineEdit(widget, text="0", validator=("int", {"min": -1, "max": 3}), bold=bold)
    edit2.returnPressed.connect(lambda: print("display =", edit2.text(), "raw =", edit2.raw_text()))
    edit3 = LineEdit(widget, text="0.1", validator=("float", {"min": -1, "max": 3, "digit": 4}), bold=bold)
    edit3.returnPressed.connect(lambda: print("display =", edit3.text(), "raw =", edit3.raw_text()))
    edit4 = LineEdit(widget, text="sqrt(3)", validator=("list_float", {"digit": 4}), bold=bold)
    edit4.returnPressed.connect(lambda: print("display =", edit4.text(), "raw =", edit4.raw_text()))
    edit5 = LineEdit(widget, text="[1,2,3]", validator=("list_int", {"shape": (3,)}), bold=bold)
    edit5.returnPressed.connect(lambda: print("display =", edit5.text(), "raw =", edit5.raw_text()))
    edit6 = LineEdit(widget, text="[1.0,2,3]", validator=("list_float", {"shape": (3,), "var": [""], "digit": 4}), bold=bold)
    edit6.returnPressed.connect(lambda: print("display =", edit6.text(), "raw =", edit6.raw_text()))

    edit7 = Editor(widget, text="3z**2-r**2", bold=bold)
    edit7.returnPressed.connect(lambda: print("display =", edit7.text(), "raw =", edit7._editor.raw_text()))
    edit8 = Editor(widget, text="3z**2-r**2", validator=("math", {}), bold=bold)
    edit8.returnPressed.connect(lambda: print("display =", edit8.text(), "raw =", edit8._editor.raw_text()))
    edit9 = Editor(widget, text="[2/3,sin(x),cos(y)]", validator=("math", {"shape": (3,), "var": ["x", "y"]}))
    edit9.returnPressed.connect(lambda: print("display =", edit9.text(), "raw =", edit9._editor.raw_text()))

    obj = [
        label1,
        label2,
        label3,
        label4,
        label5,
        label6,
        label9,
        label10,
        label12,
        label13,
        label14,
        label15,
        label16,
        edit1,
        edit2,
        edit3,
        edit4,
        edit5,
        edit6,
        edit7,
        edit8,
        edit9,
    ]

    for i, o in enumerate(obj):
        widget.layout.addWidget(o, i // 4, i % 4)

    widget.show()

    app.exec()


if __name__ == "__main__":
    test_widget()
