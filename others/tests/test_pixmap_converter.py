from qtdraw.core.pixmap_converter import latex2pixmap, text2pixmap
from qtpy.QtWidgets import QLabel, QWidget, QGridLayout, QLineEdit
from qtdraw.core.util import create_application


class CheckPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.resize(600, 150)
        self.setWindowTitle("Check LaTeX and sympy")

        self.label = QLabel(self)

        label1 = QLabel("latex code", self)
        self.editor1 = QLineEdit(self)
        self.editor1.returnPressed.connect(self.inp1)

        label2 = QLabel("sympy (x,y,z)", self)
        self.editor2 = QLineEdit(self)
        self.editor2.returnPressed.connect(self.inp2)

        layout = QGridLayout()
        layout.addWidget(label1, 0, 0)
        layout.addWidget(self.editor1, 0, 1)
        layout.addWidget(label2, 1, 0)
        layout.addWidget(self.editor2, 1, 1)
        layout.addWidget(self.label, 2, 0, 1, 2)
        self.setLayout(layout)

        self.show()

    def inp1(self):
        latex = self.editor1.text()
        pixmap = latex2pixmap(latex)
        if pixmap:
            self.label.setPixmap(pixmap)

    def inp2(self):
        text = self.editor2.text()
        pixmap = text2pixmap(text, check_var=["x", "y", "z"])
        if pixmap:
            self.label.setPixmap(pixmap)


app = create_application()
w = CheckPanel()
app.exec()
