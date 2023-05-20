from qtpy.QtWidgets import QWidget, QTreeView, QGridLayout, QHeaderView, QInputDialog, QPushButton
from qtpy.QtCore import Qt, Signal
from qtdraw.core.group_model import GroupModel, Delegate
from qtdraw.core.setting import rcParams


# ==================================================
class TreeView(QTreeView):
    deselectedItem = Signal()

    def mousePressEvent(self, event):
        self.deselectedItem.emit()
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Down or event.key() == Qt.Key_Up:
            self.deselectedItem.emit()
            super().keyPressEvent(event)
            self.clicked.emit(self.selectionModel().currentIndex())
        else:
            super().keyPressEvent(event)


# ==================================================
class GroupView(QWidget):
    textMessage = Signal(str)
    selectedData = Signal(str, int)
    deselectedData = Signal()

    # ==================================================
    def __init__(self, ds, name, read_only=False, align=None, parent=None):
        super().__init__(parent)

        self.name = name
        self.model = GroupModel(ds, name, read_only, align, parent=self)

        self.view = TreeView(self)
        self.view.setModel(self.model)
        bg = rcParams["detail.table.bg_color"]
        self.view.setStyleSheet(f"selection-background-color: {bg}")
        self.view.clicked.connect(self.itemSelected)
        self.view.deselectedItem.connect(self.itemDeselected)

        delegate = Delegate(bg, self.view)
        self.view.setItemDelegate(delegate)

        for column in self.model.hide:
            self.view.header().setSectionHidden(column, True)

        for column in range(self.model.columnCount()):
            self.view.header().setSectionResizeMode(column, QHeaderView.ResizeToContents)
            self.view.header().setDefaultAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.view.setAlternatingRowColors(True)
        self.view.header().setSectionsMovable(False)
        self.view.header().setStretchLastSection(False)

        if not read_only:
            self.add_button = QPushButton("Add", self)
            self.insert_button = QPushButton("Insert", self)
            self.remove_button = QPushButton("Remove", self)
            self.add_button.setFocusPolicy(Qt.NoFocus)
            self.insert_button.setFocusPolicy(Qt.NoFocus)
            self.remove_button.setFocusPolicy(Qt.NoFocus)

        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        if not read_only:
            layout.addWidget(self.view, 0, 0, 1, 3)
            layout.addWidget(self.add_button, 1, 0)
            layout.addWidget(self.insert_button, 1, 1)
            layout.addWidget(self.remove_button, 1, 2)

            self.add_button.clicked.connect(self.add)
            self.insert_button.clicked.connect(self.insert)
            self.remove_button.clicked.connect(self.remove)
        else:
            layout.addWidget(self.view, 0, 0)

        self.setLayout(layout)

    # ==================================================
    def itemSelected(self, index):
        indices = index.model().childIndex(index)
        if len(indices) == 1:  # no child.
            row = index.model().absIndex(indices[0])[0]
            self.selectedData.emit(self.name, row)
        else:  # with child.
            for idx in indices[:-1]:
                row = index.model().absIndex(idx)[0]
                self.selectedData.emit(self.name, row)

    # ==================================================
    def itemDeselected(self):
        self.view.clearSelection()
        self.deselectedData.emit()

    # ==================================================
    def add(self):
        text, ok = QInputDialog.getText(self, self.model.name, "Name:")
        if ok:
            self.itemDeselected()
            self.model.appendRow(name=str(text))
            self.textMessage.emit(f"add '{text}' object into {self.name}.")

    # ==================================================
    def insert(self):
        index = self.view.selectedIndexes()
        if len(index) != 0:
            self.itemDeselected()
            self.model.appendRow(index[0])
            self.textMessage.emit(f"insert object into {self.name}.")

    # ==================================================
    def remove(self):
        index = self.view.selectedIndexes()
        if len(index) != 0:
            self.itemDeselected()
            self.model.removeRow(index[0])
            self.textMessage.emit(f"remove object from {self.name}.")
