from qtpy.QtWidgets import QLabel, QComboBox
from qtdraw.core.line_edit import LineEditor
from qtdraw.core.util import create_application


class CheckPanel(LineEditor):
    def __init__(self, parent=None):
        super().__init__("validator", callback=self.accept, parent=parent)

        self.resize(600, 150)
        self.setWindowTitle("Check LineEdit")

        self.label = QLabel(self)

        self.combo = QComboBox(self)
        self.combo.addItems(self.validator_list)
        self.combo.currentIndexChanged.connect(self.set_val)
        self.combo.currentIndexChanged.emit(0)

        self.layout.addWidget(self.combo, 1, 0)
        self.layout.addWidget(self.label, 2, 0)

        self.layout.setContentsMargins(10, 10, 10, 10)

        self.show()

    def set_val(self, idx):
        key = self.validator_list[idx]
        self.set_validator(key, 4, ["x", "y", "z"])
        self.clear()
        self.label.setText("")

    def accept(self, text):
        self.label.setText("input = '" + text + "'")


app = create_application()
w = CheckPanel()
app.exec()
