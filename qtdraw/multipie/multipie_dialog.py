"""
Multipie dialog.

This module provides a dialog for drawing objects with the help of MultiPie.
"""

from PySide6.QtWidgets import QDialog, QTabWidget
from PySide6.QtCore import Signal

from qtdraw.widget.custom_widget import Layout
from qtdraw.multipie.sub_group import SubGroup
from qtdraw.multipie.tab_group import TabGroup
from qtdraw.multipie.tab_object import TabObject
from qtdraw.multipie.tab_basis import TabBasis


# ==================================================
class MultiPieDialog(QDialog):
    group_changed = Signal()

    # ==================================================
    def __init__(self, parent):
        """
        MultiPie dialog.

        Args:
            parent (MultiPiePlugin): parent.
        """
        super().__init__()
        self._pvw = parent.pyvista_widget  # PyVistaWidget.
        self._qtdraw = parent  # QtDraw.
        self._shown_data = None  # data shown in the panels.

        self.set_title()
        self.resize(600, 500)

        self._sub_panel = SubGroup(self)
        self._group_panel = TabGroup(self)
        self._object_panel = TabObject(self)
        self._basis_panel = TabBasis(self)

        # tab content.
        tab = QTabWidget(self)
        tab.addTab(self._group_panel, "Group Info.")
        tab.addTab(self._object_panel, "Object Drawing")
        tab.addTab(self._basis_panel, "Basis Drawing")

        # main layout.
        layout = Layout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.addWidget(self._sub_panel, 0, 0, 1, 1)
        layout.addWidget(tab, 0, 1, 1, 1)

        self.group_changed.connect(self._group_panel.set_irrep_list)
        self.group_changed.connect(self._group_panel.set_wyckoff_list)
        self.group_changed.connect(self._group_panel.set_harm_list)
        self.group_changed.connect(self._sub_panel.set_group_name)
        self._pvw.data_removed.connect(self.clear_data)

        self.set_data()

        self.show()

    # ==================================================
    @property
    def _data(self):
        """
        MultiPie data of the PyVistaWidget.

        It is read each time, because opening a file replaces it.

        :meta private:
        """
        if self._pvw._mp_data is None:
            self._pvw.mp_set_group()
        return self._pvw._mp_data

    # ==================================================
    def set_title(self):
        title = self._pvw.window_title.replace("QtDraw", "MultiPie Plugin")
        self.setWindowTitle(title)

    # ==================================================
    def set_data(self):
        self._shown_data = self._data
        self._sub_panel.set_data()
        self._group_panel.set_data()
        self._object_panel.set_data()
        self._basis_panel.set_data()

    # ==================================================
    def clear_data(self):
        self._sub_panel.clear_data()
        self._group_panel.clear_data()
        self._object_panel.clear_data()
        self._basis_panel.clear_data()
        # data replaced by opening a file is kept; only the data shown so far is cleared.
        if self._pvw._mp_data is not None and self._pvw._mp_data is self._shown_data:
            self._pvw._mp_data.clear_data()

    # ==================================================
    def closeEvent(self, event):
        super().closeEvent(event)
