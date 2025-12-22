"""
Multipie basis tab.

This module provides basis tab in MultiPie dialog.
"""

import numpy as np
import sympy as sp

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt

from qtdraw.widget.custom_widget import Label, Layout, Button, Combo, VSpacer, HBar, LineEdit
from qtdraw.multipie.multipie_plot import (
    plot_bond_definition,
    plot_site_cluster,
    plot_bond_cluster,
    plot_vector_cluster,
    plot_orbital_cluster,
)
from qtdraw.multipie.multipie_util import (
    create_samb_object,
    check_linear_combination,
    convert_vector_object,
    create_samb_modulation,
)
from qtdraw.multipie.multipie_modulation_dialog import ModulationDialog


# ==================================================
class TabBasis(QWidget):
    # ==================================================
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        layout = Layout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setHorizontalSpacing(30)
        layout.setVerticalSpacing(10)

        # comment.
        label_comment = Label(parent, text="This panel is only for SG/PG", bold=True)

        # definition of bond.
        label_def_bond = Label(
            parent,
            text='<span style="font-weight:bold;">Bond Definition</span> : draw bond definition.<br>&nbsp;&nbsp;1. input representative bond, + ENTER.',
        )
        self.edit_def_bond = LineEdit(parent, text="[0,0,1]@[0,0,0]", validator=("bond", {"use_var": False}))

        panel1 = QWidget(parent)
        layout1 = Layout(panel1)
        layout1.addWidget(label_comment, 0, 0, 1, 1, Qt.AlignRight)
        layout1.addWidget(label_def_bond, 1, 0, 1, 1)
        layout1.addWidget(self.edit_def_bond, 2, 0, 1, 1)

        # site samb.
        label_site = Label(
            parent,
            text='<span style="font-weight:bold;">Site</span> : draw site-cluster basis.<br>&nbsp;&nbsp;1. input representative site, + ENTER, \u21d2 2. choose basis, 3. push "draw".',
        )
        self.edit_site = LineEdit(parent, text="[0,0,0]", validator=("site", {"use_var": False}))

        label_site_to = Label(parent, text="\u21d2 basis")
        self.combo_site_samb = Combo(parent)
        self.button_site_draw = Button(parent, text="draw")

        panel2 = QWidget(parent)
        layout2 = Layout(panel2)
        layout2.addWidget(label_site, 0, 0, 1, 10)
        layout2.addWidget(self.edit_site, 1, 0, 1, 10)
        layout2.addWidget(label_site_to, 2, 0, 1, 1, Qt.AlignRight)
        layout2.addWidget(self.combo_site_samb, 2, 1, 1, 8)
        layout2.addWidget(self.button_site_draw, 2, 9, 1, 1)

        # bond samb.
        label_bond = Label(
            parent,
            text='<span style="font-weight:bold;">Bond</span> : draw bond-cluster basis.<br>&nbsp;&nbsp;1. input representative bond, + ENTER, \u21d2 2. choose basis, 3. push "draw".',
        )
        self.edit_bond = LineEdit(parent, text="[0,0,1]@[0,0,0]", validator=("bond", {"use_var": False}))
        label_bond_to = Label(parent, text="\u21d2 basis")
        self.combo_bond_samb = Combo(parent)
        self.button_bond_draw = Button(parent, text="draw")

        panel3 = QWidget(parent)
        layout3 = Layout(panel3)
        layout3.addWidget(label_bond, 0, 0, 1, 10)
        layout3.addWidget(self.edit_bond, 1, 0, 1, 10)
        layout3.addWidget(label_bond_to, 2, 0, 1, 1, Qt.AlignRight)
        layout3.addWidget(self.combo_bond_samb, 2, 1, 1, 8)
        layout3.addWidget(self.button_bond_draw, 2, 9, 1, 1)

        # vector samb.
        label_vector = Label(
            parent,
            text='<span style="font-weight:bold;">Vector</span> : draw symmetry-adapted vector.<br>&nbsp;&nbsp;1. choose type, 2. input representative site/bond, + ENTER,<br>&nbsp;&nbsp;\u21d2  3. choose (type,basis), 4. push "draw" or 3. input linear combination, + ENTER or 3. push "modulation".',
        )
        self.combo_vector_type = Combo(parent, ["Q", "G", "T", "M"])
        self.edit_vector = LineEdit(parent, text="[0,0,1]@[0,0,0]", validator=("site_bond", {"use_var": False}))
        label_vector_to = Label(parent, text="\u21d2 basis")
        self.combo_vector_samb_type = Combo(parent, ["Q", "G", "T", "M"])
        self.combo_vector_samb = Combo(parent)
        self.button_vector_draw = Button(parent, text="draw")

        label_vector_lc = Label(parent, text="linear combination")
        self.edit_vector_lc = LineEdit(parent)
        self.button_vector_modulation = Button(parent, text="modulation (SG)")
        self.combo_vector_modulation_type = Combo(parent, ["Q,G", "T,M"])
        self.edit_vector_modulation = LineEdit(parent)

        panel4 = QWidget(parent)
        layout4 = Layout(panel4)
        layout4.addWidget(label_vector, 0, 0, 1, 10)
        layout4.addWidget(self.combo_vector_type, 1, 0, 1, 1)
        layout4.addWidget(self.edit_vector, 1, 1, 1, 9)
        layout4.addWidget(label_vector_to, 2, 0, 1, 1, Qt.AlignRight)
        layout4.addWidget(self.combo_vector_samb_type, 2, 1, 1, 1)
        layout4.addWidget(self.combo_vector_samb, 2, 2, 1, 7)
        layout4.addWidget(self.button_vector_draw, 2, 9, 1, 1)
        layout4.addWidget(label_vector_lc, 3, 0, 1, 1, Qt.AlignRight)
        layout4.addWidget(self.edit_vector_lc, 3, 1, 1, 9)
        layout4.addWidget(self.button_vector_modulation, 4, 0, 1, 1)
        layout4.addWidget(self.combo_vector_modulation_type, 4, 1, 1, 1)
        layout4.addWidget(self.edit_vector_modulation, 4, 2, 1, 8)

        # orbital samb.
        label_orbital = Label(
            parent,
            text='<span style="font-weight:bold;">Orbital</span> : draw symmetry-adapted orbital.<br>&nbsp;&nbsp;1. choose (type,rank), 2. input representative site/bond, + ENTER,<br>&nbsp;&nbsp;\u21d2  3. choose (type,basis), 4. push "draw" or 3. input linear combination, + ENTER or 3. push "modulation".',
        )
        self.combo_orbital_type = Combo(parent, ["Q", "G", "T", "M"])
        self.combo_orbital_rank = Combo(parent, map(str, range(12)))
        self.edit_orbital = LineEdit(parent, text="[0,0,1]@[0,0,0]", validator=("site_bond", {"use_var": False}))
        label_orbital_to = Label(parent, text="\u21d2 basis")
        self.combo_orbital_samb_type = Combo(parent, ["Q", "G", "T", "M"])
        self.combo_orbital_samb = Combo(parent)
        self.button_orbital_draw = Button(parent, text="draw")

        label_orbital_lc = Label(parent, text="linear combination")
        self.edit_orbital_lc = LineEdit(parent)
        self.button_orbital_modulation = Button(parent, text="modulation (SG)")
        self.combo_orbital_modulation_type = Combo(parent, ["Q,G", "T,M"])
        self.edit_orbital_modulation = LineEdit(parent)

        panel5 = QWidget(parent)
        layout5 = Layout(panel5)
        layout5.addWidget(label_orbital, 0, 0, 1, 10)
        layout5.addWidget(self.combo_orbital_type, 1, 0, 1, 1)
        layout5.addWidget(self.combo_orbital_rank, 1, 1, 1, 1)
        layout5.addWidget(self.edit_orbital, 1, 2, 1, 8)
        layout5.addWidget(label_orbital_to, 2, 0, 1, 1, Qt.AlignRight)
        layout5.addWidget(self.combo_orbital_samb_type, 2, 1, 1, 1)
        layout5.addWidget(self.combo_orbital_samb, 2, 2, 1, 7)
        layout5.addWidget(self.button_orbital_draw, 2, 9, 1, 1)
        layout5.addWidget(label_orbital_lc, 3, 0, 1, 1, Qt.AlignRight)
        layout5.addWidget(self.edit_orbital_lc, 3, 1, 1, 9)
        layout5.addWidget(self.button_orbital_modulation, 4, 0, 1, 1)
        layout5.addWidget(self.combo_orbital_modulation_type, 4, 1, 1, 1)
        layout5.addWidget(self.edit_orbital_modulation, 4, 2, 1, 8)

        # layout.
        layout.addWidget(panel1, 0, 0, 1, 1)
        layout.addWidget(HBar(), 1, 0, 1, 1)
        layout.addWidget(panel2, 2, 0, 1, 1)
        layout.addWidget(HBar(), 3, 0, 1, 1)
        layout.addWidget(panel3, 4, 0, 1, 1)
        layout.addWidget(HBar(), 5, 0, 1, 1)
        layout.addWidget(panel4, 6, 0, 1, 1)
        layout.addWidget(HBar(), 7, 0, 1, 1)
        layout.addWidget(panel5, 8, 0, 1, 1)
        layout.addItem(VSpacer(), 9, 0, 1, 1)

        self._site_samb = {}
        self._bond_samb = {}
        self._vector_samb = {}
        self._orbital_samb = {}

        self._vector_list = {"Q": [], "G": [], "T": [], "M": []}
        self._orbital_list = {"Q": [], "G": [], "T": [], "M": []}

        self._vector_modulation_dialog = None
        self._orbital_modulation_dialog = None

        # connections.
        self.edit_def_bond.returnPressed.connect(self.show_bond_definition)
        self.edit_site.returnPressed.connect(self.set_site)
        self.edit_bond.returnPressed.connect(self.set_bond)
        self.edit_vector.returnPressed.connect(self.set_vector)
        self.edit_orbital.returnPressed.connect(self.set_orbital)
        self.button_site_draw.clicked.connect(self.show_site)
        self.button_bond_draw.clicked.connect(self.show_bond)
        self.combo_vector_samb_type.currentTextChanged.connect(self.set_vector_list)
        self.combo_orbital_samb_type.currentTextChanged.connect(self.set_orbital_list)
        self.button_vector_draw.clicked.connect(self.show_vector)
        self.button_orbital_draw.clicked.connect(self.show_orbital)
        self.edit_vector_lc.returnPressed.connect(self.show_vector_lc)
        self.edit_orbital_lc.returnPressed.connect(self.show_orbital_lc)
        self.button_vector_modulation.clicked.connect(self.create_vector_modulation)
        self.button_orbital_modulation.clicked.connect(self.create_orbital_modulation)

    # ==================================================
    def set_site(self):
        group = self.parent.ps_group
        site = self.edit_site.raw_text()

        self._site_wp, self._sites = group.find_wyckoff_site(site)
        self._site_samb = group.cluster_samb(self._site_wp)

        lst, self._site_samb_list = self.parent._get_index_list(self._site_samb.keys())
        self.combo_site_samb.set_item(lst)
        self.combo_site_samb.setCurrentIndex(0)

    # ==================================================
    def set_bond(self):
        group = self.parent.ps_group
        bond = self.edit_bond.raw_text()

        self._bond_wp, self._bonds = group.find_wyckoff_bond(bond)
        self._bond_samb = group.cluster_samb(self._bond_wp, "bond")

        lst, self._bond_samb_list = self.parent._get_index_list(self._bond_samb.keys())
        self.combo_bond_samb.set_item(lst)
        self.combo_bond_samb.setCurrentIndex(0)

    # ==================================================
    def set_vector(self):
        group = self.parent.ps_group
        site_bond = self.edit_vector.raw_text()
        vector_type = self.combo_vector_type.currentText()
        samb, self._vector_wp, self._vector_samb_site = group.multipole_cluster_samb(vector_type, 1, site_bond)

        self._vector_samb = {}
        self._vector_samb_list = {}
        self._vector_samb_var = {}
        for tp in ["Q", "G", "T", "M"]:
            self._vector_samb[tp] = samb.select(X=tp)
            self._vector_list[tp], self._vector_samb_list[tp] = self.parent._get_index_list(self._vector_samb[tp].keys())
            self._vector_list[tp] = [f"{tp}{no+1:02d}: {i}" for no, i in enumerate(self._vector_list[tp])]
            self._vector_samb_var[tp] = [f"{tp}{i+1:02d}" for i in range(len(self._vector_list[tp]))]
        self.set_vector_list()

    # ==================================================
    def set_vector_list(self):
        tp = self.combo_vector_samb_type.currentText()
        lst = self._vector_list[tp]
        self.combo_vector_samb.set_item(lst)
        self.combo_vector_samb.setCurrentIndex(0)

    # ==================================================
    def set_orbital(self):
        group = self.parent.ps_group
        site_bond = self.edit_orbital.raw_text()
        orbital_type = self.combo_orbital_type.currentText()
        orbital_rank = int(self.combo_orbital_rank.currentText())
        samb, self._orbital_wp, self._orbital_samb_site = group.multipole_cluster_samb(orbital_type, orbital_rank, site_bond)

        self._orbital_samb = {}
        self._orbital_samb_list = {}
        self._orbital_samb_var = {}
        for tp in ["Q", "G", "T", "M"]:
            self._orbital_samb[tp] = samb.select(X=tp)
            self._orbital_list[tp], self._orbital_samb_list[tp] = self.parent._get_index_list(self._orbital_samb[tp].keys())
            self._orbital_list[tp] = [f"{tp}{no+1:02d}: {i}" for no, i in enumerate(self._orbital_list[tp])]
            self._orbital_samb_var[tp] = [f"{tp}{i+1:02d}" for i in range(len(self._orbital_list[tp]))]
        self.set_orbital_list()

    # ==================================================
    def set_orbital_list(self):
        tp = self.combo_orbital_samb_type.currentText()
        lst = self._orbital_list[tp]
        self.combo_orbital_samb.set_item(lst)
        self.combo_orbital_samb.setCurrentIndex(0)

    # ==================================================
    def show_bond_definition(self):
        group = self.parent.ps_group
        bond = self.edit_def_bond.raw_text()
        wp, bonds = group.find_wyckoff_bond(bond)

        plot_bond_definition(self.parent, bonds, wp)

    # ==================================================
    def show_site(self):
        samb, comp = self._site_samb_list[self.combo_site_samb.currentIndex()]

        samb = self._site_samb[samb][0][comp]
        plot_site_cluster(self.parent, self._sites, samb, self._site_wp)

    # ==================================================
    def show_bond(self):
        samb, comp = self._bond_samb_list[self.combo_bond_samb.currentIndex()]
        sym = samb[0] in ["Q", "G"]

        samb = self._bond_samb[samb][0][comp]
        plot_bond_cluster(self.parent, self._bonds, samb, self._bond_wp, sym)

    # ==================================================
    def show_vector(self):
        X = self.combo_vector_type.currentText()
        tp = self.combo_vector_samb_type.currentText()
        samb, comp = self._vector_samb_list[tp][self.combo_vector_samb.currentIndex()]

        samb = self._vector_samb[tp][samb][0][comp]
        wp = self._vector_wp
        site = self._vector_samb_site

        obj = create_samb_object(self.parent.ps_group, tp, samb, wp, site)
        obj = convert_vector_object(obj)
        plot_vector_cluster(self.parent, site, obj, X)

    # ==================================================
    def show_vector_lc(self):
        ex = self.edit_vector_lc.raw_text()
        ex, var = check_linear_combination(ex, self._vector_samb_var)
        if ex is None:
            return

        X = self.combo_vector_type.currentText()
        wp = self._vector_wp
        site = self._vector_samb_site

        lc_obj = {}
        for i in var:
            tp = i[0]
            idx = int(i[1:]) - 1
            samb, comp = self._vector_samb_list[tp][idx]
            samb = self._vector_samb[tp][samb][0][comp]
            lc_obj[i] = create_samb_object(self.parent.ps_group, tp, samb, wp, site)
            lc_obj[i] = sp.Matrix(convert_vector_object(lc_obj[i]))

        obj = np.array(ex.subs(lc_obj))
        plot_vector_cluster(self.parent, site, obj, X)

    # ==================================================
    def show_orbital(self):
        X = self.combo_orbital_type.currentText()
        tp = self.combo_orbital_samb_type.currentText()
        samb, comp = self._orbital_samb_list[tp][self.combo_orbital_samb.currentIndex()]

        samb = self._orbital_samb[tp][samb][0][comp]
        wp = self._orbital_wp
        site = self._orbital_samb_site

        obj = create_samb_object(self.parent.ps_group, tp, samb, wp, site)
        plot_orbital_cluster(self.parent, site, obj, X)

    # ==================================================
    def show_orbital_lc(self):
        ex = self.edit_orbital_lc.raw_text()
        ex, var = check_linear_combination(ex, self._orbital_samb_var)
        if ex is None:
            return

        X = self.combo_orbital_type.currentText()
        wp = self._orbital_wp
        site = self._orbital_samb_site

        lc_obj = {}
        for i in var:
            tp = i[0]
            idx = int(i[1:]) - 1
            samb, comp = self._orbital_samb_list[tp][idx]
            samb = self._orbital_samb[tp][samb][0][comp]
            lc_obj[i] = sp.Matrix(create_samb_object(self.parent.ps_group, tp, samb, wp, site))

        obj = np.array(ex.subs(lc_obj)).reshape(-1)
        plot_orbital_cluster(self.parent, site, obj, X)

    # ==================================================
    def create_vector_modulation(self):
        modulation = self.edit_vector_modulation.text()
        if self.combo_vector_modulation_type.currentText() == "Q,G":
            var = self._vector_samb_var["Q"] + self._vector_samb_var["G"]
        else:
            var = self._vector_samb_var["T"] + self._vector_samb_var["M"]
        if len(var) == 0:
            return
        if not self.parent.ps_group.is_point_group:
            self._vector_modulation_dialog = ModulationDialog(self, modulation, var, vec=True)

    # ==================================================
    def create_orbital_modulation(self):
        modulation = self.edit_orbital_modulation.text()
        if self.combo_orbital_modulation_type.currentText() == "Q,G":
            var = self._orbital_samb_var["Q"] + self._orbital_samb_var["G"]
        else:
            var = self._orbital_samb_var["T"] + self._orbital_samb_var["M"]
        if len(var) == 0:
            return
        if not self.parent.ps_group.is_point_group:
            self._orbital_modulation_dialog = ModulationDialog(self, modulation, var, vec=False)

    # ==================================================
    def create_vector_samb_modulation(self, modulation, phase_dict, igrid, pset):
        wp = self._vector_wp
        site = self._vector_samb_site
        X = self.combo_vector_type.currentText()

        obj, site_idx, full_site = create_samb_modulation(
            self.parent.ps_group, modulation, phase_dict, igrid, pset, self._vector_samb, self._vector_samb_list, wp, site
        )
        obj = convert_vector_object(obj)

        plot_vector_cluster(self.parent, full_site, obj, X)

    # ==================================================
    def create_orbital_samb_modulation(self, modulation, phase_dict, igrid, pset):
        wp = self._orbital_wp
        site = self._orbital_samb_site
        X = self.combo_orbital_type.currentText()

        obj, site_idx, full_site = create_samb_modulation(
            self.parent.ps_group, modulation, phase_dict, igrid, pset, self._orbital_samb, self._orbital_samb_list, wp, site
        )

        plot_orbital_cluster(self.parent, full_site, obj, X)

    # ==================================================
    def closeEvent(self, event):
        if self._vector_modulation_dialog is not None:
            self._vector_modulation_dialog.close()
        if self._orbital_modulation_dialog is not None:
            self._orbital_modulation_dialog.close()
        super().closeEvent(event)
