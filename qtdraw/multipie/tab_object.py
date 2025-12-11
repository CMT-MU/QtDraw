from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from qtdraw.widget.custom_widget import Label, Layout, Combo, VSpacer, HSpacer, HBar, LineEdit, Check


# ==================================================
class TabObject(QWidget):
    # ==================================================
    def __init__(self, parent):
        super().__init__(parent)

        layout = Layout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setHorizontalSpacing(30)
        layout.setVerticalSpacing(10)

        # widget.
        label_site = Label(
            parent,
            text='<span style="font-weight:bold;">Site</span> : draw equivalent sites.<br>&nbsp;&nbsp;1. input representative SITE, + ENTER.',
        )
        self.object_edit_site = LineEdit(parent, text="", validator=("site", {"use_var": False}))

        panel1 = QWidget(parent)
        layout1 = Layout(panel1)
        layout1.addWidget(label_site, 0, 0, 1, 1, Qt.AlignLeft)
        layout1.addWidget(self.object_edit_site, 1, 0, 1, 1)

        label_bond = Label(
            parent,
            text='<span style="font-weight:bold;">Bond</span> : draw equivalent bonds.<br>&nbsp;&nbsp;1. input representative BOND, + ENTER.',
        )
        self.object_edit_bond = LineEdit(parent, text="", validator=("bond", {"use_var": False}))

        panel2 = QWidget(parent)
        layout2 = Layout(panel2)
        layout2.addWidget(label_bond, 0, 0, 1, 1, Qt.AlignLeft)
        layout2.addWidget(self.object_edit_bond, 1, 0, 1, 1)

        label_vector = Label(
            parent,
            text='<span style="font-weight:bold;">Vector</span> : draw vectors at equivalent sites or bonds.<br>&nbsp;&nbsp;1. choose type, 2. input vector [x,y,z] # representative SITE/BOND, + ENTER.',
        )
        self.object_combo_vector_type = Combo(parent, ["Q", "G", "T", "M"])
        self.object_edit_vector = LineEdit(parent, text="", validator=("vector_site_bond", {"use_var": False}))

        panel3 = QWidget(parent)
        layout3 = Layout(panel3)
        layout3.addWidget(label_vector, 0, 0, 1, 10, Qt.AlignLeft)
        layout3.addWidget(self.object_combo_vector_type, 1, 0, 1, 1)
        layout3.addWidget(self.object_edit_vector, 1, 1, 1, 9)

        label_orbital = Label(
            parent,
            text='<span style="font-weight:bold;">Orbital</span> : draw orbitals at equivalent sites or bonds.<br>&nbsp;&nbsp;1. choose type, 2. input orbital (xyz polynomial) # representative SITE/BOND, + ENTER.',
        )
        self.object_combo_orbital_type = Combo(parent, ["Q", "G", "T", "M"])
        self.object_edit_orbital = LineEdit(parent, text="", validator=("orbital_site_bond", {"use_var": False}))

        panel4 = QWidget(parent)
        layout4 = Layout(panel4)
        layout4.addWidget(label_orbital, 0, 0, 1, 10, Qt.AlignLeft)
        layout4.addWidget(self.object_combo_orbital_type, 1, 0, 1, 1)
        layout4.addWidget(self.object_edit_orbital, 1, 1, 1, 9)

        label_harmonics = Label(
            parent,
            text='<span style="font-weight:bold;">Harmonics</span> : draw point-group harmonics at equivalent sites or bonds.<br>&nbsp;&nbsp;1. choose (type,rank,irrep.), 2. input representative SITE/BOND, + ENTER.<br>&nbsp;&nbsp;\u21d2  expression of harmonics is also shown (in LaTeX form).',
        )
        self.object_combo_harmonics_type = Combo(parent, ["Q", "G", "T", "M"])
        self.object_combo_harmonics_rank = Combo(parent, map(str, range(12)))
        self.object_combo_harmonics_irrep = Combo(parent)
        self.object_edit_harmonics = LineEdit(parent, text="", validator=("site_bond", {"use_var": False}))
        label_harmonics_ex = Label(parent, text="expression")
        self.object_edit_harmonics_ex = LineEdit(parent)
        self.object_check_harmonics_latex = Check(parent, text="LaTeX")

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
            text='<span style="font-weight:bold;">Wyckoff</span> : find wyckoff position (WP) and site symmetry (SS).<br>&nbsp;&nbsp;1. input representative SITE/BOND, + ENTER. \u21d2 WP and SS are shown.',
        )
        self.object_edit_wyckoff = LineEdit(parent, text="", validator=("site_bond", {"use_var": False}))
        label_wyckoff_position = Label(parent, text="\u21d2 WP")
        self.object_edit_wyckoff_position = LineEdit(parent)
        label_symmetry = Label(parent, text="sym.")
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

    # ==================================================
