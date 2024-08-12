"""
Tab of GroupView.

This module provides a set of group view classes in tab format.
"""

from PySide6.QtWidgets import QTabWidget, QDialog
from PySide6.QtGui import QFont
from qtdraw.widget.group_view import GroupView
from qtdraw.widget.custom_widget import Layout


# ==================================================
class TabGroupView(QDialog):
    # ==================================================
    def __init__(
        self,
        models,
        title="Data",
        parent=None,
    ):
        """
        Data view group.

        Args:
            models (dict): set of models, {object_type: GroupModel}.
            title (str, optional): window title.
            parent (QWidget, optional): parent.
        """
        super().__init__(parent=parent)
        self.setWindowTitle(title)

        self.tab = QTabWidget(self)
        self.tab.setUsesScrollButtons(True)
        bold = QFont()
        bold.setBold(True)
        self.tab.tabBar().setFont(bold)

        self.view = {}
        for object_type, model in models.items():
            item = GroupView(model, parent=self)
            self.tab.addTab(item, object_type)
            self.view[object_type] = item

        layout = Layout(self)
        layout.addWidget(self.tab, 0, 0, 1, 1)

        self.setLayout(layout)

    # ==================================================
    def select_tab(self, object_type):
        """
        Select tab.

        Args:
            object_type (str): object type.
        """
        idx = list(self.view.keys()).index(object_type)
        self.tab.setCurrentIndex(idx)

    # ==================================================
    def closeEvent(self, event):
        """
        Close event for deselect all.

        :meta private:
        """
        for view in self.view.values():
            view.closeEvent(event)
        super().closeEvent(event)

    # ==================================================
    def update_widget(self):
        """
        Update widget.

        :meta private:
        """
        for view in self.view.values():
            view.update_widget(force=True)
