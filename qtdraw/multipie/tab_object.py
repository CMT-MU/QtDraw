"""
Multipie object tab.

This module provides object tab in MultiPie dialog.
"""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt

from qtdraw.widget.custom_widget import Label, Layout, Combo, VSpacer, HBar, LineEdit, Check
from qtdraw.multipie.multipie_plot import plot_cell_site, plot_cell_bond, plot_cell_vector, plot_cell_multipole


# ==================================================
class TabObject(QWidget):
    # ==================================================
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        layout = Layout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setHorizontalSpacing(30)
        layout.setVerticalSpacing(10)

        # site.
        label_site = Label(
            parent,
            text='<span style="font-weight:bold;">Site</span> : draw equivalent sites.<br>&nbsp;&nbsp;1. input representative site, + ENTER.',
        )
        self.edit_site = LineEdit(parent, text="", validator=("site", {"use_var": False}))

        panel1 = QWidget(parent)
        layout1 = Layout(panel1)
        layout1.addWidget(label_site, 0, 0, 1, 1, Qt.AlignLeft)
        layout1.addWidget(self.edit_site, 1, 0, 1, 1)

        # bond.
        label_bond = Label(
            parent,
            text='<span style="font-weight:bold;">Bond</span> : draw equivalent bonds.<br>&nbsp;&nbsp;1. input representative bond, + ENTER.',
        )
        self.edit_bond = LineEdit(parent, text="", validator=("bond", {"use_var": False}))

        panel2 = QWidget(parent)
        layout2 = Layout(panel2)
        layout2.addWidget(label_bond, 0, 0, 1, 1, Qt.AlignLeft)
        layout2.addWidget(self.edit_bond, 1, 0, 1, 1)

        # vector.
        label_vector = Label(
            parent,
            text='<span style="font-weight:bold;">Vector</span> : draw vectors at equivalent sites or bonds.<br>&nbsp;&nbsp;1. choose type (and check average), 2. input vector # site/bond, + ENTER.',
        )
        self.combo_vector_type = Combo(parent, ["Q", "G", "T", "M"])
        self.edit_vector = LineEdit(parent, text="", validator=("vector_site_bond", {"use_var": False}))
        self.check_vector_av = Check(parent, text="av.")
        self.check_vector_cart = Check(parent, text="cartesian")

        panel3 = QWidget(parent)
        layout3 = Layout(panel3)
        layout3.addWidget(label_vector, 0, 0, 1, 3, Qt.AlignLeft)
        layout3.addWidget(self.combo_vector_type, 1, 0, 1, 1)
        layout3.addWidget(self.check_vector_av, 1, 1, 1, 1, Qt.AlignRight)
        layout3.addWidget(self.edit_vector, 1, 2, 1, 1)
        layout3.addWidget(self.check_vector_cart, 2, 0, 1, 2)

        # orbital.
        label_orbital = Label(
            parent,
            text='<span style="font-weight:bold;">Orbital</span> : draw orbitals at equivalent sites or bonds.<br>&nbsp;&nbsp;1. choose type (and check average), 2. input orbital # site/bond, + ENTER.',
        )
        self.combo_orbital_type = Combo(parent, ["Q", "G", "T", "M"])
        self.edit_orbital = LineEdit(parent, text="", validator=("orbital_site_bond", {"use_var": False}))
        self.check_orbital_av = Check(parent, text="av.")

        panel4 = QWidget(parent)
        layout4 = Layout(panel4)
        layout4.addWidget(label_orbital, 0, 0, 1, 3, Qt.AlignLeft)
        layout4.addWidget(self.combo_orbital_type, 1, 0, 1, 1)
        layout4.addWidget(self.check_orbital_av, 1, 1, 1, 1, Qt.AlignRight)
        layout4.addWidget(self.edit_orbital, 1, 2, 1, 1)

        # layout.
        layout.addWidget(panel1)
        layout.addWidget(HBar())
        layout.addWidget(panel2)
        layout.addWidget(HBar())
        layout.addWidget(panel3)
        layout.addWidget(HBar())
        layout.addWidget(panel4)
        layout.addItem(VSpacer())

        # connections.
        self.edit_site.returnPressed.connect(self.show_site)
        self.edit_bond.returnPressed.connect(self.show_bond)
        self.edit_vector.returnPressed.connect(self.show_vector)
        self.edit_orbital.returnPressed.connect(self.show_orbital)

    # ==================================================
    def show_site(self, size=None, color=None, opacity=None):
        site = self.edit_site.raw_text()
        sites, mp, wp = self.parent.group.create_cell_site(site)
        plot_cell_site(self.parent, sites, wp=wp, label=mp, size=size, color=color, opacity=opacity)

    # ==================================================
    def show_bond(self, width=None, color=None, color2=None, opacity=None):
        bond = self.edit_bond.raw_text()
        bonds, mp, wp = self.parent.group.create_cell_bond(bond)
        plot_cell_bond(self.parent, bonds, wp=wp, label=mp, width=width, color=color, color2=color2, opacity=opacity)

    # ==================================================
    def show_vector(self, length=None, width=None, color=None, opacity=None):
        vector = self.edit_vector.raw_text()
        vector_type = self.combo_vector_type.currentText()
        cartesian = self.check_vector_cart.is_checked()
        av = self.check_vector_av.is_checked()
        vectors, sites, mp, wp = self.parent.group.create_cell_vector(vector, vector_type, av, cartesian)
        plot_cell_vector(
            self.parent,
            vectors,
            sites,
            vector_type,
            wp=wp,
            label=mp,
            average=av,
            cartesian=cartesian,
            length=length,
            width=width,
            color=color,
            opacity=opacity,
        )

    # ==================================================
    def show_orbital(self, size=None, color=None, opacity=None):
        orbital = self.edit_orbital.raw_text()
        orbital_type = self.combo_orbital_type.currentText()
        av = self.check_orbital_av.is_checked()
        orbitals, sites, mp, wp = self.parent.group.create_cell_multipole(orbital, orbital_type, av)
        plot_cell_multipole(
            self.parent, orbitals, sites, orbital_type, wp=wp, label=mp, average=av, size=size, color=color, opacity=opacity
        )

    # ==================================================
    def closeEvent(self, event):
        self.clear_data()
        super().closeEvent(event)

    # ==================================================
    def set_data(self, data):
        d = data["object"]
        self.edit_site.setText(d["site"])
        self.edit_bond.setText(d["bond"])
        self.combo_vector_type.setCurrentText(d["vector_type"])
        self.edit_vector.setText(d["vector"])
        self.check_vector_av.setChecked(d["vector_average"])
        self.check_vector_cart.setChecked(d["vector_cartesian"])
        self.combo_orbital_type.setCurrentText(d["orbital_type"])
        self.edit_orbital.setText(d["orbital"])
        self.check_orbital_av.setChecked(d["orbital_average"])

    # ==================================================
    def clear_data(self):
        pass

    # ==================================================
    def get_status(self):
        d = {
            "site": self.edit_site.raw_text(),
            "bond": self.edit_bond.raw_text(),
            "vector_type": self.combo_vector_type.currentText(),
            "vector": self.edit_vector.raw_text(),
            "vector_average": self.check_vector_av.is_checked(),
            "vector_cartesian": self.check_vector_cart.is_checked(),
            "orbital_type": self.combo_orbital_type.currentText(),
            "orbital": self.edit_orbital.raw_text(),
            "orbital_average": self.check_orbital_av.is_checked(),
        }
        return {"object": d}
