import sys
import xml.etree.ElementTree as ET
from PySide6.QtWidgets import QApplication, QWidget, QTextEdit, QPushButton, QSpinBox, QGridLayout
from PySide6.QtGui import QPainter
from PySide6.QtCore import QSize
from PySide6.QtSvg import QSvgRenderer

from qtdraw.mathjax.mathjax import MathJaxSVG
from qtdraw.widget.custom_widget import ColorSelector


# ====================
class MathWidget(QWidget):
    def __init__(self, parent=None, text="", color="black", size=None, mathjax=None):
        super().__init__(parent)
        if size is None:
            size = self.font().pointSize()
        self._size = size + 5
        self._color = color
        self._text = ""
        self._renderer = None
        self._wsize = (0, 0)

        if mathjax is None:
            self.mathjax = MathJaxSVG(clear_cache=True)
        else:
            self.mathjax = mathjax

        self.setText(text)

    def setColor(self, color):
        self._color = color
        self.setText(self._text)

    def setSize(self, size):
        self._size = size + 5
        self.setText(self._text)

    def setText(self, text):
        self._text = text
        latex = "$$" + text + "$$"

        svg, wh = self.mathjax.convert(latex, self._color, self._size)
        self._wsize = wh

        root = ET.fromstring(svg)
        svg_bytes = ET.tostring(root, encoding="utf-8")
        self._renderer = QSvgRenderer(svg_bytes)
        self.setFixedSize(*self._wsize)
        self.update()

    def paintEvent(self, event):
        if self._renderer:
            self._renderer.render(QPainter(self))

    def sizeHint(self):
        return QSize(*self._wsize)

    def text(self):
        return self._text


# ====================
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.mathjax = MathJaxSVG(clear_cache=False)

        self.text = QTextEdit()
        self.button = QPushButton(text="Convert")
        self.button.clicked.connect(self.convert)
        self.size = QSpinBox(minimum=8, maximum=96)
        self.size.valueChanged.connect(lambda x: self.svg.setSize(x))
        self.color = ColorSelector()
        self.color.currentTextChanged.connect(lambda x: self.svg.setColor(x))
        self.svg = MathWidget(text="", mathjax=self.mathjax)

        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setHorizontalSpacing(2)
        layout.setVerticalSpacing(5)

        layout.addWidget(self.text, 0, 0, 1, 3)
        layout.addWidget(self.button, 1, 0, 1, 1)
        layout.addWidget(self.color, 1, 1, 1, 1)
        layout.addWidget(self.size, 1, 2, 1, 1)
        layout.addWidget(self.svg, 2, 1, 1, 1)

    def convert(self):
        self.svg.setText(self.text.toPlainText())

    def closeEvent(self, event):
        self.mathjax.close()
        return super().closeEvent(event)


# ====================
if __name__ == "__main__":
    import sys, os
    from contextlib import contextmanager

    @contextmanager
    def suppress_stderr():
        fd = sys.stderr.fileno()
        old_stderr = os.dup(fd)
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, fd)
        os.close(devnull)
        try:
            yield
        finally:
            os.dup2(old_stderr, fd)
            os.close(old_stderr)

    with suppress_stderr():
        app = QApplication.instance() or QApplication(sys.argv)

        win = MainWindow()
        win.show()

        app.exec()
