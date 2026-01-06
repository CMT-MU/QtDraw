"""
Tab of GroupView.

This module provides a set of group view classes in tab format.
"""

from PySide6.QtWidgets import QTabWidget, QDialog
from PySide6.QtGui import QFont

from qtdraw.widget.group_view import GroupView
from qtdraw.widget.custom_widget import Layout
from qtdraw.widget.mathjax import MathJaxSVG


# ==================================================
class TabGroupView(QDialog):
    # ==================================================
    def __init__(self, parent=None, models=None, title="Data", mathjax=None):
        """
        Data view group.

        Args:
            parent (QWidget, optional): parent.
            models (dict, optional): set of models, {object_type: GroupModel}.
            title (str, optional): window title.
        """
        super().__init__(parent)
        if mathjax is None:
            self._mathjax = MathJaxSVG()
        else:
            self._mathjax = mathjax

        if models is None:
            models = {}

        self.setWindowTitle(title)

        self.tab = QTabWidget(self)
        self.tab.setUsesScrollButtons(True)
        bold = QFont()
        bold.setBold(True)
        self.tab.tabBar().setFont(bold)

        self.view = {}
        for object_type, model in models.items():
            item = GroupView(parent=self, model=model, mathjax=self._mathjax)
            self.tab.addTab(item, object_type)
            self.view[object_type] = item

        layout = Layout(self)
        layout.addWidget(self.tab)

        self.setLayout(layout)

        self._tabname = self.tab.tabText(self.tab.currentIndex())
        self.tab.currentChanged.connect(self.tab_change)

    def tab_change(self, idx):
        self.view[self._tabname].clear_selection()
        self._tabname = self.tab.tabText(idx)

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
            view.close()
        super().closeEvent(event)
