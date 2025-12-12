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

        # layout.
        layout.addWidget(panel1)
        layout.addWidget(HBar())
        layout.addWidget(panel2)
        layout.addWidget(HBar())
        layout.addWidget(panel3)
        layout.addWidget(HBar())
        layout.addWidget(panel4)
        layout.addItem(HSpacer(), 0, 1, 1, 1)
        layout.addItem(VSpacer())

    # ==================================================
