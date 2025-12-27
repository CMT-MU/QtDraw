"""
Multipie side panel.

This module provides side panel in MultiPie dialog.
"""

from PySide6.QtWidgets import QWidget

from qtdraw.widget.custom_widget import Label, Layout, Button, Combo, VSpacer, HBar
from qtdraw.multipie.multipie_info_dialog import (
    show_symmetry_operation,
    show_character_table,
    show_wyckoff_site,
    show_wyckoff_bond,
    show_product_table,
)


# ==================================================
class SubGroup(QWidget):
    # ==================================================
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.setMinimumWidth(270)
        layout = Layout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setHorizontalSpacing(30)
        layout.setVerticalSpacing(10)

        # widget.
        label_group = Label(parent, text="Group", bold=True)
        self._type_list = {"Point Group": "PG", "Space Group": "SG", "Magnetic Point Group": "MPG", "Magnetic Space Group": "MSG"}
        self.combo_group_type = Combo(parent, self._type_list.keys())
        self.combo_crystal_type = Combo(parent, parent._crystal_list.keys())
        self.combo_group = Combo(parent, [])
        label_assoc_group = Label(parent, text="Associated Group (PG/SG/MPG/MSG)", bold=True)
        self.label_pg_name = Label(parent, text="")
        self.label_sg_name = Label(parent, text="")
        self.label_mpg_name = Label(parent, text="")
        self.label_msg_name = Label(parent, text="")

        label_info = Label(parent, text="Info.", bold=True)
        self.button_symmetry_operation = Button(parent, text="Symmetry Operation")
        self.button_character_table = Button(parent, text="Character Table (PG)")
        self.button_wyckoff_site = Button(parent, text="Wyckoff Site (PG/SG)")
        self.button_wyckoff_bond = Button(parent, text="Wyckoff Bond (PG/SG)")
        self.button_product_table = Button(parent, text="Product Table (PG)")

        label_site_bond = Label(
            parent,
            text="Site:\n   [x,y,z]\n\nBond:\n   [x0,y0,z0] ; [x1,y1,z1]     (tail-head)\n   [X,Y,Z] @ [x,y,z]     (vector-center)\n   [x0,y0,z0] : [X,Y,Z]     (start-vector)\n\nVector:\n   [X,Y,Z] # site/bond\n\nOrbital:\n   (xyz[r]-polynomial) # site/bond",
        )

        # layout.
        layout.addWidget(label_group)
        layout.addWidget(self.combo_crystal_type)
        layout.addWidget(self.combo_group_type)
        layout.addWidget(self.combo_group)
        layout.addWidget(label_assoc_group)
        layout.addWidget(self.label_pg_name)
        layout.addWidget(self.label_sg_name)
        layout.addWidget(self.label_mpg_name)
        layout.addWidget(self.label_msg_name)
        layout.addWidget(HBar())
        layout.addWidget(label_info)
        layout.addWidget(self.button_symmetry_operation)
        layout.addWidget(self.button_character_table)
        layout.addWidget(self.button_wyckoff_site)
        layout.addWidget(self.button_wyckoff_bond)
        layout.addWidget(self.button_product_table)
        layout.addWidget(HBar())
        layout.addWidget(label_site_bond)
        layout.addItem(VSpacer())

        # connections.
        self.combo_group_type.currentTextChanged.connect(self.set_group_type)
        self.combo_crystal_type.currentTextChanged.connect(self.set_crystal_type)
        self.combo_group.currentTextChanged.connect(self.set_group)
        self.button_symmetry_operation.clicked.connect(self.show_symmetry_operation)
        self.button_character_table.clicked.connect(self.show_character_table)
        self.button_wyckoff_site.clicked.connect(self.show_wyckoff_site)
        self.button_wyckoff_bond.clicked.connect(self.show_wyckoff_bond)
        self.button_product_table.clicked.connect(self.show_product_table)

    # ==================================================
    def set_axis(self):
        if self.parent._type in ["PG", "MPG"]:
            self.parent._qtdraw.set_cell("off")
            self.parent._qtdraw.set_axis("full")
        else:
            self.parent._qtdraw.set_cell("single")
            self.parent._qtdraw.set_axis("on")

    # ==================================================
    def set_crystal_type(self, crystal):
        group_list = self.parent._get_group_list(crystal)
        group = group_list[0]  # top.
        self.parent._crystal = crystal
        self.combo_group.set_item(group_list)
        self.combo_group.setCurrentText(group)
        self.set_group(group)
        self.parent._qtdraw._set_crystal(crystal)

    # ==================================================
    def set_group_type(self, group_type):
        tp = self._type_list[group_type]
        group = self.parent._get_group_name()[tp]
        group_list = self.parent._get_group_list(tp=tp)
        self.parent._type = tp
        self.combo_group.set_item(group_list)
        self.combo_group.setCurrentText(group)
        self.set_group(group)
        self.set_axis()

    # ==================================================
    def set_group(self, group):
        self.parent._tag = self.parent._to_tag[group]
        self.parent._group = None
        self.parent._p_group = None
        self.parent._ps_group = None
        self.parent._mp_group = None

        self.set_group_name()
        self.parent.group_changed.emit()

    # ==================================================
    def set_group_name(self):
        name = self.parent._get_group_name()
        self.label_pg_name.setText("  " + name["PG"])
        self.label_sg_name.setText("  " + name["SG"])
        self.label_mpg_name.setText("  " + name["MPG"])
        self.label_msg_name.setText("  " + name["MSG"])

    # ==================================================
    def show_symmetry_operation(self):
        group = self.parent.group
        self._symmetry_operation_dialog = show_symmetry_operation(group, self)

    # ==================================================
    def show_character_table(self):
        group = self.parent.p_group
        self._character_table_dialog = show_character_table(group, self)

    # ==================================================
    def show_wyckoff_site(self):
        group = self.parent.ps_group
        self._wyckoff_site_dialog = show_wyckoff_site(group, self)

    # ==================================================
    def show_wyckoff_bond(self):
        group = self.parent.ps_group
        self._wyckoff_bond_dialog = show_wyckoff_bond(group, self)

    # ==================================================
    def show_product_table(self):
        group = self.parent.p_group
        self._product_table_dialog = show_product_table(group, self)

    # ==================================================
    def closeEvent(self, event):
        self.clear_data()
        super().closeEvent(event)

    # ==================================================
    def set_data(self, data):
        d = {"PG": 0, "SG": 1, "MPG": 2, "MSG": 3}
        crystal = data["general"]["crystal"]
        tp = data["general"]["type"]
        idx = data["general"]["index"]
        group = self.parent._crystal_list[crystal][tp][idx]
        self.combo_crystal_type.setCurrentText(crystal)
        self.combo_group_type.setCurrentIndex(d[tp])
        group_list = self.parent._get_group_list(crystal, tp)
        self.combo_group.set_item(group_list)
        self.combo_group.setCurrentText(group)
        self.set_group_name()
        self.set_axis()

        self._symmetry_operation_dialog = None
        self._character_table_dialog = None
        self._wyckoff_site_dialog = None
        self._wyckoff_bond_dialog = None
        self._product_table_dialog = None

    # ==================================================
    def clear_data(self):
        if self._symmetry_operation_dialog is not None:
            self._symmetry_operation_dialog.close()
        if self._character_table_dialog is not None:
            self._character_table_dialog.close()
        if self._wyckoff_site_dialog is not None:
            self._wyckoff_site_dialog.close()
        if self._wyckoff_bond_dialog is not None:
            self._wyckoff_bond_dialog.close()
        if self._product_table_dialog is not None:
            self._product_table_dialog.close()

        self._symmetry_operation_dialog = None
        self._character_table_dialog = None
        self._wyckoff_site_dialog = None
        self._wyckoff_bond_dialog = None
        self._product_table_dialog = None

    # ==================================================
    def get_status(self):
        status = {
            "general": {
                "crystal": self.parent._crystal,
                "type": self.parent._type,
                "index": self.combo_group.currentIndex(),
            }
        }
        return status
