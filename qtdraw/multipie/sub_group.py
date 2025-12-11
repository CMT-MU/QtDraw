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

        self.setMinimumWidth(180)
        layout = Layout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setHorizontalSpacing(30)
        layout.setVerticalSpacing(10)

        # initial value.
        crystal = "triclinic"
        tp = "Point Group"
        group = next(iter(parent._mapping))

        # widget.
        label_group = Label(parent, text="Group", bold=True)
        self._type_list = {"Point Group": 0, "Space Group": 1, "Magnetic Point Group": 2, "Magnetic Space Group": 3}
        self.group_combo_group_type = Combo(parent, self._type_list.keys())
        crystal_list = parent._crystal_list.keys()
        self.group_combo_crystal_type = Combo(parent, crystal_list)

        group_list = parent._crystal_list[crystal][self._type_list[tp]]
        self.group_combo_group = Combo(parent, group_list)

        label_info = Label(parent, text="Info.", bold=True)
        self.group_button_symmetry_operation = Button(parent, text="Symmetry Operation")
        self.group_button_character_table = Button(parent, text="Character Table (PG)")
        self.group_button_wyckoff_site = Button(parent, text="Wyckoff Site (PG/SG)")
        self.group_button_wyckoff_bond = Button(parent, text="Wyckoff Bond (PG/SG)")
        self.group_button_product_table = Button(parent, text="Product Table (PG)")

        label_site_bond = Label(
            parent, text="SITE:\n   [x,y,z]\n\nBOND:\n   [tail] ; [head]\n   [vector] @ [center]\n   [start] : [vector]"
        )

        layout.addWidget(label_group)
        layout.addWidget(self.group_combo_crystal_type)
        layout.addWidget(self.group_combo_group_type)
        layout.addWidget(self.group_combo_group)
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

        self.set_crystal_type(crystal)
        self.set_group_type(tp)
        self.set_group(group)

    # ==================================================
    def set_crystal_type(self, crystal):
        group_list = self.parent()._crystal_list[crystal][self.parent()._type]
        group = group_list[0]  # top.
        self.group_combo_group.set_item(group_list)
        self.set_group(group)

    # ==================================================
    def set_group_type(self, group_type):
        group = self.group_combo_group.currentText()
        self.parent()._type = self._type_list[group_type]
        group_list = self.parent()._crystal_list[self.group_combo_crystal_type.currentText()][self.parent()._type]
        self.group_combo_group.set_item(group_list)
        self.set_group(group)

    # ==================================================
    def set_group(self, group):
        self.parent()._tag = self.parent()._mapping[group]
        self.group_combo_group.setCurrentText(group)
        self.parent()._group = [None, None, None, None]

    # ==================================================
    def show_symmetry_operation(self):
        group = self.parent().group()
        self._symmetry_operation_dialog = show_symmetry_operation(group, self)

    # ==================================================
    def show_character_table(self):
        group = self.parent().group(0)  # PG.
        self._character_table_dialog = show_character_table(group, self)

    # ==================================================
    def show_wyckoff_site(self):
        if self.parent()._type in [0, 2]:
            group = self.parent().group(0)  # PG.
        else:
            group = self.parent().group(1)  # SG.
        self._wyckoff_site_dialog = show_wyckoff_site(group, self)

    # ==================================================
    def show_wyckoff_bond(self):
        if self.parent()._type in [0, 2]:
            group = self.parent().group(0)  # PG.
        else:
            group = self.parent().group(1)  # SG.
        self._wyckoff_bond_dialog = show_wyckoff_bond(group, self)

    # ==================================================
    def show_product_table(self):
        group = self.parent().group(0)  # PG.
        self._product_table_dialog = show_product_table(group, self)
