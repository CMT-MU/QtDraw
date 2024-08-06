"""
Test for math table widget.

This module provides a test for MathTable.
"""

from PySide6.QtWidgets import QWidget
from qtdraw.util.qt_event_util import get_qt_application
from qtdraw.widget.custom_widget import Layout
from qtdraw.widget.table_view import TableView


# ==================================================
def test_math_table():
    app = get_qt_application()

    widget = QWidget()
    widget.setWindowTitle("Math Table test")
    widget.resize(800, 400)
    layout = Layout(widget)
    layout.setContentsMargins(10, 10, 10, 10)

    data = [
        [r"\frac{\sqrt{3}}{2}(x^2-y^2)", r"\begin{bmatrix} 1 & 2 \\ 3 & 4 \end{bmatrix}"],
        [r"\left[\begin{array}{cc} 1 & 2 \\ 3 & 4 \end{array}\right]", r"f'(x) =\lim _{h\rightarrow 0}\dfrac{f(x+h) - f(x) }{h}"],
    ]
    table = TableView(None, data, ["eq1", "eq2"])
    layout.addWidget(table)

    widget.show()

    app.exec()


# ================================================== main
if __name__ == "__main__":
    test_math_table()
