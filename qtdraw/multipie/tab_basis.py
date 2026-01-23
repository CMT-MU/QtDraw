"""
Multipie basis tab.

This module provides basis tab in MultiPie dialog.
"""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt

from qtdraw.widget.custom_widget import Label, Layout, Button, Combo, VSpacer, HBar, LineEdit
from qtdraw.multipie.multipie_modulation_dialog import ModulationDialog
from qtdraw.multipie.multipie_info_dialog import (
    show_site_samb_panel,
    show_bond_samb_panel,
    show_vector_samb_panel,
    show_orbital_samb_panel,
)


# ==================================================
class TabBasis(QWidget):
    # ==================================================
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.data = parent._data

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
        self.edit_def_bond = LineEdit(parent, text="", validator=("bond", {"use_var": False}))

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
        self.edit_site = LineEdit(parent, text="", validator=("site", {"use_var": False}))

        label_site_to = Label(parent, text="\u21d2 basis")
        self.combo_site_samb = Combo(parent)
        self.button_site_draw = Button(parent, text="draw")
        self.button_site_info = Button(parent, text="info")

        panel2 = QWidget(parent)
        layout2 = Layout(panel2)
        layout2.addWidget(label_site, 0, 0, 1, 10)
        layout2.addWidget(self.edit_site, 1, 0, 1, 10)
        layout2.addWidget(label_site_to, 2, 0, 1, 1, Qt.AlignRight)
        layout2.addWidget(self.combo_site_samb, 2, 1, 1, 7)
        layout2.addWidget(self.button_site_draw, 2, 8, 1, 1)
        layout2.addWidget(self.button_site_info, 2, 9, 1, 1)

        # bond samb.
        label_bond = Label(
            parent,
            text='<span style="font-weight:bold;">Bond</span> : draw bond-cluster basis.<br>&nbsp;&nbsp;1. input representative bond, + ENTER, \u21d2 2. choose basis, 3. push "draw".',
        )
        self.edit_bond = LineEdit(parent, text="", validator=("bond", {"use_var": False}))
        label_bond_to = Label(parent, text="\u21d2 basis")
        self.combo_bond_samb = Combo(parent)
        self.button_bond_draw = Button(parent, text="draw")
        self.button_bond_info = Button(parent, text="info")

        panel3 = QWidget(parent)
        layout3 = Layout(panel3)
        layout3.addWidget(label_bond, 0, 0, 1, 10)
        layout3.addWidget(self.edit_bond, 1, 0, 1, 10)
        layout3.addWidget(label_bond_to, 2, 0, 1, 1, Qt.AlignRight)
        layout3.addWidget(self.combo_bond_samb, 2, 1, 1, 7)
        layout3.addWidget(self.button_bond_draw, 2, 8, 1, 1)
        layout3.addWidget(self.button_bond_info, 2, 9, 1, 1)

        # vector samb.
        label_vector = Label(
            parent,
            text='<span style="font-weight:bold;">Vector</span> : draw symmetry-adapted vector.<br>&nbsp;&nbsp;1. choose type, 2. input representative site/bond, + ENTER,<br>&nbsp;&nbsp;\u21d2  3. choose (type,basis), 4. push "draw" or 3. input linear combination, + ENTER or 3. push "modulation".',
        )
        self.combo_vector_type = Combo(parent, ["Q", "G", "T", "M"])
        self.edit_vector = LineEdit(parent, text="", validator=("site_bond", {"use_var": False}))
        label_vector_to = Label(parent, text="\u21d2 basis")
        self.combo_vector_samb_type = Combo(parent, ["Q", "G", "T", "M"])
        self.combo_vector_samb = Combo(parent)
        self.button_vector_draw = Button(parent, text="draw")
        self.button_vector_info = Button(parent, text="info")
        label_vector_lc = Label(parent, text="linear combination")
        self.edit_vector_lc = LineEdit(parent, text="")
        self.button_vector_modulation = Button(parent, text="modulation (SG)")
        self.edit_vector_modulation = LineEdit(parent, text="")

        panel4 = QWidget(parent)
        layout4 = Layout(panel4)
        layout4.addWidget(label_vector, 0, 0, 1, 10)
        layout4.addWidget(self.combo_vector_type, 1, 0, 1, 1)
        layout4.addWidget(self.edit_vector, 1, 1, 1, 9)
        layout4.addWidget(label_vector_to, 2, 0, 1, 1, Qt.AlignRight)
        layout4.addWidget(self.combo_vector_samb_type, 2, 1, 1, 1)
        layout4.addWidget(self.combo_vector_samb, 2, 2, 1, 6)
        layout4.addWidget(self.button_vector_draw, 2, 8, 1, 1)
        layout4.addWidget(self.button_vector_info, 2, 9, 1, 1)
        layout4.addWidget(label_vector_lc, 3, 0, 1, 1, Qt.AlignRight)
        layout4.addWidget(self.edit_vector_lc, 3, 1, 1, 9)
        layout4.addWidget(self.button_vector_modulation, 4, 0, 1, 1)
        layout4.addWidget(self.edit_vector_modulation, 4, 1, 1, 8)

        # orbital samb.
        label_orbital = Label(
            parent,
            text='<span style="font-weight:bold;">Orbital</span> : draw symmetry-adapted orbital.<br>&nbsp;&nbsp;1. choose (type,rank), 2. input representative site/bond, + ENTER,<br>&nbsp;&nbsp;\u21d2  3. choose (type,basis), 4. push "draw" or 3. input linear combination, + ENTER or 3. push "modulation".',
        )
        self.combo_orbital_type = Combo(parent, ["Q", "G", "T", "M"])
        self.combo_orbital_rank = Combo(parent, map(str, range(12)))
        self.edit_orbital = LineEdit(parent, text="", validator=("site_bond", {"use_var": False}))
        label_orbital_to = Label(parent, text="\u21d2 basis")
        self.combo_orbital_samb_type = Combo(parent, ["Q", "G", "T", "M"])
        self.combo_orbital_samb = Combo(parent)
        self.button_orbital_draw = Button(parent, text="draw")
        self.button_orbital_info = Button(parent, text="info")

        label_orbital_lc = Label(parent, text="linear combination")
        self.edit_orbital_lc = LineEdit(parent, text="")
        self.button_orbital_modulation = Button(parent, text="modulation (SG)")
        self.edit_orbital_modulation = LineEdit(parent, text="")

        panel5 = QWidget(parent)
        layout5 = Layout(panel5)
        layout5.addWidget(label_orbital, 0, 0, 1, 10)
        layout5.addWidget(self.combo_orbital_type, 1, 0, 1, 1)
        layout5.addWidget(self.combo_orbital_rank, 1, 1, 1, 1)
        layout5.addWidget(self.edit_orbital, 1, 2, 1, 8)
        layout5.addWidget(label_orbital_to, 2, 0, 1, 1, Qt.AlignRight)
        layout5.addWidget(self.combo_orbital_samb_type, 2, 1, 1, 1)
        layout5.addWidget(self.combo_orbital_samb, 2, 2, 1, 6)
        layout5.addWidget(self.button_orbital_draw, 2, 8, 1, 1)
        layout5.addWidget(self.button_orbital_info, 2, 9, 1, 1)
        layout5.addWidget(label_orbital_lc, 3, 0, 1, 1, Qt.AlignRight)
        layout5.addWidget(self.edit_orbital_lc, 3, 1, 1, 9)
        layout5.addWidget(self.button_orbital_modulation, 4, 0, 1, 1)
        layout5.addWidget(self.edit_orbital_modulation, 4, 1, 1, 8)

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

        # connections.
        self.edit_def_bond.returnPressed.connect(self.show_bond_definition)
        self.edit_site.returnPressed.connect(self.set_site)
        self.edit_bond.returnPressed.connect(self.set_bond)
        self.edit_vector.returnPressed.connect(self.set_vector)
        self.edit_orbital.returnPressed.connect(self.set_orbital)
        self.button_site_draw.clicked.connect(self.show_site)
        self.button_site_info.clicked.connect(self.show_site_info)
        self.button_bond_draw.clicked.connect(self.show_bond)
        self.button_bond_info.clicked.connect(self.show_bond_info)
        self.combo_vector_samb_type.currentTextChanged.connect(self.set_vector_list)
        self.combo_orbital_samb_type.currentTextChanged.connect(self.set_orbital_list)
        self.button_vector_draw.clicked.connect(self.show_vector)
        self.button_vector_info.clicked.connect(self.show_vector_info)
        self.button_orbital_draw.clicked.connect(self.show_orbital)
        self.button_orbital_info.clicked.connect(self.show_orbital_info)
        self.edit_vector_lc.returnPressed.connect(self.show_vector_lc)
        self.edit_orbital_lc.returnPressed.connect(self.show_orbital_lc)
        self.button_vector_modulation.released.connect(self.create_vector_modulation)
        self.button_orbital_modulation.released.connect(self.create_orbital_modulation)

    # ==================================================
    def set_site(self):
        site = self.edit_site.raw_text()
        lst = self.data.site_samb_list(site)
        self.combo_site_samb.set_item(lst)
        self.combo_site_samb.setCurrentIndex(0)

    # ==================================================
    def show_site_info(self):
        if len(self.data._site_list) == 0:
            return

        if self._site_samb_dialog is not None:
            self._site_samb_dialog.close()

        self._site_samb_dialog = show_site_samb_panel(
            self.data.ps_group, self.data._site_list, self.data._site_wp, self.data._site_samb_list, self.data._site_samb, self
        )

    # ==================================================
    def set_bond(self):
        bond = self.edit_bond.raw_text()
        lst = self.data.bond_samb_list(bond)
        self.combo_bond_samb.set_item(lst)
        self.combo_bond_samb.setCurrentIndex(0)

    # ==================================================
    def show_bond_info(self):
        if len(self.data._bond_list) == 0:
            return

        if self._bond_samb_dialog is not None:
            self._bond_samb_dialog.close()

        self._bond_samb_dialog = show_bond_samb_panel(
            self.data.ps_group, self.data._bond_list, self.data._bond_wp, self.data._bond_samb_list, self.data._bond_samb, self
        )

    # ==================================================
    def set_vector(self):
        site_bond = self.edit_vector.raw_text()
        vector_type = self.combo_vector_type.currentText()
        self.data.vector_samb_list(site_bond, vector_type)
        self.set_vector_list()

    # ==================================================
    def show_vector_info(self):
        vector_type = self.combo_vector_samb_type.currentText()
        if len(self.data._vector_list[vector_type]) == 0:
            return

        if self._vector_samb_dialog is not None:
            self._vector_samb_dialog.close()

        self._vector_samb_dialog = show_vector_samb_panel(
            self.data.ps_group,
            self.data._vector_list[vector_type],
            self.data._vector_wp,
            self.combo_vector_type.currentText(),
            self.data._vector_samb_list[vector_type],
            self.data._vector_samb[vector_type],
            self,
        )

    # ==================================================
    def set_vector_list(self):
        vector_type = self.combo_vector_samb_type.currentText()
        self.combo_vector_samb.set_item(self.data._vector_list[vector_type])
        self.combo_vector_samb.setCurrentIndex(0)

    # ==================================================
    def set_orbital(self):
        site_bond = self.edit_orbital.raw_text()
        orbital_type = self.combo_orbital_type.currentText()
        orbital_rank = self.combo_orbital_rank.currentText()
        self.data.orbital_samb_list(site_bond, orbital_type, orbital_rank)
        self.set_orbital_list()

    # ==================================================
    def show_orbital_info(self):
        orbital_type = self.combo_orbital_samb_type.currentText()
        if len(self.data._orbital_list[orbital_type]) == 0:
            return

        if self._orbital_samb_dialog is not None:
            self._orbital_samb_dialog.close()

        self._orbital_samb_dialog = show_orbital_samb_panel(
            self.data.ps_group,
            self.data._orbital_list[orbital_type],
            self.data._orbital_wp,
            self.combo_orbital_type.currentText(),
            self.data._orbital_samb_list[orbital_type],
            self.data._orbital_samb[orbital_type],
            self,
        )

    # ==================================================
    def set_orbital_list(self):
        orbital_type = self.combo_orbital_samb_type.currentText()
        self.combo_orbital_samb.set_item(self.data._orbital_list[orbital_type])
        self.combo_orbital_samb.setCurrentIndex(0)

    # ==================================================
    def show_bond_definition(self):
        bond = self.edit_def_bond.raw_text()
        self.data.add_bond_definition(bond)

    # ==================================================
    def show_site(self):
        tag = self.combo_site_samb.currentText()
        self.data.add_site_samb(tag)

    # ==================================================
    def show_bond(self):
        tag = self.combo_bond_samb.currentText()
        self.data.add_bond_samb(tag)

    # ==================================================
    def show_vector(self):
        tag = self.combo_vector_samb.currentText().split(":")[0]
        self.data.add_vector_samb(tag)

    # ==================================================
    def show_vector_lc(self):
        lc = self.edit_vector_lc.raw_text()
        self.data.add_vector_samb(lc)

    # ==================================================
    def show_orbital(self):
        tag = self.combo_orbital_samb.currentText().split(":")[0]
        self.data.add_orbital_samb(tag)

    # ==================================================
    def show_orbital_lc(self):
        lc = self.edit_orbital_lc.raw_text()
        self.data.add_orbital_samb(lc)

    # ==================================================
    def create_vector_modulation(self):
        if sum([len(i) for i in self.data._vector_samb_var.values()]) == 0:
            return

        if not self.data.ps_group.is_point_group:
            modulation = self.edit_vector_modulation.text()
            self._vector_modulation_dialog = ModulationDialog(self, modulation, self.data._vector_samb_var, vec=True)

    # ==================================================
    def create_orbital_modulation(self):
        if sum([len(i) for i in self.data._orbital_samb_var.values()]) == 0:
            return

        if not self.data.ps_group.is_point_group:
            modulation = self.edit_orbital_modulation.text()
            self._orbital_modulation_dialog = ModulationDialog(self, modulation, self.data._orbital_samb_var, vec=False)

    # ==================================================
    def show_vector_samb_modulation(self, modulation_range):
        self.data.add_vector_samb_modulation(modulation_range)

    # ==================================================
    def show_orbital_samb_modulation(self, modulation_range):
        self.data.add_orbital_samb_modulation(modulation_range)

    # ==================================================
    def closeEvent(self, event):
        self.clear_data()
        super().closeEvent(event)

    # ==================================================
    def set_data(self):
        d = self.data.status["basis"]

        self.edit_def_bond.setText(d["bond_definition"])
        self.edit_site.setText(d["site"])
        self.edit_bond.setText(d["bond"])
        self.combo_vector_type.setCurrentText(d["vector_type"])
        self.edit_vector.setText(d["vector"])
        self.edit_vector_lc.setText(d["vector_lc"])
        self.edit_vector_modulation.setText(d["vector_modulation"])
        self.combo_orbital_type.setCurrentText(d["orbital_type"])
        self.combo_orbital_rank.setCurrentText(str(d["orbital_rank"]))
        self.edit_orbital.setText(d["orbital"])
        self.edit_orbital_lc.setText(d["orbital_lc"])
        self.edit_orbital_modulation.setText(d["orbital_modulation"])

        self._vector_modulation_dialog = None
        self._orbital_modulation_dialog = None
        self._site_samb_dialog = None
        self._bond_samb_dialog = None
        self._vector_samb_dialog = None
        self._orbital_samb_dialog = None

        self.combo_site_samb.set_item([])
        self.combo_bond_samb.set_item([])
        self.combo_vector_samb.set_item([])
        self.combo_orbital_samb.set_item([])

    # ==================================================
    def clear_data(self):
        if self._vector_modulation_dialog is not None:
            self._vector_modulation_dialog.close()
        if self._orbital_modulation_dialog is not None:
            self._orbital_modulation_dialog.close()
        if self._site_samb_dialog is not None:
            self._site_samb_dialog.close()
        if self._bone_samb_dialog is not None:
            self._bond_samb_dialog.close()
        if self._vector_samb_dialog is not None:
            self._vector_samb_dialog.close()
        if self._orbital_samb_dialog is not None:
            self._orbital_samb_dialog.close()

        self._vector_modulation_dialog = None
        self._orbital_modulation_dialog = None
        self._site_samb_dialog = None
        self._bond_samb_dialog = None
        self._vector_samb_dialog = None
        self._orbital_samb_dialog = None

        self.combo_site_samb.set_item([])
        self.combo_bond_samb.set_item([])
        self.combo_vector_samb.set_item([])
        self.combo_orbital_samb.set_item([])
