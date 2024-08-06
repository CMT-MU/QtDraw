"""
Render LaTeX to SVG.

This module provides LaTeX converter to SVG.

See for example, https://github.com/ipython/IPython/lib/latextools.py.
"""

from io import BytesIO
from matplotlib import figure
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QGridLayout
from PySide6.QtGui import Qt, QPainter
from PySide6.QtSvgWidgets import QSvgWidget
from gcoreutils.color_palette import all_colors
from qtdraw.util.util import set_latex_setting


# ==================================================
def latex_to_svg(text, wrap=True, color="black", size=12):
    """
    Render a LaTeX string to svg via matplotlib.

    Args:
        text (str): raw string containing valid inline LaTeX.
        wrap (bool, optional): if true, automatically wrap `s` as a LaTeX equation.
        color (str, optional): color name.
        size (int, optional): fontsize.

    Returns:
        - (str) -- SVG code (byte string).
        - (int) -- width.
        - (int) -- height.

    Note:
        - None is returned when the backend cannot be used.
    """
    # mpl mathtext doesn't support display math, force inline
    text = text.replace("$$", "$")
    if wrap:
        text = "${0}$".format(text)

    color = all_colors[color][0]

    fig = figure.Figure()
    fig.text(0, 0, text, fontsize=size, color=color)

    buffer = BytesIO()
    fig.savefig(buffer, format="svg", transparent=True, bbox_inches="tight", pad_inches=0.1)

    svg = buffer.getvalue()
    w, h = get_svg_size(svg.decode())
    return svg, w, h


# ==================================================
def get_svg_size(svg):
    """
    Get SVG size.

    Args:
        svg (str): bin code of svg.

    Returns:
        - (int) -- width.
        - (int) -- hight.
    """
    svg = svg.replace("'", '"')

    # find viewBox='x y width height' in SVG.
    start = svg.find('viewBox="')
    if start == -1:
        return None
    start += 9
    end = svg.find('"', start)
    if end == -1:
        return None

    # convert to size.
    view = svg[start:end]
    view = view.split(" ")
    if len(view) != 4:
        return None

    width = int(float(view[2]))
    height = int(float(view[3]))

    return width, height


# ==================================================
class SVGWidget(QSvgWidget):
    # ==================================================
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        super().paintEvent(event)


# ==================================================
class MathText(QWidget):
    # ==================================================
    def __init__(self, parent, text, size, color):
        """
        Math Text via SVG.

        Args:
            parent (QWidget): parent.
            text (str): LaTeX stirng without "$".
            size (int): font size.
            color (str): color.
        """
        super().__init__(parent=parent)

        self.widget = QLabel(self)
        self.widget.setAlignment(Qt.AlignCenter)

        text, w, h = latex_to_svg(text, True, color, size)
        self.widget = SVGWidget(self)
        self.widget.setFixedSize(w, h)
        self.widget.load(text)

        layout = QGridLayout(self)
        layout.addWidget(self.widget)


# ================================================== main
if __name__ == "__main__":
    set_latex_setting()
    app = QApplication([])
    # ex = r"E=mc^2"
    ex = r"\begin{bmatrix} a & b \\ c & d \end{bmatrix}"
    widget = MathText(None, ex, 24, "black")
    widget.show()

    app.exec()
