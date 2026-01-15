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
        self.data = parent._data

        self.setMinimumWidth(270)
        layout = Layout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setHorizontalSpacing(30)
        layout.setVerticalSpacing(10)

        # widget.
        label_group = Label(parent, text="Group", bold=True)
        self.combo_group_type = Combo(parent, self.data._type_list.keys())
        self.combo_crystal_type = Combo(parent, self.data._crystal_list.keys())
        self.combo_group = Combo(parent, [])
        self.label_pg_name = Label(parent, text="")
        self.label_sg_name = Label(parent, text="")
        self.label_mpg_name = Label(parent, text="")
        self.label_msg_name = Label(parent, text="")

        label_info = Label(parent, text="Info.", bold=True)
        self.button_symmetry_operation = Button(parent, text="Symmetry Operation")
        self.button_character_table = Button(parent, text="Character Table (PG)")
        self.button_wyckoff_site = Button(parent, text="Wyckoff Site")
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
        self.button_symmetry_operation.released.connect(self.show_symmetry_operation)
        self.button_character_table.released.connect(self.show_character_table)
        self.button_wyckoff_site.released.connect(self.show_wyckoff_site)
        self.button_wyckoff_bond.released.connect(self.show_wyckoff_bond)
        self.button_product_table.released.connect(self.show_product_table)

    # ==================================================
    def set_crystal_type(self, crystal):
        group_list, group = self.data.set_crystal_type(crystal)
        self.combo_group.set_item(group_list)
        self.combo_group.setCurrentText(group)
        self.parent._qtdraw._set_crystal(crystal)
        self.parent.group_changed.emit()

    # ==================================================
    def set_group_type(self, group_type):
        group_list, group = self.data.set_group_type(group_type)
        self.combo_group.set_item(group_list)
        self.combo_group.setCurrentText(group)
        self.parent.group_changed.emit()

    # ==================================================
    def set_group(self, group):
        self.data.set_group(group)
        self.parent.group_changed.emit()

    # ==================================================
    def set_group_name(self):
        d = {"PG": 0, "SG": 1, "MPG": 2, "MSG": 3}
        name = self.data._get_group_name()
        name = [
            "&nbsp;<b>PG:</b>&nbsp;" + name["PG"],
            "&nbsp;<b>SG:</b>&nbsp;" + name["SG"],
            "&nbsp;<b>MPG:</b>&nbsp;" + name["MPG"],
            "&nbsp;<b>MSG:</b>&nbsp;" + name["MSG"],
        ]
        name[d[self.data._type]] = name[d[self.data._type]].replace(r"</b>", "") + "</b>"
        self.label_pg_name.setText(name[0])
        self.label_sg_name.setText(name[1])
        self.label_mpg_name.setText(name[2])
        self.label_msg_name.setText(name[3])

    # ==================================================
    def show_symmetry_operation(self):
        group = self.data.group
        self._symmetry_operation_dialog = show_symmetry_operation(group, self)

    # ==================================================
    def show_character_table(self):
        group = self.data.p_group
        self._character_table_dialog = show_character_table(group, self)

    # ==================================================
    def show_wyckoff_site(self):
        group = self.data.group
        self._wyckoff_site_dialog = show_wyckoff_site(group, self)

    # ==================================================
    def show_wyckoff_bond(self):
        group = self.data.ps_group
        self._wyckoff_bond_dialog = show_wyckoff_bond(group, self)

    # ==================================================
    def show_product_table(self):
        group = self.data.p_group
        self._product_table_dialog = show_product_table(group, self)

    # ==================================================
    def closeEvent(self, event):
        self.clear_data()
        super().closeEvent(event)

    # ==================================================
    def set_data(self):
        d = {"PG": 0, "SG": 1, "MPG": 2, "MSG": 3}
        crystal = self.data._crystal
        tp = self.data._type
        idx = self.data._idx

        group_list = self.data._get_group_list()
        self.combo_crystal_type.setCurrentText(crystal)
        self.combo_group_type.setCurrentIndex(d[tp])
        self.combo_group.set_item(group_list)
        self.combo_group.setCurrentIndex(idx)
        self.parent._qtdraw._set_crystal(crystal)
        self.parent.group_changed.emit()

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
