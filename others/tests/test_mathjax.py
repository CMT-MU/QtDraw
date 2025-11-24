import sys
from PySide6.QtWidgets import QApplication, QWidget, QTextEdit, QPushButton, QGridLayout

from qtdraw.widget.mathjax import MathJaxSVG
from qtdraw.widget.custom_widget import MathWidget


# ====================
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.mathjax = MathJaxSVG(clear_cache=False)

        self.text = QTextEdit()
        self.button = QPushButton(text="Convert")
        self.button.clicked.connect(self.convert)
        self.svg = MathWidget(text="", mathjax=self.mathjax)

        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setHorizontalSpacing(2)
        layout.setVerticalSpacing(5)

        layout.addWidget(self.text)
        layout.addWidget(self.button)
        layout.addWidget(self.svg)

    def convert(self):
        self.svg.setText(self.text.toPlainText())

    def closeEvent(self, event):
        self.mathjax.close()
        return super().closeEvent(event)


# ====================
if __name__ == "__main__":
    app = QApplication.instance() or QApplication(sys.argv)

    win = MainWindow()
    win.show()

    app.exec()
