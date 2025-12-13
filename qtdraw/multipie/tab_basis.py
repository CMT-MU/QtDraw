from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from qtdraw.widget.custom_widget import Label, Layout, Button, Combo, VSpacer, HSpacer, HBar, LineEdit


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

        # widget.
        label_site = Label(
            parent,
            text='<span style="font-weight:bold;">Site</span> : draw site-cluster basis.<br>&nbsp;&nbsp;1. input representative SITE, + ENTER, \u21d2 2. choose basis, 3. push "draw".',
        )
        self.basis_edit_site = LineEdit(parent, text="", validator=("site", {"use_var": False}))

        label_site_to = Label(parent, text="\u21d2 basis")
        self.basis_combo_site_samb = Combo(parent)
        self.basis_button_site_draw = Button(parent, text="draw")

        panel1 = QWidget(parent)
        layout1 = Layout(panel1)
        layout1.addWidget(label_site, 0, 0, 1, 10)
        layout1.addWidget(self.basis_edit_site, 1, 0, 1, 10)
        layout1.addWidget(label_site_to, 2, 0, 1, 1, Qt.AlignRight)
        layout1.addWidget(self.basis_combo_site_samb, 2, 1, 1, 8)
        layout1.addWidget(self.basis_button_site_draw, 2, 9, 1, 1)

        label_bond = Label(
            parent,
            text='<span style="font-weight:bold;">Bond</span> : draw bond-cluster basis.<br>&nbsp;&nbsp;1. input representative BOND, + ENTER, \u21d2 2. choose basis, 3. push "draw".',
        )
        self.basis_edit_bond = LineEdit(parent, text="", validator=("bond", {"use_var": False}))
        label_bond_to = Label(parent, text="\u21d2 basis")
        self.basis_combo_bond_samb = Combo(parent)
        self.basis_button_bond_draw = Button(parent, text="draw")

        panel2 = QWidget(parent)
        layout2 = Layout(panel2)
        layout2.addWidget(label_bond, 0, 0, 1, 10)
        layout2.addWidget(self.basis_edit_bond, 1, 0, 1, 10)
        layout2.addWidget(label_bond_to, 2, 0, 1, 1, Qt.AlignRight)
        layout2.addWidget(self.basis_combo_bond_samb, 2, 1, 1, 8)
        layout2.addWidget(self.basis_button_bond_draw, 2, 9, 1, 1)

        label_vector = Label(
            parent,
            text='<span style="font-weight:bold;">Vector</span> : draw symmetry-adapted vector.<br>&nbsp;&nbsp;1. choose type, 2. input representative SITE/BOND, + ENTER,<br>&nbsp;&nbsp;\u21d2  3. choose (type,basis), 4. push "draw" or 3. input linear combination, + ENTER or 3. push "modulation".',
        )
        self.basis_combo_vector_type = Combo(parent, ["Q", "G", "T", "M"])
        self.basis_edit_vector = LineEdit(parent, text="", validator=("site_bond", {"use_var": False}))
        label_vector_to = Label(parent, text="\u21d2 basis")
        self.basis_combo_vector_samb_type = Combo(parent, ["Q", "G", "T", "M"])
        self.basis_combo_vector_samb = Combo(parent)
        self.basis_button_vector_draw = Button(parent, text="draw")

        label_vector_lc = Label(parent, text="linear combination")
        self.basis_edit_vector_lc = LineEdit(parent)
        self.basis_button_vector_modulation = Button(parent, text="modulation")
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
            text='<span style="font-weight:bold;">Orbital</span> : draw symmetry-adapted orbital.<br>&nbsp;&nbsp;1. choose (type,rank), 2. input representative SITE/BOND, + ENTER,<br>&nbsp;&nbsp;\u21d2  3. choose (type,basis), 4. push "draw" or 3. input linear combination, + ENTER or 3. push "modulation".',
        )
        self.basis_combo_orbital_type = Combo(parent, ["Q", "G", "T", "M"])
        self.basis_combo_orbital_rank = Combo(parent, map(str, range(12)))
        self.basis_edit_orbital = LineEdit(parent, text="", validator=("site_bond", {"use_var": False}))
        label_orbital_to = Label(parent, text="\u21d2 basis")
        self.basis_combo_orbital_samb_type = Combo(parent, ["Q", "G", "T", "M"])
        self.basis_combo_orbital_samb = Combo(parent)
        self.basis_button_orbital_draw = Button(parent, text="draw")

        label_orbital_lc = Label(parent, text="linear combination")
        self.basis_edit_orbital_lc = LineEdit(parent)
        self.basis_button_orbital_modulation = Button(parent, text="modulation")
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
            text='<span style="font-weight:bold;">Hopping</span> : draw hopping direction.<br>&nbsp;&nbsp;1. input representative BOND, + ENTER.',
        )
        self.basis_edit_hopping = LineEdit(parent, text="", validator=("bond", {"use_var": False}))

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

    # ==================================================
