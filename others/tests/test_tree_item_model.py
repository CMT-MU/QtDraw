from qtdraw.core.util import create_application
from qtpy.QtWidgets import QWidget, QTreeView, QGridLayout, QInputDialog, QPushButton
from qtpy.QtCore import Qt
from gcoreutils.dataset import DataSet
from qtdraw.core.tree_item_model import TreeItemModel
from qtdraw.test.data import test_data1, test_data2


class Window(QWidget):
    def __init__(self, ds, name, parent=None):
        super().__init__(parent)
        self.setWindowTitle(name)
        self.resize(1024, 768)

        self.model = TreeItemModel(ds, name, parent=self)

        self.view = QTreeView()
        self.view.setModel(self.model)

        self.add_button = QPushButton("Add", self)
        self.insert_button = QPushButton("Insert", self)
        self.remove_button = QPushButton("Remove", self)
        self.add_button.setFocusPolicy(Qt.NoFocus)
        self.insert_button.setFocusPolicy(Qt.NoFocus)
        self.remove_button.setFocusPolicy(Qt.NoFocus)

        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self.view, 0, 0, 1, 3)
        layout.addWidget(self.add_button, 1, 0)
        layout.addWidget(self.insert_button, 1, 1)
        layout.addWidget(self.remove_button, 1, 2)

        self.add_button.clicked.connect(self.add)
        self.insert_button.clicked.connect(self.insert)
        self.remove_button.clicked.connect(self.remove)

        self.setLayout(layout)

    def add(self):
        text, ok = QInputDialog.getText(self, self.model.name, "Name:")
        if ok:
            self.model.appendRow(name=str(text))

    def insert(self):
        index = self.view.selectedIndexes()
        if len(index) != 0:
            self.model.appendRow(index[0])

    def remove(self):
        index = self.view.selectedIndexes()
        if len(index) != 0:
            self.model.removeRow(index[0])


ds1 = DataSet(test_data1)
ds2 = DataSet(test_data2)

app = create_application()

ex1 = Window(ds1, "test")
ex1.show()

ex2 = Window(ds2, "site")
ex2.show()

app.exec()
