"""
Multipie dialog.

This module provides a dialog for drawing objects with the help of MultiPie.
"""

import copy
from PySide6.QtWidgets import QDialog, QTabWidget
from PySide6.QtCore import Signal

from multipie import __version__, Group
from qtdraw.widget.custom_widget import Layout
from qtdraw.multipie.sub_group import SubGroup
from qtdraw.multipie.tab_group import TabGroup
from qtdraw.multipie.tab_object import TabObject
from qtdraw.multipie.tab_basis import TabBasis
from qtdraw.multipie.multipie_group_list import group_list
from qtdraw.multipie.multipie_setting import default_status


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
        self._pvw.data_removed.connect(self.clear_data)

        self.set_data()
        self.clear_data()

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
    def set_data(self, data=None):
        dic = copy.deepcopy(default_status)
        if data is not None:
            dic.update(data)

        self._crystal = dic["general"]["crystal"]
        self._type = dic["general"]["type"]
        idx = dic["general"]["index"]
        group = self._crystal_list[self._crystal][self._type][idx]
        self._tag = self._to_tag[group]
        self._group = None
        self._p_group = None
        self._ps_group = None
        self._mp_group = None

        self._counter = dic["counter"]
        self._sub_panel.set_data(dic)
        self._group_panel.set_data(dic)
        self._object_panel.set_data(dic)
        self._basis_panel.set_data(dic)

    # ==================================================
    def clear_data(self):
        self._sub_panel.clear_data()
        self._group_panel.clear_data()
        self._object_panel.clear_data()
        self._basis_panel.clear_data()
        self._counter = {}

    # ==================================================
    def closeEvent(self, event):
        print(self.get_status())
        super().closeEvent(event)

    # ==================================================
    def _set_counter(self, name):
        cnt = self._counter.get(name, 0) + 1
        self._counter[name] = cnt
        return cnt

    # ==================================================
    def get_status(self):
        status = default_status
        dic = {
            "version": __version__,
            "counter": self._counter,
        }
        status.update(self._sub_panel.get_status())
        status.update(self._group_panel.get_status())
        status.update(self._object_panel.get_status())
        status.update(self._basis_panel.get_status())
        status.update(dic)

        return status

    # ==================================================
    def _get_index_list(self, lst):
        idx = [(Group.tag_multipole(i), i) for i in lst]
        tag_lst = [n for v, _ in idx for n in v]
        idx_comp = [(i, no) for v, i in idx for no, _ in enumerate(v)]

        return tag_lst, idx_comp
