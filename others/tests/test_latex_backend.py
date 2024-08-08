"""
Test for LaTeX rendering.

This module provides a test for LaTeX rendering.
"""

from PySide6.QtWidgets import QApplication, QLabel, QWidget
from PySide6.QtGui import QPixmap
from qtdraw.util.latex_to_png import latex_to_png
from qtdraw.util.latex_to_svg import MathText
from qtdraw.widget.custom_widget import Layout
from qtdraw.util.util import set_latex_setting


# ==================================================
class MathLabel(QWidget):
    def __init__(self, code):
        super().__init__()

        code = latex_to_png(code, True, "black", 12, 120)

        pixmap = QPixmap()
        pixmap.loadFromData(code)

        # Display the QPixmap in a QLabel
        label = QLabel()
        label.setPixmap(pixmap)

        # Set up the layout
        layout = Layout(self)
        layout.addWidget(label)


# ================================================== main
if __name__ == "__main__":
    import sympy as sp

    set_latex_setting()

    a = sp.Matrix([1, 2, 3])
    code = r"\frac{\sqrt{3}}{2}(x^2-y^2)"
    code = r"\begin{bmatrix} 1 & 2 \\ 3 & 4 \end{bmatrix}"
    code = r"\left[\begin{array}{cc} 1 & 2 \\ 3 & 4 \end{array}\right]"
    code = r"f'(x) =\lim _{h\rightarrow 0}\dfrac{f(x+h) - f(x) }{h}"
    code = sp.latex(a)

    app = QApplication([])
    png = MathLabel(code)
    png.show()
    svg = MathText(None, code, 24, "black")
    svg.show()

    app.exec()
