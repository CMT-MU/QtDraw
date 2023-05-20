from qtpy.QtWidgets import QDialog, QVBoxLayout, QTabWidget
from qtpy.QtGui import QFont
from qtpy.QtCore import Signal
from qtdraw.core.group_view import GroupView


# ==================================================
class GroupTab(QDialog):
    textMessage = Signal(str)  # message
    selectedData = Signal(str, int)  # name, row
    deselectedData = Signal()
    rawDataChanged = Signal(str, int)  # name, row

    # ==================================================
    def __init__(self, ds, title="Group Tab", width=512, height=800, read_only=False, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(width, height)

        self.tab = QTabWidget(self)
        bold = QFont()
        bold.setBold(True)
        self.tab.tabBar().setFont(bold)
        for name in ds.keys():
            tabItem = GroupView(ds, name, read_only, parent=self)
            tabItem.model.rawDataChanged.connect(self.rawDataChanged.emit)
            tabItem.textMessage.connect(self.textMessage.emit)
            tabItem.selectedData.connect(self.selectedData.emit)
            tabItem.deselectedData.connect(self.deselectedData.emit)
            self.tab.addTab(tabItem, name)
        self.tab.setUsesScrollButtons(True)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.tab)

        self.setLayout(layout)

    # ==================================================
    def closeEvent(self, event):
        for i in range(self.tab.count()):
            self.tab.widget(i).itemDeselected()
        return super().closeEvent(event)
