"""
Multipie side panel.

This module provides side panel in MultiPie dialog.
"""

from PySide6.QtWidgets import QWidget

from qtdraw.widget.custom_widget import Label, Layout, Button, Combo, VSpacer, HBar
from qtdraw.multipie.info_dialog import (
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

        # initial value.
        self._symmetry_operation_dialog = None
        self._character_table_dialog = None
        self._wyckoff_site_dialog = None
        self._wyckoff_bond_dialog = None
        self._product_table_dialog = None

        # widget.
        label_group = Label(parent, text="Group", bold=True)
        self._type_list = {"Point Group": 0, "Space Group": 1, "Magnetic Point Group": 2, "Magnetic Space Group": 3}
        self.group_combo_group_type = Combo(parent, self._type_list.keys())
        self.group_combo_crystal_type = Combo(parent, parent._crystal_list.keys())
        self.group_combo_group = Combo(parent, [])
        label_assoc_group = Label(parent, text="Associated Group (PG/SG/MPG/MSG)", bold=True)
        self.label_pg_name = Label(parent, text="")
        self.label_sg_name = Label(parent, text="")
        self.label_mpg_name = Label(parent, text="")
        self.label_msg_name = Label(parent, text="")

        label_info = Label(parent, text="Info.", bold=True)
        self.group_button_symmetry_operation = Button(parent, text="Symmetry Operation")
        self.group_button_character_table = Button(parent, text="Character Table (PG)")
        self.group_button_wyckoff_site = Button(parent, text="Wyckoff Site (PG/SG)")
        self.group_button_wyckoff_bond = Button(parent, text="Wyckoff Bond (PG/SG)")
        self.group_button_product_table = Button(parent, text="Product Table (PG)")

        label_site_bond = Label(
            parent,
            text="SITE:\n   [x,y,z]\n\nBOND:\n   [x0,y0,z0] ; [x1,y1,z1] (tail-head)\n   [X,Y,Z] @ [x,y,z] (vector-center)\n   [x0,y0,z0] : [X,Y,Z] (start-vector)\n\nVECTOR:\n   [X,Y,Z] # SITE/BOND\n\nORBITAL:\n   (xyz[r]-polynomial) # SITE/BOND",
        )

        # layout.
        layout.addWidget(label_group)
        layout.addWidget(self.group_combo_crystal_type)
        layout.addWidget(self.group_combo_group_type)
        layout.addWidget(self.group_combo_group)
        layout.addWidget(label_assoc_group)
        layout.addWidget(self.label_pg_name)
        layout.addWidget(self.label_sg_name)
        layout.addWidget(self.label_mpg_name)
        layout.addWidget(self.label_msg_name)
        layout.addWidget(HBar())
        layout.addWidget(label_info)
        layout.addWidget(self.group_button_symmetry_operation)
        layout.addWidget(self.group_button_character_table)
        layout.addWidget(self.group_button_wyckoff_site)
        layout.addWidget(self.group_button_wyckoff_bond)
        layout.addWidget(self.group_button_product_table)
        layout.addWidget(HBar())
        layout.addWidget(label_site_bond)
        layout.addItem(VSpacer())

        # connections.
        self.group_combo_group_type.currentTextChanged.connect(self.set_group_type)
        self.group_combo_crystal_type.currentTextChanged.connect(self.set_crystal_type)
        self.group_combo_group.currentTextChanged.connect(self.set_group)
        self.group_button_symmetry_operation.clicked.connect(self.show_symmetry_operation)
        self.group_button_character_table.clicked.connect(self.show_character_table)
        self.group_button_wyckoff_site.clicked.connect(self.show_wyckoff_site)
        self.group_button_wyckoff_bond.clicked.connect(self.show_wyckoff_bond)
        self.group_button_product_table.clicked.connect(self.show_product_table)

        # set initial values.
        self.group_combo_crystal_type.setCurrentText(self.parent._crystal)
        self.group_combo_group_type.setCurrentIndex(self.parent._type)
        self.group_combo_group.set_item(self.parent._get_group_list())
        if self.parent._type in [0, 2]:
            self.parent._qtdraw.set_cell("off")
        else:
            self.parent._qtdraw.set_cell("single")

    # ==================================================
    def set_crystal_type(self, crystal):
        group_list = self.parent._get_group_list(crystal)
        group = group_list[0]  # top.

        self.set_group(group, crystal=crystal)
        self.group_combo_group.set_item(group_list)
        self.parent._qtdraw._set_crystal(crystal)

    # ==================================================
    def set_group_type(self, group_type):
        tp = self._type_list[group_type]
        group = self.parent._get_group_name()[tp]
        group_list = self.parent._get_group_list(tp=tp)
        self.group_combo_group.set_item(group_list)
        self.set_group(group, tp=tp)

        if tp in [0, 2]:
            self.parent._qtdraw.set_cell("off")
        else:
            self.parent._qtdraw.set_cell("single")

    # ==================================================
    def set_group(self, group, crystal=None, tp=None):
        if crystal is None:
            crystal = self.group_combo_crystal_type.currentText()
        if tp is None:
            tp = self._type_list[self.group_combo_group_type.currentText()]
        self.parent._set_group_data(group, crystal=crystal, tp=tp)
        self.group_combo_group.setCurrentText(group)
        self.set_group_name()

    # ==================================================
    def set_group_name(self):
        name = self.parent._get_group_name()
        self.label_pg_name.setText("  " + name[0])
        self.label_sg_name.setText("  " + name[1])
        self.label_mpg_name.setText("  " + name[2])
        self.label_msg_name.setText("  " + name[3])

    # ==================================================
    def show_symmetry_operation(self):
        group = self.parent.group()
        self._symmetry_operation_dialog = show_symmetry_operation(group, self)

    # ==================================================
    def show_character_table(self):
        group = self.parent.group(0)  # PG.
        self._character_table_dialog = show_character_table(group, self)

    # ==================================================
    def show_wyckoff_site(self):
        if self.parent._type in [0, 2]:
            group = self.parent.group(0)  # PG.
        else:
            group = self.parent.group(1)  # SG.
        self._wyckoff_site_dialog = show_wyckoff_site(group, self)

    # ==================================================
    def show_wyckoff_bond(self):
        if self.parent._type in [0, 2]:
            group = self.parent.group(0)  # PG.
        else:
            group = self.parent.group(1)  # SG.
        self._wyckoff_bond_dialog = show_wyckoff_bond(group, self)

    # ==================================================
    def show_product_table(self):
        group = self.parent.group(0)  # PG.
        self._product_table_dialog = show_product_table(group, self)

    # ==================================================
    def closeEvent(self, event):
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
        super().closeEvent(event)
