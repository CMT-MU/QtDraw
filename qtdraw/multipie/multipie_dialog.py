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
from qtdraw.multipie.multipie_group_list import group_list


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
        self._counter = {}

        self._crystal_list = {crystal: {tp: i[1] for tp, i in v.items()} for crystal, v in group_list.items()}
        self._to_tag = {}
        self._to_name = {}
        for v in group_list.values():
            for i in v.values():
                for a, b in zip(i[0], i[1]):
                    self._to_tag[b] = a
                    self._to_name[a] = b

        self.set_title()
        self.resize(600, 500)

        # initial value.
        crystal, tp, idx = "triclinic", "PG", 0  # PG#1.
        self._set_group_data(self._crystal_list[crystal][tp][idx], crystal, tp)

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
        self.group_changed.connect(group_panel.set_harm_list)
        self._pvw.data_removed.connect(self.clear_data)

        self.group_changed.emit()
        sub_panel.set_group_name()

        self.show()

    # ==================================================
    @property
    def group(self):
        if self._group is None:
            self._group = Group(self._tag)

        return self._group

    # ==================================================
    @property
    def ps_group(self):
        if self.group.group_type in ["PG", "SG"]:
            return self.group
        if self._ps_group is None:
            ps = self.group.info.PG if self.group.group_type in ["MPG"] else self.group.info.SG
            self._ps_group = Group(ps)

        return self._ps_group

    # ==================================================
    @property
    def p_group(self):
        if self.group.group_type in ["PG"]:
            return self.group
        if self._p_group is None:
            self._p_group = Group(self.group.info.PG)

        return self._p_group

    # ==================================================
    @property
    def mp_group(self):
        if self.group.group_type in ["MPG"]:
            return self.group
        if self._mp_group is None:
            self._mp_group = Group(self.group.info.MPG)

        return self._mp_group

    # ==================================================
    def set_title(self):
        title = self._pvw.window_title.replace("QtDraw", "MultiPie Plugin")
        self.setWindowTitle(title)

    # ==================================================
    def _set_group_data(self, name, crystal=None, tp=None):
        if crystal is not None:
            self._crystal = crystal
        if tp is not None:
            self._type = tp

        self._tag = self._to_tag[name]
        self._group = None
        self._p_group = None
        self._ps_group = None
        self._mp_group = None

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
        info = self.group.info
        name = {
            "PG": self._to_name[info.PG],
            "SG": self._to_name[info.SG],
            "MPG": self._to_name[info.MPG],
            "MSG": self._to_name[info.MSG],
        }
        return name

    # ==================================================
    def clear_data(self):
        self._counter = {}

    # ==================================================
    def closeEvent(self, event):
        super().closeEvent(event)

    # ==================================================
    def _set_counter(self, name):
        cnt = self._counter.get(name, 0) + 1
        self._counter[name] = cnt
        return cnt

    # ==================================================
    def get_status(self):
        status = {"version": __version__}
        return status

    # ==================================================
    def _get_index_list(self, lst):
        idx = [(Group.tag_multipole(i), i) for i in lst]
        tag_lst = [n for v, _ in idx for n in v]
        idx_comp = [(i, no) for v, i in idx for no, _ in enumerate(v)]

        return tag_lst, idx_comp
