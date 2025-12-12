"""
Multipie dialog.

This module provides a dialog for drawing objects with the help of MultiPie.
"""

from PySide6.QtWidgets import QDialog, QTabWidget
from PySide6.QtCore import Signal

from multipie import __version__, Group
from qtdraw.widget.custom_widget import Layout
from qtdraw.multipie.sub_group import SubGroup
from qtdraw.multipie.tab_group import TabGroup
from qtdraw.multipie.tab_object import TabObject
from qtdraw.multipie.tab_basis import TabBasis
from qtdraw.multipie.multipie_setting import setting_detail as detail


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
        self._qtdraw = parent  # QtDraw.
        self._pvw = parent.pyvista_widget  # PyVistaWidget.

        mapping = Group.global_info()["mapping"]
        self._crystal_list = {crystal: {tp: list(i.keys()) for tp, i in enumerate(v.values())} for crystal, v in mapping.items()}
        self._mapping = {}
        for v in mapping.values():
            for i in v.values():
                for k, x in i.items():
                    self._mapping[k] = x
        self._tag_name = {}
        for v in mapping.values():
            for k, x in v["PG"].items():
                self._tag_name[x[0]] = k
            for k, x in v["SG"].items():
                self._tag_name[x[1]] = k
            for k, x in v["MPG"].items():
                self._tag_name[x[2]] = k
            for k, x in v["MSG"].items():
                self._tag_name[x[3]] = k

        self.set_title()
        self.resize(600, 500)

        # initial value.
        self._set_group_data("#1: C1 (1)", "triclinic", 0)  # PG#1.

        self._pvw.update_preference("label", "default_check", detail["general"]["label"])

        sub_panel = SubGroup(self)
        group_panel = TabGroup(self)
        object_panel = TabObject(self)
        basis_panel = TabBasis(self)

        # tab content.
        tab = QTabWidget(self)
        tab.addTab(group_panel, "Group Info.")
        tab.addTab(object_panel, "Object Drawing")
        tab.addTab(basis_panel, "Basis Drawing")

        # main layout.
        layout = Layout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.addWidget(sub_panel, 0, 0, 1, 1)
        layout.addWidget(tab, 0, 1, 1, 1)

        self.group_changed.connect(group_panel.set_irrep_list)
        self.group_changed.connect(group_panel.set_wyckoff_list)

        self.group_changed.emit()
        sub_panel.set_group_name()

        self.show()

    # ==================================================
    def group(self, tp=None):
        if tp is None:
            tp = self._type
        if self._group[tp] is None:
            self._group[tp] = Group(self._tag[tp], with_pg=False)

        return self._group[tp]

    # ==================================================
    def set_title(self):
        title = self._pvw.window_title.replace("QtDraw", "MultiPie Plugin")
        self.setWindowTitle(title)

    # ==================================================
    def _set_group_data(self, tag, crystal=None, tp=None):
        if crystal is not None:
            self._crystal = crystal
        if tp is not None:
            self._type = tp

        self._tag = self._mapping[tag]
        self._group = [None, None, None, None]

        self.group_changed.emit()

    # ==================================================
    def _get_group_list(self, crystal=None, tp=None):
        if crystal is None:
            crystal = self._crystal
        if tp is None:
            tp = self._type
        return self._crystal_list[crystal][tp]

    # ==================================================
    def _get_group_name(self):
        name = [self._tag_name[i] for i in self._tag]
        return name

    # ==================================================
    def clear_data(self):
        # set counter zero.
        pass

    # ==================================================
    def closeEvent(self, event):
        super().closeEvent(event)

    # ==================================================
    def get_status(self):
        status = {"version": __version__}
        return status
