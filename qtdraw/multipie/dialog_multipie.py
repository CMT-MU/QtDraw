"""
Multipie dialog.

This module provides a dialog for drawing objects with the help of MultiPie.
"""

import sympy as sp
from PySide6.QtWidgets import QDialog, QTabWidget, QWidget
from PySide6.QtCore import Qt
from gcoreutils.nsarray import NSArray
from gcoreutils.string_util import remove_space
from multipie.multipole.util.atomic_orbital_util import parse_orb_list
from qtdraw.widget.custom_widget import Label, Layout, Button, Combo, LineEdit, Check, VSpacer, HSpacer, HBar
from qtdraw.multipie.util import create_samb_object, check_linear_combination
from qtdraw.multipie.plugin_multipie_setting import crystal_list, point_group_list, space_group_list, point_group_all_list
from qtdraw.multipie.dialog_info import (
    show_symmetry_operation,
    show_character_table,
    show_wyckoff,
    show_product_table,
    show_harmonics,
    show_harmonics_decomp,
    show_virtual_cluster,
    show_atomic_multipole,
    show_response,
)
from qtdraw.multipie.dialog_modulation import ModulationDialog


# ==================================================
class MultiPieDialog(QDialog):
    # ==================================================
    def __init__(self, parent):
        """
        MultiPie dialog.

        Args:
            parent (MultiPiePlugin): parent.
        """
        super().__init__()
        self.plugin = parent
        title = self.plugin._pvw.window_title.replace("QtDraw", "MultiPie Plugin")
        self.setWindowTitle(title)
        self.resize(600, 500)

        sub_panel = self.create_sub_group_panel(self)
        group_panel = self.create_group_panel(self)
        object_panel = self.create_object_panel(self)
        basis_panel = self.create_basis_panel(self)

        self.set_group_panel_value()
        self.set_object_panel_value()
        self.set_basis_panel_value()

        self.set_group_connection()
        self.set_object_connection()
        self.set_basis_connection()

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

        self._symmetry_operation_dialog = None
        self._character_table_dialog = None
        self._wyckoff_dialog = None
        self._product_table_dialog = None
        self._harmonics_dialog = None
        self._harmonics_decomp_dialog = None
        self._virtual_cluster_dialog = None
        self._atomic_dialog = None
        self._response_dialog = None

        self._vector_modulation_dialog = None
        self._orbital_modulation_dialog = None

    # ==================================================
    @property
    def group(self):
        """
        Group status dict.
        """
        return self.plugin.group

    # ==================================================
    @property
    def obj(self):
        """
        Object status dict.
        """
        return self.plugin.obj

    # ==================================================
    @property
    def basis(self):
        """
        Basis status dict.
        """
        return self.plugin.basis

    # ==================================================
    @property
    def plus(self):
        """
        Plus status dict.
        """
        return self.plugin.plus

    # ==================================================
    def set_group_panel_value(self):
        """
        Set initial values in group panel.
        """
        self.set_basis_item()

        if self.plus["point_group"]:
            self.group_combo_group_type.setCurrentIndex(1)
        else:
            self.group_combo_group_type.setCurrentIndex(0)

        self.group_combo_crystal_type.setCurrentText(self.plus["crystal"])
        self.set_group_item()

        no = self.group_combo_group.find_index(self.group["group"])[0]
        self.group_combo_group.setCurrentIndex(no)
        self.set_irrep_item()
        self.set_wyckoff_item()

        self.group_combo_irrep1.setCurrentText(self.group["irrep1"])
        self.group_combo_irrep2.setCurrentText(self.group["irrep2"])
        self.group_combo_irrep.setCurrentText(self.group["irrep"])
        self.set_irrep_decomp()

        self.group_combo_harmonics_type.setCurrentText(self.group["harmonics_type"])
        self.group_combo_harmonics_rank.setCurrentText(str(self.group["harmonics_rank"]))
        no = self.group_combo_harmonics_decomp.find_index(self.group["harmonics_decomp"])[0]
        self.group_combo_harmonics_decomp.setCurrentIndex(no)

        self.group_combo_vc_wyckoff.setCurrentText(self.group["vc_wyckoff"])
        self.group_edit_vc_neighbor.setText(self.group["vc_neighbor"])

        self.group_combo_atomic_type.setCurrentText(self.group["atomic_type"])
        self.group_combo_atomic_basis_type.setCurrentText(self.group["atomic_basis_type"])
        self.group_combo_atomic_bra_basis.setCurrentText(self.group["atomic_bra"])
        self.group_combo_atomic_ket_basis.setCurrentText(self.group["atomic_ket"])

        self.group_combo_response_type.setCurrentText(self.group["response_type"])
        self.group_combo_response_rank.setCurrentText(str(self.group["response_rank"]))

        self.plugin.parent._set_crystal(self.plus["crystal"])

    # ==================================================
    def set_object_panel_value(self):
        """
        Set initial values in object panel.
        """
        self.object_edit_site.setText(self.obj["site"])

        self.object_edit_bond.setText(self.obj["bond"])

        self.object_combo_vector_type.setCurrentText(self.obj["vector_type"])
        self.object_edit_vector.setText(self.obj["vector"])

        self.object_combo_orbital_type.setCurrentText(self.obj["orbital_type"])
        self.object_edit_orbital.setText(self.obj["orbital"])

        self.set_harmonics_item()
        self.object_combo_harmonics_type.setCurrentText(self.obj["harmonics_type"])
        self.object_combo_harmonics_rank.setCurrentText(str(self.obj["harmonics_rank"]))
        self.object_combo_harmonics_irrep.setCurrentIndex(self.obj["harmonics_irrep"])
        self.object_edit_harmonics.setText(self.obj["harmonics"])
        self.object_check_harmonics_latex.setChecked(self.obj["harmonics_latex"])
        ex = self.plugin.get_harmonics()
        self.object_edit_harmonics_ex.setText(ex)

        self.object_edit_wyckoff.setText(self.obj["wyckoff"])
        wp, sym = self.plugin.find_wyckoff()
        self.object_edit_wyckoff_position.setText(wp)
        self.object_edit_wyckoff_symmetry.setText(sym)

    # ==================================================
    def set_basis_panel_value(self):
        """
        Set initial values in basis panel.
        """
        self.basis_edit_site.setText(self.basis["site"])
        self.basis_combo_site_samb.setCurrentIndex(0)

        self.basis_edit_bond.setText(self.basis["bond"])
        self.basis_combo_bond_samb.setCurrentIndex(0)

        self.basis_combo_vector_type.setCurrentText(self.basis["vector_type"])
        self.basis_edit_vector.setText(self.basis["vector"])
        self.basis_combo_vector_samb_type.setCurrentText(self.basis["vector_samb_type"])
        self.basis_combo_vector_samb.setCurrentIndex(0)
        self.basis_edit_vector_lc.setText(self.basis["vector_lc"])
        self.basis_combo_vector_modulation_type.setCurrentText(self.basis["vector_modulation_type"])
        self.basis_edit_vector_modulation.setText(self.basis["vector_modulation"])

        self.basis_combo_orbital_type.setCurrentText(self.basis["orbital_type"])
        self.basis_combo_orbital_rank.setCurrentIndex(self.basis["orbital_rank"])
        self.basis_edit_orbital.setText(self.basis["orbital"])
        self.basis_combo_orbital_samb_type.setCurrentText(self.basis["orbital_samb_type"])
        self.basis_combo_orbital_samb.setCurrentIndex(0)
        self.basis_edit_orbital_lc.setText(self.basis["orbital_lc"])
        self.basis_combo_orbital_modulation_type.setCurrentText(self.basis["orbital_modulation_type"])
        self.basis_edit_orbital_modulation.setText(self.basis["orbital_modulation"])

        self.basis_edit_hopping.setText(self.basis["hopping"])

    # ==================================================
    def create_sub_group_panel(self, parent):
        """
        Create subgroup panel.

        Args:
            parent (QWidget): parent.

        Returns:
            - (QWidget) -- panel.
        """
        panel = QWidget(parent)
        panel.setMinimumWidth(180)
        layout = Layout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setHorizontalSpacing(30)
        layout.setVerticalSpacing(10)

        # widget.
        label_group = Label(parent, "Group", True)
        self.group_combo_group_type = Combo(parent, ["space group", "point group"])
        self.group_combo_crystal_type = Combo(parent, crystal_list)
        label_group_name = Label(parent, "group")
        self.group_combo_group = Combo(parent, point_group_list["triclinic"])

        label_info = Label(parent, "Info.", True)
        self.group_button_symmetry_operation = Button(parent, "symmetry operation")
        self.group_button_character_table = Button(parent, "character table")
        self.group_button_wyckoff = Button(parent, "Wyckoff position")
        self.group_button_product_table = Button(parent, "product table")

        label_site_bond = Label(
            parent, "SITE:\n   [x,y,z]\n\nBOND:\n   [tail] ; [head]\n   [vector] @ [center]\n   [start] : [vector]"
        )

        layout.addWidget(label_group, 0, 0, 1, 1)
        layout.addWidget(self.group_combo_group_type, 1, 0, 1, 1)
        layout.addWidget(self.group_combo_crystal_type, 2, 0, 1, 1)
        layout.addWidget(label_group_name, 3, 0, 1, 1)
        layout.addWidget(self.group_combo_group, 4, 0, 1, 1)
        layout.addWidget(HBar(), 5, 0, 1, 1)
        layout.addWidget(label_info, 6, 0, 1, 1)
        layout.addWidget(self.group_button_symmetry_operation, 7, 0, 1, 1)
        layout.addWidget(self.group_button_character_table, 8, 0, 1, 1)
        layout.addWidget(self.group_button_wyckoff, 9, 0, 1, 1)
        layout.addWidget(self.group_button_product_table, 10, 0, 1, 1)
        layout.addWidget(HBar(), 11, 0, 1, 1)
        layout.addWidget(label_site_bond, 12, 0, 1, 1)
        layout.addItem(VSpacer(), 13, 0, 1, 1)

        return panel

    # ==================================================
    def create_group_panel(self, parent):
        """
        Create group panel.

        Args:
            parent (QWidget): parent.

        Returns:
            - (QWidget) -- panel.
        """
        panel = QWidget(parent)
        layout = Layout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setHorizontalSpacing(30)
        layout.setVerticalSpacing(10)

        # widget.
        label_decomp = Label(parent, "Irrep. Decomposition", True)
        label_symmetric = Label(parent, "symmetric")
        label_antisymmetric = Label(parent, "anti-symmetric")
        self.group_combo_irrep1 = Combo(parent)
        self.group_combo_irrep2 = Combo(parent)
        label_decomp_disp = Label(parent, "decomposition")
        self.group_label_symmetric_decomp = Label(parent)
        self.group_combo_irrep = Combo(parent)
        self.group_label_antisymmetric_decomp = Label(parent)

        panel12 = QWidget(parent)
        layout12 = Layout(panel12)
        layout12.addWidget(label_decomp, 0, 0, 1, 1)
        layout12.addWidget(label_decomp_disp, 0, 1, 1, 1, Qt.AlignRight)

        panel3 = QWidget(parent)
        layout3 = Layout(panel3)
        layout3.addWidget(label_symmetric, 0, 0, 1, 1, Qt.AlignRight)
        layout3.addWidget(self.group_combo_irrep1, 0, 1, 1, 1)
        layout3.addWidget(self.group_combo_irrep2, 0, 2, 1, 1)
        layout3.addWidget(self.group_label_symmetric_decomp, 0, 3, 1, 1)
        layout3.addWidget(label_antisymmetric, 1, 0, 1, 1, Qt.AlignRight)
        layout3.addWidget(self.group_combo_irrep, 1, 1, 1, 1)
        layout3.addWidget(self.group_label_antisymmetric_decomp, 1, 3, 1, 1)

        label_harmonics = Label(parent, "Harmonics", True)
        self.group_button_harmonics = Button(parent, "show")
        label_harmonics_type = Label(parent, "type")
        self.group_combo_harmonics_type = Combo(parent, ["Q", "G", "T", "M"])
        label_harmonics_rank = Label(parent, "rank")
        self.group_combo_harmonics_rank = Combo(parent, map(str, range(12)))

        label_harmonics_decomp = Label(parent, "target PG")
        self.group_combo_harmonics_decomp = Combo(parent, point_group_all_list)
        self.group_button_harmonics_decomp = Button(parent, "decompose")

        panel5 = QWidget(parent)
        layout5 = Layout(panel5)
        layout5.addWidget(label_harmonics, 0, 0, 1, 1)
        layout5.addWidget(self.group_button_harmonics, 0, 1, 1, 1, Qt.AlignRight)

        panel4 = QWidget(parent)
        layout4 = Layout(panel4)
        layout4.addWidget(label_harmonics_type, 0, 0, 1, 1, Qt.AlignRight)
        layout4.addWidget(self.group_combo_harmonics_type, 0, 1, 1, 1)
        layout4.addWidget(label_harmonics_rank, 0, 2, 1, 1, Qt.AlignRight)
        layout4.addWidget(self.group_combo_harmonics_rank, 0, 3, 1, 1)
        layout4.addWidget(label_harmonics_decomp, 1, 0, 1, 1, Qt.AlignRight)
        layout4.addWidget(self.group_combo_harmonics_decomp, 1, 1, 1, 1)
        layout4.addWidget(self.group_button_harmonics_decomp, 1, 2, 1, 2)

        label_response = Label(parent, "Response Tensor", True)
        self.group_button_response = Button(parent, "show")
        self.group_combo_response_type = Combo(parent, ["Q", "G", "T", "M"])
        label_response_type = Label(parent, "type")
        label_response_rank = Label(parent, "rank")
        self.group_combo_response_rank = Combo(parent, map(str, range(1, 5)))

        panel11 = QWidget(parent)
        layout11 = Layout(panel11)
        layout11.addWidget(label_response, 0, 0, 1, 1)
        layout11.addWidget(self.group_button_response, 0, 1, 1, 1, Qt.AlignRight)

        panel6 = QWidget(parent)
        layout6 = Layout(panel6)
        layout6.addWidget(label_response_type, 0, 0, 1, 1, Qt.AlignRight)
        layout6.addWidget(self.group_combo_response_type, 0, 1, 1, 1)
        layout6.addWidget(label_response_rank, 1, 0, 1, 1, Qt.AlignRight)
        layout6.addWidget(self.group_combo_response_rank, 1, 1, 1, 1)

        label_atomic = Label(parent, "Atomic Multipole", True)
        self.group_button_atomic = Button(parent, "show")
        label_atomic_type = Label(parent, "type")
        self.group_combo_atomic_type = Combo(parent, ["", "Q", "G", "T", "M"])
        self.group_combo_atomic_basis_type = Combo(parent, ["lm", "jm"])
        label_atomic_braket = Label(parent, "bra-ket")
        self.group_combo_atomic_bra_basis = Combo(parent, ["s", "p", "d", "f"])
        self.group_combo_atomic_ket_basis = Combo(parent, ["s", "p", "d", "f"])

        panel10 = QWidget(parent)
        layout10 = Layout(panel10)
        layout10.addWidget(label_atomic, 0, 0, 1, 1)
        layout10.addWidget(self.group_button_atomic, 0, 1, 1, 1, Qt.AlignRight)

        panel7 = QWidget(parent)
        layout7 = Layout(panel7)
        layout7.addWidget(label_atomic_type, 0, 0, 1, 1, Qt.AlignRight)
        layout7.addWidget(self.group_combo_atomic_type, 0, 1, 1, 1)
        layout7.addWidget(self.group_combo_atomic_basis_type, 0, 2, 1, 1)
        layout7.addWidget(label_atomic_braket, 1, 0, 1, 1, Qt.AlignRight)
        layout7.addWidget(self.group_combo_atomic_bra_basis, 1, 1, 1, 1)
        layout7.addWidget(self.group_combo_atomic_ket_basis, 1, 2, 1, 1)

        label_virtual_cluster = Label(parent, "Virtual Cluster", True)
        self.group_button_virtual_cluster = Button(parent, "show")
        label_vc_neighbor = Label(parent, "neighbor")
        label_wyckoff = Label(parent, "wyckoff")
        self.group_combo_vc_wyckoff = Combo(parent)
        self.group_edit_vc_neighbor = LineEdit(parent, "", ("ilist", (0,)))

        panel9 = QWidget(parent)
        layout9 = Layout(panel9)
        layout9.addWidget(label_virtual_cluster, 0, 0, 1, 1)
        layout9.addWidget(self.group_button_virtual_cluster, 0, 1, 1, 1, Qt.AlignRight)

        panel8 = QWidget(parent)
        layout8 = Layout(panel8)
        layout8.addWidget(label_wyckoff, 0, 0, 1, 1, Qt.AlignRight)
        layout8.addWidget(self.group_combo_vc_wyckoff, 0, 1, 1, 1)
        layout8.addWidget(label_vc_neighbor, 1, 0, 1, 1, Qt.AlignRight)
        layout8.addWidget(self.group_edit_vc_neighbor, 1, 1, 1, 1)

        # layout.
        layout.addWidget(panel12, 0, 0, 1, 2)
        layout.addWidget(panel3, 1, 0, 1, 2)
        layout.addWidget(HBar(), 2, 0, 1, 2)

        layout.addWidget(panel5, 3, 0, 1, 1)
        layout.addWidget(panel9, 3, 1, 1, 1)
        layout.addWidget(panel4, 4, 0, 1, 1)
        layout.addWidget(panel8, 4, 1, 1, 1)
        layout.addWidget(HBar(), 5, 0, 1, 2)

        layout.addWidget(panel10, 6, 0, 1, 1)
        layout.addWidget(panel11, 6, 1, 1, 1)
        layout.addWidget(panel7, 7, 0, 1, 1)
        layout.addWidget(panel6, 7, 1, 1, 1)

        layout.addItem(HSpacer(), 0, 3, 1, 1)
        layout.addItem(VSpacer(), 8, 0, 1, 1)

        return panel

    # ==================================================
    def create_object_panel(self, parent):
        """
        Create object panel.

        Args:
            parent (QWidget): parent.

        Returns:
            - (QWidget) -- panel.
        """
        panel = QWidget(parent)
        layout = Layout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setHorizontalSpacing(30)
        layout.setVerticalSpacing(10)

        # widget.
        label_site = Label(
            parent,
            '<span style="font-weight:bold;">Site</span> : draw equivalent sites.<br>&nbsp;&nbsp;1. input representative SITE, + ENTER.',
        )
        self.object_edit_site = LineEdit(parent, "", ("site", False))

        panel1 = QWidget(parent)
        layout1 = Layout(panel1)
        layout1.addWidget(label_site, 0, 0, 1, 1, Qt.AlignLeft)
        layout1.addWidget(self.object_edit_site, 1, 0, 1, 1)

        label_bond = Label(
            parent,
            '<span style="font-weight:bold;">Bond</span> : draw equivalent bonds.<br>&nbsp;&nbsp;1. input representative BOND, + ENTER.',
        )
        self.object_edit_bond = LineEdit(parent, "", ("bond", False))

        panel2 = QWidget(parent)
        layout2 = Layout(panel2)
        layout2.addWidget(label_bond, 0, 0, 1, 1, Qt.AlignLeft)
        layout2.addWidget(self.object_edit_bond, 1, 0, 1, 1)

        label_vector = Label(
            parent,
            '<span style="font-weight:bold;">Vector</span> : draw vectors at equivalent sites or bonds.<br>&nbsp;&nbsp;1. choose type, 2. input vector [x,y,z] # representative SITE/BOND, + ENTER.',
        )
        self.object_combo_vector_type = Combo(parent, ["Q", "G", "T", "M"])
        self.object_edit_vector = LineEdit(parent, "", ("vector_site_bond", False))

        panel3 = QWidget(parent)
        layout3 = Layout(panel3)
        layout3.addWidget(label_vector, 0, 0, 1, 10, Qt.AlignLeft)
        layout3.addWidget(self.object_combo_vector_type, 1, 0, 1, 1)
        layout3.addWidget(self.object_edit_vector, 1, 1, 1, 9)

        label_orbital = Label(
            parent,
            '<span style="font-weight:bold;">Orbital</span> : draw orbitals at equivalent sites or bonds.<br>&nbsp;&nbsp;1. choose type, 2. input orbital (xyz polynomial) # representative SITE/BOND, + ENTER.',
        )
        self.object_combo_orbital_type = Combo(parent, ["Q", "G", "T", "M"])
        self.object_edit_orbital = LineEdit(parent, "", ("orbital_site_bond", False))

        panel4 = QWidget(parent)
        layout4 = Layout(panel4)
        layout4.addWidget(label_orbital, 0, 0, 1, 10, Qt.AlignLeft)
        layout4.addWidget(self.object_combo_orbital_type, 1, 0, 1, 1)
        layout4.addWidget(self.object_edit_orbital, 1, 1, 1, 9)

        label_harmonics = Label(
            parent,
            '<span style="font-weight:bold;">Harmonics</span> : draw point-group harmonics at equivalent sites or bonds.<br>&nbsp;&nbsp;1. choose (type,rank,irrep.), 2. input representative SITE/BOND, + ENTER.<br>&nbsp;&nbsp;\u21d2  expression of harmonics is also shown (in LaTeX form).',
        )
        self.object_combo_harmonics_type = Combo(parent, ["Q", "G", "T", "M"])
        self.object_combo_harmonics_rank = Combo(parent, map(str, range(12)))
        self.object_combo_harmonics_irrep = Combo(parent)
        self.object_edit_harmonics = LineEdit(parent, "", ("site_bond", False))
        label_harmonics_ex = Label(parent, "expression")
        self.object_edit_harmonics_ex = LineEdit(parent)
        self.object_check_harmonics_latex = Check(parent, "LaTeX")

        panel5 = QWidget(parent)
        layout5 = Layout(panel5)
        layout5.addWidget(label_harmonics, 0, 0, 1, 10, Qt.AlignLeft)
        layout5.addWidget(self.object_combo_harmonics_type, 1, 0, 1, 1)
        layout5.addWidget(self.object_combo_harmonics_rank, 1, 1, 1, 1)
        layout5.addWidget(self.object_combo_harmonics_irrep, 1, 2, 1, 3)
        layout5.addWidget(self.object_edit_harmonics, 1, 5, 1, 5)
        layout5.addWidget(label_harmonics_ex, 2, 0, 1, 1)
        layout5.addWidget(self.object_edit_harmonics_ex, 2, 1, 1, 8)
        layout5.addWidget(self.object_check_harmonics_latex, 2, 9, 1, 1, Qt.AlignRight)

        label_wyckoff = Label(
            parent,
            '<span style="font-weight:bold;">Wyckoff</span> : find wyckoff position (WP) and site symmetry (SS).<br>&nbsp;&nbsp;1. input representative SITE/BOND, + ENTER. \u21d2 WP and SS are shown.',
        )
        self.object_edit_wyckoff = LineEdit(parent, "", ("site_bond", False))
        label_wyckoff_position = Label(parent, "\u21d2 WP")
        self.object_edit_wyckoff_position = LineEdit(parent)
        label_symmetry = Label(parent, "sym.")
        self.object_edit_wyckoff_symmetry = LineEdit(parent)

        panel6 = QWidget(parent)
        layout6 = Layout(panel6)
        layout6.addWidget(label_wyckoff, 0, 0, 1, 10, Qt.AlignLeft)
        layout6.addWidget(self.object_edit_wyckoff, 1, 0, 1, 6)
        layout6.addWidget(label_wyckoff_position, 1, 6, 1, 1, Qt.AlignRight)
        layout6.addWidget(self.object_edit_wyckoff_position, 1, 7, 1, 1)
        layout6.addWidget(label_symmetry, 1, 8, 1, 1, Qt.AlignRight)
        layout6.addWidget(self.object_edit_wyckoff_symmetry, 1, 9, 1, 1)

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
        layout.addWidget(HBar(), 9, 0, 1, 1)
        layout.addWidget(panel6, 10, 0, 1, 1)
        layout.addItem(HSpacer(), 0, 1, 1, 1)
        layout.addItem(VSpacer(), 11, 0, 1, 1)

        return panel

    # ==================================================
    def create_basis_panel(self, parent):
        """
        Create basis panel.

        Args:
            parent (QWidget): parent.

        Returns:
            - (QWidget) -- panel.
        """
        panel = QWidget(parent)
        layout = Layout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setHorizontalSpacing(30)
        layout.setVerticalSpacing(10)

        # widget.
        label_site = Label(
            parent,
            '<span style="font-weight:bold;">Site</span> : draw site-cluster basis.<br>&nbsp;&nbsp;1. input representative SITE, + ENTER, \u21d2 2. choose basis, 3. push "draw".',
        )
        self.basis_edit_site = LineEdit(parent, "", ("site", False))

        label_site_to = Label(parent, "\u21d2 basis")
        self.basis_combo_site_samb = Combo(parent)
        self.basis_button_site_draw = Button(parent, "draw")

        panel1 = QWidget(parent)
        layout1 = Layout(panel1)
        layout1.addWidget(label_site, 0, 0, 1, 10)
        layout1.addWidget(self.basis_edit_site, 1, 0, 1, 10)
        layout1.addWidget(label_site_to, 2, 0, 1, 1, Qt.AlignRight)
        layout1.addWidget(self.basis_combo_site_samb, 2, 1, 1, 8)
        layout1.addWidget(self.basis_button_site_draw, 2, 9, 1, 1)

        label_bond = Label(
            parent,
            '<span style="font-weight:bold;">Bond</span> : draw bond-cluster basis.<br>&nbsp;&nbsp;1. input representative BOND, + ENTER, \u21d2 2. choose basis, 3. push "draw".',
        )
        self.basis_edit_bond = LineEdit(parent, "", ("bond", False))
        label_bond_to = Label(parent, "\u21d2 basis")
        self.basis_combo_bond_samb = Combo(parent)
        self.basis_button_bond_draw = Button(parent, "draw")

        panel2 = QWidget(parent)
        layout2 = Layout(panel2)
        layout2.addWidget(label_bond, 0, 0, 1, 10)
        layout2.addWidget(self.basis_edit_bond, 1, 0, 1, 10)
        layout2.addWidget(label_bond_to, 2, 0, 1, 1, Qt.AlignRight)
        layout2.addWidget(self.basis_combo_bond_samb, 2, 1, 1, 8)
        layout2.addWidget(self.basis_button_bond_draw, 2, 9, 1, 1)

        label_vector = Label(
            parent,
            '<span style="font-weight:bold;">Vector</span> : draw symmetry-adapted vector.<br>&nbsp;&nbsp;1. choose type, 2. input representative SITE/BOND, + ENTER,<br>&nbsp;&nbsp;\u21d2  3. choose (type,basis), 4. push "draw" or 3. input linear combination, + ENTER or 3. push "modulation".',
        )
        self.basis_combo_vector_type = Combo(parent, ["Q", "G", "T", "M"])
        self.basis_edit_vector = LineEdit(parent, "", ("site_bond", False))
        label_vector_to = Label(parent, "\u21d2 basis")
        self.basis_combo_vector_samb_type = Combo(parent, ["Q", "G", "T", "M"])
        self.basis_combo_vector_samb = Combo(parent)
        self.basis_button_vector_draw = Button(parent, "draw")

        label_vector_lc = Label(parent, "linear combination")
        self.basis_edit_vector_lc = LineEdit(parent)
        self.basis_button_vector_modulation = Button(parent, "modulation")
        self.basis_combo_vector_modulation_type = Combo(parent, ["Q,G", "T,M"])
        self.basis_edit_vector_modulation = LineEdit(parent)

        panel3 = QWidget(parent)
        layout3 = Layout(panel3)
        layout3.addWidget(label_vector, 0, 0, 1, 10)
        layout3.addWidget(self.basis_combo_vector_type, 1, 0, 1, 1)
        layout3.addWidget(self.basis_edit_vector, 1, 1, 1, 9)
        layout3.addWidget(label_vector_to, 2, 0, 1, 1, Qt.AlignRight)
        layout3.addWidget(self.basis_combo_vector_samb_type, 2, 1, 1, 1)
        layout3.addWidget(self.basis_combo_vector_samb, 2, 2, 1, 7)
        layout3.addWidget(self.basis_button_vector_draw, 2, 9, 1, 1)
        layout3.addWidget(label_vector_lc, 3, 0, 1, 1, Qt.AlignRight)
        layout3.addWidget(self.basis_edit_vector_lc, 3, 1, 1, 9)
        layout3.addWidget(self.basis_button_vector_modulation, 4, 0, 1, 1)
        layout3.addWidget(self.basis_combo_vector_modulation_type, 4, 1, 1, 1)
        layout3.addWidget(self.basis_edit_vector_modulation, 4, 2, 1, 8)

        label_orbital = Label(
            parent,
            '<span style="font-weight:bold;">Orbital</span> : draw symmetry-adapted orbital.<br>&nbsp;&nbsp;1. choose (type,rank), 2. input representative SITE/BOND, + ENTER,<br>&nbsp;&nbsp;\u21d2  3. choose (type,basis), 4. push "draw" or 3. input linear combination, + ENTER or 3. push "modulation".',
        )
        self.basis_combo_orbital_type = Combo(parent, ["Q", "G", "T", "M"])
        self.basis_combo_orbital_rank = Combo(parent, map(str, range(12)))
        self.basis_edit_orbital = LineEdit(parent, "", ("site_bond", False))
        label_orbital_to = Label(parent, "\u21d2 basis")
        self.basis_combo_orbital_samb_type = Combo(parent, ["Q", "G", "T", "M"])
        self.basis_combo_orbital_samb = Combo(parent)
        self.basis_button_orbital_draw = Button(parent, "draw")

        label_orbital_lc = Label(parent, "linear combination")
        self.basis_edit_orbital_lc = LineEdit(parent)
        self.basis_button_orbital_modulation = Button(parent, "modulation")
        self.basis_combo_orbital_modulation_type = Combo(parent, ["Q,G", "T,M"])
        self.basis_edit_orbital_modulation = LineEdit(parent)

        panel4 = QWidget(parent)
        layout4 = Layout(panel4)
        layout4.addWidget(label_orbital, 0, 0, 1, 10)
        layout4.addWidget(self.basis_combo_orbital_type, 1, 0, 1, 1)
        layout4.addWidget(self.basis_combo_orbital_rank, 1, 1, 1, 1)
        layout4.addWidget(self.basis_edit_orbital, 1, 2, 1, 8)
        layout4.addWidget(label_orbital_to, 2, 0, 1, 1, Qt.AlignRight)
        layout4.addWidget(self.basis_combo_orbital_samb_type, 2, 1, 1, 1)
        layout4.addWidget(self.basis_combo_orbital_samb, 2, 2, 1, 7)
        layout4.addWidget(self.basis_button_orbital_draw, 2, 9, 1, 1)
        layout4.addWidget(label_orbital_lc, 3, 0, 1, 1, Qt.AlignRight)
        layout4.addWidget(self.basis_edit_orbital_lc, 3, 1, 1, 9)
        layout4.addWidget(self.basis_button_orbital_modulation, 4, 0, 1, 1)
        layout4.addWidget(self.basis_combo_orbital_modulation_type, 4, 1, 1, 1)
        layout4.addWidget(self.basis_edit_orbital_modulation, 4, 2, 1, 8)

        label_hopping = Label(
            parent,
            '<span style="font-weight:bold;">Hopping</span> : draw hopping direction.<br>&nbsp;&nbsp;1. input representative BOND, + ENTER.',
        )
        self.basis_edit_hopping = LineEdit(parent, "", ("bond", False))

        panel5 = QWidget(parent)
        layout5 = Layout(panel5)
        layout5.addWidget(label_hopping, 0, 0, 1, 1)
        layout5.addWidget(self.basis_edit_hopping, 1, 0, 1, 1)

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
        layout.addItem(HSpacer(), 0, 1, 1, 1)
        layout.addItem(VSpacer(), 9, 0, 1, 1)

        # self.tab2_modulated_vector_active = False
        # self.tab2_modulated_orbital_active = False

        return panel

    # ==================================================
    def set_group_connection(self):
        """
        Set connections in group panel.
        """
        self.group_combo_group_type.currentIndexChanged.connect(self.set_group_type)
        self.group_combo_crystal_type.currentTextChanged.connect(self.set_crystal_type)
        self.group_combo_group.currentTextChanged.connect(self.set_group)

        self.group_button_symmetry_operation.clicked.connect(self.show_symmetry_operation)
        self.group_button_character_table.clicked.connect(self.show_character_table)
        self.group_button_wyckoff.clicked.connect(self.show_wyckoff)
        self.group_button_product_table.clicked.connect(self.show_product_table)

        self.group_combo_irrep1.currentTextChanged.connect(self.set_irrep_decomp)
        self.group_combo_irrep2.currentTextChanged.connect(self.set_irrep_decomp)
        self.group_combo_irrep.currentTextChanged.connect(self.set_irrep_decomp)

        self.group_button_harmonics.clicked.connect(self.show_harmonics)
        self.group_button_harmonics_decomp.clicked.connect(self.show_harmonics_decomp)
        self.group_combo_harmonics_type.currentTextChanged.connect(self.set_harmonics_type)
        self.group_combo_harmonics_rank.currentTextChanged.connect(self.set_harmonics_rank)
        self.group_combo_harmonics_decomp.currentTextChanged.connect(self.set_harmonics_decomp)

        self.group_button_virtual_cluster.clicked.connect(self.show_virtual_cluster)
        self.group_combo_vc_wyckoff.currentTextChanged.connect(self.set_vc_wyckoff)
        self.group_edit_vc_neighbor.returnPressed.connect(self.set_vc_neighbor)

        self.group_button_atomic.clicked.connect(self.show_atomic)
        self.group_combo_atomic_type.currentTextChanged.connect(self.set_atomic_type)
        self.group_combo_atomic_basis_type.currentTextChanged.connect(self.set_atomic_basis_type)
        self.group_combo_atomic_bra_basis.currentTextChanged.connect(lambda x: self.set_atomic_bra_ket())
        self.group_combo_atomic_ket_basis.currentTextChanged.connect(lambda x: self.set_atomic_bra_ket())

        self.group_button_response.clicked.connect(self.show_response)
        self.group_combo_response_type.currentTextChanged.connect(self.set_response_type)
        self.group_combo_response_rank.currentTextChanged.connect(self.set_response_rank)

    # ==================================================
    def set_object_connection(self):
        """
        Set connections in object panel.
        """
        self.object_edit_site.returnPressed.connect(self.obj_add_site)

        self.object_edit_bond.returnPressed.connect(self.obj_add_bond)

        self.object_combo_vector_type.currentTextChanged.connect(self.set_obj_vector_type)
        self.object_edit_vector.returnPressed.connect(self.obj_add_vector)

        self.object_combo_orbital_type.currentTextChanged.connect(self.set_obj_orbital_type)
        self.object_edit_orbital.returnPressed.connect(self.obj_add_orbital)

        self.object_combo_harmonics_type.currentTextChanged.connect(lambda x: self.set_obj_harmonics_type())
        self.object_combo_harmonics_rank.currentTextChanged.connect(lambda x: self.set_obj_harmonics_rank())
        self.object_combo_harmonics_irrep.currentIndexChanged.connect(lambda x: self.set_obj_harmonics())
        self.object_edit_harmonics.returnPressed.connect(self.obj_add_harmonics)
        self.object_check_harmonics_latex.toggled.connect(lambda x: self.set_obj_harmonics())

        self.object_edit_wyckoff.returnPressed.connect(self.set_obj_wyckoff)

    # ==================================================
    def set_basis_connection(self):
        """
        Set connections in basis panel.
        """
        self.basis_edit_site.returnPressed.connect(self.basis_gen_site)
        self.basis_button_site_draw.clicked.connect(self.basis_add_site)

        self.basis_edit_bond.returnPressed.connect(self.basis_gen_bond)
        self.basis_button_bond_draw.clicked.connect(self.basis_add_bond)

        self.basis_combo_vector_type.currentTextChanged.connect(lambda x: self.basis.update({"vector_type": x}))
        self.basis_edit_vector.returnPressed.connect(self.basis_gen_vector)
        self.basis_combo_vector_samb_type.currentIndexChanged.connect(self.basis_set_vector_select)
        self.basis_button_vector_draw.clicked.connect(self.basis_add_vector)
        self.basis_edit_vector_lc.returnPressed.connect(self.basis_add_vector_lc)
        self.basis_combo_vector_modulation_type.currentTextChanged.connect(
            lambda x: self.basis.update({"vector_modulation_type": x})
        )
        self.basis_button_vector_modulation.clicked.connect(self.basis_gen_vector_modulation)

        self.basis_combo_orbital_type.currentTextChanged.connect(lambda x: self.basis.update({"orbital_type": x}))
        self.basis_combo_orbital_rank.currentTextChanged.connect(lambda x: self.basis.update({"orbital_rank": int(x)}))
        self.basis_edit_orbital.returnPressed.connect(self.basis_gen_orbital)
        self.basis_combo_orbital_samb_type.currentIndexChanged.connect(self.basis_set_orbital_select)
        self.basis_button_orbital_draw.clicked.connect(self.basis_add_orbital)
        self.basis_edit_orbital_lc.returnPressed.connect(self.basis_add_orbital_lc)
        self.basis_combo_orbital_modulation_type.currentTextChanged.connect(
            lambda x: self.basis.update({"orbital_modulation_type": x})
        )
        self.basis_button_orbital_modulation.clicked.connect(self.basis_gen_orbital_modulation)

        self.basis_edit_hopping.returnPressed.connect(self.basis_add_hopping)

    # ==================================================
    def set_group_item(self, point_group=None):
        """
        Set group widgets.

        Args:
            point_group (str, optional): point group.
        """
        if point_group is None:
            point_group = self.plus["point_group"]

        crystal = self.plus["crystal"]
        if point_group:
            lst = point_group_list[crystal]
        else:
            lst = space_group_list[crystal]

        self.group_combo_group.set_item(lst)

    # ==================================================
    def set_irrep_item(self):
        """
        Set irrep widgets.
        """
        self.group_combo_irrep1.set_item(self.plus["irrep"])
        self.group_combo_irrep2.set_item(self.plus["irrep"])
        self.group_combo_irrep.set_item(self.plus["irrep"])

    # ==================================================
    def set_wyckoff_item(self):
        """
        Set Wyckoff list.
        """
        self.group_combo_vc_wyckoff.set_item(self.plus["wyckoff"])

    # ==================================================
    def set_basis_item(self):
        """
        Set basis widgets.
        """
        if self.group["atomic_basis_type"] == "lm":
            lst = ["s", "p", "d", "f"]
        else:
            lst = [
                "(1/2,0)",
                "(1/2,1)",
                "(3/2,1)",
                "(3/2,2)",
                "(5/2,2)",
                "(5/2,3)",
                "(7/2,3)",
            ]
        self.group_combo_atomic_bra_basis.set_item(lst)
        self.group_combo_atomic_ket_basis.set_item(lst)

    # ==================================================
    def set_harmonics_item(self):
        """
        Set harmonics widgets.
        """
        lst = self.plugin.get_harmonics_irrep()
        self.object_combo_harmonics_irrep.set_item(lst)

    # ==================================================
    def set_group_type(self, index):
        """
        Set group type.

        Args:
            index (int): 0 (to SG), 1 (to PG).
        """
        to_pg = index == 1
        if to_pg == self.plus["point_group"]:
            return

        if to_pg:
            tag = str(self.plugin._point_group)
        else:
            tag = self.group["group"].replace("-1", "") + "^1"

        self.group["group"] = tag
        self.plugin.set_group()
        self.set_group_item(to_pg)

        no = self.group_combo_group.find_index(self.group["group"])[0]
        self.group_combo_group.setCurrentIndex(no)

        self.set_group(tag)

    # ==================================================
    def set_crystal_type(self, crystal):
        """
        Set crystal type.

        Args:
            crystal (str): crystal type.
        """
        if crystal == self.plus["crystal"]:
            return

        self.plus["crystal"] = crystal
        self.plugin.parent._set_crystal(crystal)

        self.set_group_item()

        tag = self.group_combo_group.currentText()
        self.set_group(tag)

    # ==================================================
    def set_group(self, tag):
        """
        Set current group.

        Args:
            tag (TagGroup or str): group tag.
        """
        if tag.count(" ") > 0:
            tag = tag.split(" ")[1]

        if tag == self.group["group"]:
            return

        self.group["group"] = tag
        self.plugin.set_group()

        self.set_wyckoff_item()
        self.set_harmonics_item()
        self.set_irrep_item()
        self.set_irrep_decomp()

    # ==================================================
    def set_irrep_decomp(self):
        """
        Set decomposition of product of irreps.
        """
        irrep1 = self.group_combo_irrep1.currentText()
        irrep2 = self.group_combo_irrep2.currentText()
        irrep = self.group_combo_irrep.currentText()

        self.group["irrep1"] = irrep1
        self.group["irrep2"] = irrep2
        self.group["irrep"] = irrep

        s, a = self.plugin.get_product_decomp(irrep1, irrep2, irrep)

        self.group_label_symmetric_decomp.setText("   =   " + s)
        self.group_label_antisymmetric_decomp.setText("   =   " + a)

    # ==================================================
    def set_harmonics_type(self, h_type):
        """
        Set harmonics type.

        Args:
            h_type (str): harmonics type.
        """
        self.group["harmonics_type"] = h_type

    # ==================================================
    def set_harmonics_rank(self, rank):
        """
        Set harmonics rank.

        Args:
            rank (str): harmonics rank.
        """
        self.group["harmonics_rank"] = int(rank)

    # ==================================================
    def set_harmonics_decomp(self, to_pg):
        """
        Set harmonics decomposition.

        Args:
            to_pg (str): destination point group.
        """
        if to_pg.count(" ") > 0:
            to_pg = to_pg.split(" ")[1]
        self.group["harmonics_decomp"] = to_pg

    # ==================================================
    def set_vc_wyckoff(self, wp):
        """
        Set wyckoff in virtual cluster.

        Args:
            wp (str): Wyckoff position.
        """
        self.group["vc_wyckoff"] = wp

    # ==================================================
    def set_vc_neighbor(self):
        """
        Set neighbor list in virtual cluster.
        """
        self.group["vc_neighbor"] = self.group_edit_vc_neighbor.text()

    # ==================================================
    def set_atomic_type(self, a_type):
        """
        Set atomic multipole type.

        Args:
            a_type (str): atomic multipole type.
        """
        self.group["atomic_type"] = a_type

    # ==================================================
    def set_atomic_basis_type(self, basis_type):
        """
        Set atomic multipole basis type.

        Args:
            basis_type (str): basis type.
        """
        if basis_type == self.group["atomic_basis_type"]:
            return

        self.group["atomic_basis_type"] = basis_type

        self.set_basis_item()

        self.group_combo_atomic_bra_basis.setCurrentIndex(0)
        self.group_combo_atomic_ket_basis.setCurrentIndex(0)

    # ==================================================
    def set_atomic_bra_ket(self):
        """
        Set bra and ket basis of atomic multipole.
        """
        self.group["atomic_bra"] = self.group_combo_atomic_bra_basis.currentText()
        self.group["atomic_ket"] = self.group_combo_atomic_ket_basis.currentText()

    # ==================================================
    def set_response_type(self, r_type):
        """
        Set type of response tensor.

        Args:
            r_type (str): type of response tensor.
        """
        self.group["response_type"] = r_type

    # ==================================================
    def set_response_rank(self, rank):
        """
        Set rank of response tensor.

        Args:
            rank (str): rank of response tensor.
        """
        self.group["response_rank"] = int(rank)

    # ==================================================
    def set_obj_vector_type(self, v_type):
        """
        Set vector type in object panel.

        Args:
            v_type (str): vector type.
        """
        self.obj["vector_type"] = v_type

    # ==================================================
    def set_obj_orbital_type(self, o_type):
        """
        Set orbital type in object panel.

        Args:
            o_type (str): orbital type.
        """
        self.obj["orbital_type"] = o_type

    # ==================================================
    def set_obj_harmonics_type(self):
        """
        Set harmonics type in object panel.
        """
        h_type = self.object_combo_harmonics_type.currentText()
        self.obj["harmonics_type"] = h_type
        self.obj["harmonics_irrep"] = 0
        self.set_harmonics_item()
        self.object_combo_harmonics_irrep.setCurrentIndex(0)
        self.set_obj_harmonics()

    # ==================================================
    def set_obj_harmonics_rank(self):
        """
        Set harmonics rank in object panel.
        """
        rank = int(self.object_combo_harmonics_rank.currentText())
        self.obj["harmonics_rank"] = rank
        self.obj["harmonics_irrep"] = 0
        self.set_harmonics_item()
        self.object_combo_harmonics_irrep.setCurrentIndex(0)
        self.set_obj_harmonics()

    # ==================================================
    def set_obj_harmonics(self):
        """
        Set harmonics in object panel.
        """
        irrep = self.object_combo_harmonics_irrep.currentIndex()
        check = self.object_check_harmonics_latex.is_checked()
        self.obj["harmonics_irrep"] = irrep
        self.obj["harmonics_latex"] = check

        ex = self.plugin.get_harmonics()
        self.object_edit_harmonics_ex.setText(ex)

    # ==================================================
    def set_obj_wyckoff(self):
        """
        Set Wyckoff position in object panel.
        """
        wyckoff = self.object_edit_wyckoff.text()
        self.obj["wyckoff"] = wyckoff

        # find WP and write.
        wp, sym = self.plugin.find_wyckoff()
        self.object_edit_wyckoff_position.setText(wp)
        self.object_edit_wyckoff_symmetry.setText(sym)

    # ==================================================
    def show_symmetry_operation(self):
        """
        Show symmetry operation panel.
        """
        self._symmetry_operation_dialog = show_symmetry_operation(self.plugin._group, self)

    # ==================================================
    def show_character_table(self):
        """
        Show character table panel.
        """
        self._character_table_dialog = show_character_table(self.plugin._point_group, self)

    # ==================================================
    def show_wyckoff(self):
        """
        Show Wyckoff position panel.
        """
        self._wyckoff_dialog = show_wyckoff(self.plugin._group, self)

    # ==================================================
    def show_product_table(self):
        """
        Show product table panel.
        """
        self._product_table_dialog = show_product_table(self.plugin._point_group, self)

    # ==================================================
    def show_harmonics(self):
        """
        Show harmonics panel.
        """
        head = self.group_combo_harmonics_type.currentText()
        rank = int(self.group_combo_harmonics_rank.currentText())
        self._harmonics_dialog = show_harmonics(self.plugin._point_group, rank, head, self)

        self.plugin.add_harmonics_set(head, rank)

    # ==================================================
    def show_harmonics_decomp(self):
        """
        Show harmonics decomposition panel.
        """
        head = self.group_combo_harmonics_type.currentText()
        rank = int(self.group_combo_harmonics_rank.currentText())
        to_pg = self.group_combo_harmonics_decomp.currentText()
        self._harmonics_decomp_dialog = show_harmonics_decomp(self.plugin._point_group, rank, head, to_pg, self)

    # ==================================================
    def show_virtual_cluster(self):
        """
        Show virtual cluster panel.
        """
        wp = self.group_combo_vc_wyckoff.currentText()
        bond = self.group_edit_vc_neighbor.text()
        self._virtual_cluster_dialog = show_virtual_cluster(self.plugin._point_group, wp, self)

        self.plugin.add_virtual_cluster(wp, bond)

    # ==================================================
    def show_atomic(self):
        """
        Show atomic multipole panel.
        """
        head = self.group_combo_atomic_type.currentText()
        btype = self.group_combo_atomic_basis_type.currentText()
        bra = self.group_combo_atomic_bra_basis.currentText()
        ket = self.group_combo_atomic_ket_basis.currentText()

        spinful = btype == "jm"
        bra = parse_orb_list(bra, spinful, self.plugin._point_group.symmetry_operation.crystal)
        ket = parse_orb_list(ket, spinful, self.plugin._point_group.symmetry_operation.crystal)
        am = self.plugin._point_group.atomic_samb(bra, ket, spinful)
        if head != "":
            am = {tag: m for tag, m in am.items() if tag.head == head}

        self._atomic_dialog = show_atomic_multipole(self.plugin._point_group, bra, ket, am, self)

    # ==================================================
    def show_response(self):
        """
        Show response tensor panel.
        """
        rank = int(self.group_combo_response_rank.currentText())
        r_type = self.group_combo_response_type.currentText()
        self._response_dialog = show_response(self.plugin._point_group, rank, r_type, self)

    # ==================================================
    def obj_add_site(self, scale=1.0, color=None):
        """
        Add representative site in object dict.

        Args:
            scale (float, optional): size scale.
            color (str, optional): color.
        """
        site = self.object_edit_site.text()
        r_site = self.plugin.add_equivalent_site(site, scale, color)
        if r_site is not None:
            self.obj["site"] = r_site

    # ==================================================
    def obj_add_bond(self, scale=1.0, color=None, color2=None):
        """
        Add representative bond in object dict.

        Args:
            scale (float, optional): width scale.
            color (str, optional): color.
            color2 (str, optional): color2.
        """
        bond = self.object_edit_bond.text()
        r_bond = self.plugin.add_equivalent_bond(bond, scale, color, color2)
        if r_bond is not None:
            self.obj["bond"] = r_bond

    # ==================================================
    def obj_add_vector(self, scale=1.0):
        """
        Add equivalent vectors in object dict.

        Args:
            scale (float, optional): length scale.
        """
        v_type = self.object_combo_vector_type.currentText()
        pos = self.object_edit_vector.text()
        pos = self.plugin.add_vector_equivalent_site(v_type, pos, scale)
        if pos is not None:
            self.obj["vector"] = pos

    # ==================================================
    def obj_add_orbital(self, scale=1.0):
        """
        Add equivalent orbitals in object dict.

        Args:
            scale (float, optional): size scale.
        """
        o_type = self.object_combo_orbital_type.currentText()
        pos = self.object_edit_orbital.text()
        pos = self.plugin.add_orbital_equivalent_site(o_type, pos, scale)
        if pos is not None:
            self.obj["orbital"] = pos

    # ==================================================
    def obj_add_harmonics(self, scale=1.0):
        """
        Add equivalent poing-group harmonics in object dict.

        Args:
            scale (float, optional): size scale.
        """
        o_type = self.object_combo_harmonics_type.currentText()
        orbital = self.plugin.get_harmonics()
        txt = self.object_edit_harmonics.text()
        pos = orbital + "#" + txt
        pos = self.plugin.add_orbital_equivalent_site(o_type, pos, scale)
        if pos is not None:
            self.obj["harmonics"] = pos

    # ==================================================
    def basis_gen_site(self):
        """
        Generate site cluster SAMB.
        """
        pos = self.basis_edit_site.text()
        pos = self.plugin.gen_site_samb(pos)
        self.basis["site"] = pos

        return self.basis_set_site_select()

    # ==================================================
    def basis_set_site_select(self):
        """
        Set site cluster SAMB selection list.
        """
        z_samb = self.plus["site_z_samb"]
        if len(z_samb) == 0:
            return

        select = z_samb["Q"]

        lst = [f"{i[0][0]}{no+1:02d}: {i[0]}" for no, i in enumerate(select)]

        self.basis_combo_site_samb.set_item(lst)
        self.basis_combo_site_samb.setCurrentIndex(0)

        return lst

    # ==================================================
    def basis_add_site(self, scale=None):
        """
        Add site cluster SAMB.

        Args:
            scale (float, optional): size scale.
        """
        z_samb = self.plus["site_z_samb"]
        if len(z_samb) == 0:
            return

        samb = self.basis_combo_site_samb.currentIndex()
        samb_str = self.basis_combo_site_samb.currentText()
        cluster = self.plus["site_cluster"]
        r_site = self.basis_edit_site.text()

        v = NSArray.vector3d()
        cluster_obj = create_samb_object(
            z_samb,
            cluster,
            self.plus["site_c_samb"],
            "Q",
            samb,
            self.plugin._point_group,
            v,
            False,
        )
        label = samb_str[:3] + " \u21d0 " + remove_space(r_site)
        self.plugin.add_site_samb(cluster, cluster_obj, label, scale)

    # ==================================================
    def basis_gen_bond(self):
        """
        Generate bond cluster SAMB.
        """
        pos = self.basis_edit_bond.text()
        pos = self.plugin.gen_bond_samb(pos)
        self.basis["bond"] = pos

        return self.basis_set_bond_select()

    # ==================================================
    def basis_set_bond_select(self):
        """
        Set bond cluster SAMB selection list.
        """
        z_samb = self.plus["bond_z_samb"]
        if len(z_samb) == 0:
            return

        select = z_samb["Q"] + z_samb["T"]
        qn = len(z_samb["Q"])

        lst = [f"Q{no+1:02d}: {i[0]}" if i[0][0] == "Q" else f"T{no+1-qn:02d}: {i[0]}" for no, i in enumerate(select)]

        self.basis_combo_bond_samb.set_item(lst)
        self.basis_combo_bond_samb.setCurrentIndex(0)

        return lst

    # ==================================================
    def basis_add_bond(self, scale=None):
        """
        Add bond cluster SAMB.

        Args:
            scale (float, optional): width scale.
        """
        z_samb = self.plus["bond_z_samb"]
        if len(z_samb) == 0:
            return

        samb = self.basis_combo_bond_samb.currentIndex()
        samb_str = self.basis_combo_bond_samb.currentText()
        cluster = self.plus["bond_cluster"]
        r_bond = self.basis_edit_bond.text()

        z_type = self.basis_combo_bond_samb.currentText()[0]
        if z_type == "T":
            samb -= len(z_samb["Q"])
        t_odd = z_type != "Q"

        v = NSArray.vector3d()
        cluster_obj = create_samb_object(
            z_samb,
            cluster,
            self.plus["bond_c_samb"],
            z_type,
            samb,
            self.plugin._point_group,
            v,
            t_odd,
        )
        label = samb_str[:3] + " \u21d0 " + remove_space(r_bond)
        self.plugin.add_bond_samb(cluster, cluster_obj, label, z_type, scale)

    # ==================================================
    def basis_gen_vector(self):
        """
        Generate vector cluster SAMB.
        """
        pos = self.basis_edit_vector.text()
        v_type = self.basis_combo_vector_type.currentText()
        pos = self.plugin.gen_vector_samb(pos, v_type)
        self.basis["vector"] = pos

        self.basis_set_vector_select()

    # ==================================================
    def basis_set_vector_select(self):
        """
        Set vector cluster SAMB selection list.
        """
        z_type = self.basis_combo_vector_samb_type.currentText()
        self.basis["vector_samb_type"] = z_type

        z_samb = self.plus["vector_z_samb"]
        if len(z_samb) == 0:
            return

        select = z_samb[z_type]

        lst = [f"{i[0][0]}{no+1:02d}: {i[0]}" for no, i in enumerate(select)]

        self.basis_combo_vector_samb.set_item(lst)
        self.basis_combo_vector_samb.setCurrentIndex(0)

    # ==================================================
    def basis_add_vector(self):
        """
        Add vector cluster SAMB.
        """
        z_samb = self.plus["vector_z_samb"]
        if len(z_samb) == 0:
            return

        z_type = self.basis_combo_vector_samb_type.currentText()
        v_type = self.basis_combo_vector_type.currentText()
        samb = self.basis_combo_vector_samb.currentIndex()
        samb_str = self.basis_combo_vector_samb.currentText()
        r_site_bond = self.basis_edit_vector.text()
        cluster = self.plus["vector_cluster"]

        t_odd = v_type.replace("M", "T").replace("G", "Q") != z_type.replace("M", "T").replace("G", "Q")

        v = NSArray.vector3d()
        cluster_obj = create_samb_object(
            z_samb,
            cluster,
            self.plus["vector_c_samb"],
            z_type,
            samb,
            self.plugin._point_group,
            v,
            t_odd,
        )

        label = samb_str[:3] + " \u21d0 " + v_type + ", " + remove_space(r_site_bond)
        self.plugin.add_vector_samb(cluster, cluster_obj, label, v_type, v)

    # ==================================================
    def basis_add_vector_lc(self, scale=1.0):
        """
        Add linear combination of vector cluster SAMB.

        Args:
            scale (float, optional): length scale.
        """
        z_samb = self.plus["vector_z_samb"]
        if len(z_samb) == 0:
            return

        z_type = self.basis_combo_vector_samb_type.currentText()
        r_site_bond = self.basis_edit_vector.text()
        lc = self.basis_edit_vector_lc.text()
        cluster = self.plus["vector_cluster"]
        form, ex_var, t_odd = check_linear_combination(z_samb, lc, z_type)
        if form is None:
            self.basis["vector_lc"] = ""
            return
        self.basis["vector_lc"] = lc

        v = NSArray.vector3d()
        lc_basis = {
            i: sp.Matrix(
                create_samb_object(
                    z_samb,
                    cluster,
                    self.plus["vector_c_samb"],
                    i[0].upper(),
                    int(i[1:]) - 1,
                    self.plugin._point_group,
                    v,
                    t_odd,
                ).tolist()
            )
            for i in ex_var
        }
        cluster_obj = NSArray(str(NSArray(form).subs(lc_basis).tolist().T.tolist()[0]))

        label = remove_space(lc) + " \u21d0 " + z_type + ", " + remove_space(r_site_bond)

        self.plugin.add_vector_samb(cluster, cluster_obj, label, z_type, v, scale)

    # ==================================================
    def basis_gen_vector_modulation(self):
        """
        Generate vector modulation.
        """
        z_samb = self.plus["vector_z_samb"]
        if len(z_samb) == 0:
            return

        if self.basis_combo_vector_modulation_type.currentText() == "Q,G":
            basis = [f"Q{i+1:02d}" for i in range(len(z_samb["Q"]))] + [f"G{i+1:02d}" for i in range(len(z_samb["G"]))]
        else:
            basis = [f"T{i+1:02d}" for i in range(len(z_samb["T"]))] + [f"M{i+1:02d}" for i in range(len(z_samb["M"]))]
        if len(basis) < 1:
            return

        head = self.basis_combo_vector_type.currentText()
        modulation = self.basis_edit_vector_modulation.text()

        self._vector_modulation_dialog = ModulationDialog(self.plugin._pvw, basis, modulation, head, False, self)

    # ==================================================
    def basis_gen_orbital(self):
        """
        Generate orbital cluster SAMB.
        """
        pos = self.basis_edit_orbital.text()
        o_type = self.basis_combo_orbital_type.currentText()
        rank = self.basis_combo_orbital_rank.currentText()
        pos = self.plugin.gen_orbital_samb(pos, o_type, rank)
        self.basis["orbital"] = pos

        self.basis_set_orbital_select()

    # ==================================================
    def basis_set_orbital_select(self):
        """
        Set orbital cluster SAMB selection list.
        """
        z_type = self.basis_combo_orbital_samb_type.currentText()
        self.basis["orbital_samb_type"] = z_type

        z_samb = self.plus["orbital_z_samb"]
        if len(z_samb) == 0:
            return

        select = z_samb[z_type]

        lst = [f"{i[0][0]}{no+1:02d}: {i[0]}" for no, i in enumerate(select)]

        self.basis_combo_orbital_samb.set_item(lst)
        self.basis_combo_orbital_samb.setCurrentIndex(0)

    # ==================================================
    def basis_add_orbital(self):
        """
        Add orbital cluster SAMB.
        """
        z_samb = self.plus["orbital_z_samb"]
        if len(z_samb) == 0:
            return

        z_type = self.basis_combo_orbital_samb_type.currentText()
        o_type = self.basis_combo_orbital_type.currentText()
        rank = self.basis_combo_orbital_rank.currentText()
        samb = self.basis_combo_orbital_samb.currentIndex()
        samb_str = self.basis_combo_orbital_samb.currentText()
        r_site_bond = self.basis_edit_orbital.text()
        cluster = self.plus["orbital_cluster"]

        t_odd = o_type.replace("M", "T").replace("G", "Q") != z_type.replace("M", "T").replace("G", "Q")

        v = NSArray.vector3d()
        cluster_obj = create_samb_object(
            z_samb,
            cluster,
            self.plus["orbital_c_samb"],
            z_type,
            samb,
            self.plugin._point_group,
            v,
            t_odd,
        )

        label = samb_str[:3] + " \u21d0 " + o_type + rank + ", " + remove_space(r_site_bond)
        self.plugin.add_orbital_samb(cluster, cluster_obj, label, o_type)

    # ==================================================
    def basis_add_orbital_lc(self, scale=1.0):
        """
        Add linear combination of orbital cluster SAMB.

        Args:
            scale (float, optional): size scale.
        """
        z_samb = self.plus["orbital_z_samb"]
        if len(z_samb) == 0:
            return

        z_type = self.basis_combo_orbital_samb_type.currentText()
        rank = self.basis_combo_orbital_rank.currentText()
        lc = self.basis_edit_orbital_lc.text()
        r_site_bond = self.basis_edit_orbital.text()
        cluster = self.plus["orbital_cluster"]
        form, ex_var, t_odd = check_linear_combination(z_samb, lc, z_type)
        if form is None:
            self.basis["orbital_lc"] = ""
            return
        self.basis["orbital_lc"] = lc

        v = NSArray.vector3d()
        lc_basis = {
            i: sp.Matrix(
                create_samb_object(
                    z_samb,
                    cluster,
                    self.plus["orbital_c_samb"],
                    i[0].upper(),
                    int(i[1:]) - 1,
                    self.plugin._point_group,
                    v,
                    t_odd,
                ).tolist()
            )
            for i in ex_var
        }
        cluster_obj = NSArray(str(NSArray(form).subs(lc_basis).tolist().T.tolist()[0]))

        label = remove_space(lc) + " \u21d0 " + z_type + rank + ", " + remove_space(r_site_bond)
        self.plugin.add_orbital_samb(cluster, cluster_obj, label, z_type, scale)

    # ==================================================
    def basis_gen_orbital_modulation(self):
        """
        Generate orbital modulation.
        """
        z_samb = self.plus["orbital_z_samb"]
        if len(z_samb) == 0:
            return

        if self.basis_combo_orbital_modulation_type.currentText() == "Q,G":
            basis = [f"Q{i+1:02d}" for i in range(len(z_samb["Q"]))] + [f"G{i+1:02d}" for i in range(len(z_samb["G"]))]
        else:
            basis = [f"T{i+1:02d}" for i in range(len(z_samb["T"]))] + [f"M{i+1:02d}" for i in range(len(z_samb["M"]))]
        if len(basis) < 1:
            return

        head = self.basis_combo_orbital_type.currentText()
        modulation = self.basis_edit_orbital_modulation.text()

        self._orbital_modulation_dialog = ModulationDialog(self.plugin._pvw, basis, modulation, head, True, self)

    # ==================================================
    def basis_add_hopping(self, scale=1.0):
        """
        Add hopping SAMB.

        Args:
            scale (float, optional): length scale.
        """
        pos = self.basis_edit_hopping.text()
        pos = self.plugin.gen_hopping_samb(pos)
        self.basis["hopping"] = pos

        if pos != "":
            bond = self.plugin.create_hopping_direction(pos)
            label = "T \u21d0 " + remove_space(str(pos))

            self.plugin.add_hopping_samb(bond, label, scale)

    # ==================================================
    def close(self):
        """
        Close dialogs.
        """
        if self._symmetry_operation_dialog is not None:
            self._symmetry_operation_dialog.close()
        if self._character_table_dialog is not None:
            self._character_table_dialog.close()
        if self._wyckoff_dialog is not None:
            self._wyckoff_dialog.close()
        if self._product_table_dialog is not None:
            self._product_table_dialog.close()
        if self._harmonics_dialog is not None:
            self._harmonics_dialog.close()
        if self._harmonics_decomp_dialog is not None:
            self._harmonics_decomp_dialog.close()
        if self._virtual_cluster_dialog is not None:
            self._virtual_cluster_dialog.close()
        if self._atomic_dialog is not None:
            self._atomic_dialog.close()
        if self._response_dialog is not None:
            self._response_dialog.close()
        if self._vector_modulation_dialog is not None:
            self._vector_modulation_dialog.close()
        if self._orbital_modulation_dialog is not None:
            self._orbital_modulation_dialog.close()
        super().close()
