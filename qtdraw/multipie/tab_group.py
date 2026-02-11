"""
Multipie group tab.

This module provides group tab in MultiPie dialog.
"""

import numpy as np
import sympy as sp
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt

from qtdraw.util.util import distance, to_latex
from qtdraw.widget.custom_widget import Label, Layout, Button, Combo, VSpacer, HSpacer, HBar, LineEdit, Check
from qtdraw.multipie.multipie_info_dialog import show_harmonics_decomp, show_harmonics_info, show_atomic_multipole, show_response
from qtdraw.multipie.multipie_plot import plot_cell_site, plot_cell_bond


# ==================================================
class TabGroup(QWidget):
    # ==================================================
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.data = parent._data

        layout = Layout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setHorizontalSpacing(30)
        layout.setVerticalSpacing(10)

        # irrep. decomposition.
        label_decomp = Label(parent, text="Irrep. Decomposition (PG)", bold=True)
        label_symmetric = Label(parent, text="symmetric")
        label_antisymmetric = Label(parent, text="anti-symmetric")
        self.combo_irrep1 = Combo(parent)
        self.combo_irrep2 = Combo(parent)
        self.label_symmetric_decomp = Label(parent)
        self.combo_irrep = Combo(parent)
        self.label_antisymmetric_decomp = Label(parent)

        panel1 = QWidget(parent)
        layout1 = Layout(panel1)
        layout1.addWidget(label_decomp, 0, 0, 1, 1)

        panel2 = QWidget(parent)
        layout2 = Layout(panel2)
        layout2.addWidget(label_symmetric, 0, 0, 1, 1, Qt.AlignRight)
        layout2.addWidget(self.combo_irrep1, 0, 1, 1, 1)
        layout2.addWidget(self.combo_irrep2, 0, 2, 1, 1)
        layout2.addWidget(self.label_symmetric_decomp, 0, 3, 1, 3)
        layout2.addWidget(label_antisymmetric, 1, 0, 1, 1, Qt.AlignRight)
        layout2.addWidget(self.combo_irrep, 1, 1, 1, 1)
        layout2.addWidget(self.label_antisymmetric_decomp, 1, 3, 1, 3)

        # harmonics decomposition.
        label_harmonics = Label(parent, text="Harmonics Decomposition (PG)", bold=True)
        label_harmonics_type = Label(parent, text="type")
        self.combo_harmonics_type = Combo(parent, ["Q", "G"])
        label_harmonics_rank = Label(parent, text="rank")
        self.combo_harmonics_rank = Combo(parent, map(str, range(12)))
        label_harmonics_decomp = Label(parent, text="target PG")
        point_group_all_list = sum([i["PG"] for i in self.data._crystal_list.values()], [])
        self.combo_harmonics_decomp = Combo(parent, point_group_all_list)
        self.button_harmonics_decomp = Button(parent, text="decompose")

        panel3 = QWidget(parent)
        layout3 = Layout(panel3)
        layout3.addWidget(label_harmonics, 0, 0, 1, 1)
        layout3.addWidget(self.button_harmonics_decomp, 0, 2, 1, 1, Qt.AlignRight)

        panel4 = QWidget(parent)
        layout4 = Layout(panel4)
        layout4.addWidget(label_harmonics_type, 0, 0, 1, 1, Qt.AlignRight)
        layout4.addWidget(self.combo_harmonics_type, 0, 1, 1, 1)
        layout4.addWidget(label_harmonics_rank, 0, 2, 1, 1, Qt.AlignRight)
        layout4.addWidget(self.combo_harmonics_rank, 0, 3, 1, 1)
        layout4.addWidget(label_harmonics_decomp, 0, 4, 1, 1, Qt.AlignRight)
        layout4.addWidget(self.combo_harmonics_decomp, 0, 5, 1, 2)

        # harmonics.
        label_harmonics1 = Label(parent, text="Harmonics (PG)", bold=True)
        self.combo_harmonics1_type = Combo(parent, ["Q", "G"])
        self.combo_harmonics1_rank = Combo(parent, map(str, range(12)))
        self.combo_harmonics1 = Combo(parent)
        self.combo_harmonics1.setMinimumWidth(150)
        label_harmonics_ex = Label(parent, text="expression")
        self.edit_harmonics1_ex = LineEdit(parent)
        self.check_harmonics1_latex = Check(parent, text="LaTeX")
        self.button_harmonics_info = Button(parent, text="info")

        panel5 = QWidget(parent)
        layout5 = Layout(panel5)
        layout5.addWidget(label_harmonics1, 0, 0, 1, 1)
        panel6 = QWidget(parent)
        layout6 = Layout(panel6)
        layout6.addWidget(self.combo_harmonics1_type, 0, 0, 1, 1)
        layout6.addWidget(self.combo_harmonics1_rank, 0, 1, 1, 1)
        layout6.addWidget(self.combo_harmonics1, 0, 2, 1, 1)
        layout6.addWidget(self.button_harmonics_info, 0, 3, 1, 1)
        layout6.addWidget(self.check_harmonics1_latex, 0, 4, 1, 1, Qt.AlignRight)
        layout6.addWidget(label_harmonics_ex, 1, 0, 1, 1)
        layout6.addWidget(self.edit_harmonics1_ex, 1, 1, 1, 4)

        # find Wyckoff.
        label_fwyckoff = Label(parent, text="Find Wyckoff Site(PG/SG/MPG/MSG)/Bond(PG/SG)", bold=True)
        label_fwyckoff_sb = Label(parent, text="site/bond")
        self.edit_find_wyckoff = LineEdit(parent, text="", validator=("site_bond", {"use_var": False}))
        label_wyckoff = Label(parent, text="Wyckoff")
        self.edit_find_wyckoff_position = Label(parent, text="")
        self.edit_find_wyckoff_position.set_background(True)
        self.edit_find_wyckoff_position.setMinimumWidth(200)
        label_symmetry = Label(parent, text="site symmetry")
        self.edit_find_wyckoff_symmetry = Label(parent, text="")
        self.edit_find_wyckoff_symmetry.set_background(True)
        self.edit_find_wyckoff_symmetry.setMinimumWidth(100)

        panel7 = QWidget(parent)
        layout7 = Layout(panel7)
        layout7.addWidget(label_fwyckoff, 0, 0, 1, 5, Qt.AlignLeft)
        panel8 = QWidget(parent)
        layout8 = Layout(panel8)
        layout8.addWidget(label_fwyckoff_sb, 0, 0, 1, 1)
        layout8.addWidget(self.edit_find_wyckoff, 0, 1, 1, 4)
        layout8.addWidget(label_wyckoff, 1, 1, 1, 1, Qt.AlignRight)
        layout8.addWidget(self.edit_find_wyckoff_position, 1, 2, 1, 1)
        layout8.addWidget(label_symmetry, 1, 3, 1, 1, Qt.AlignRight)
        layout8.addWidget(self.edit_find_wyckoff_symmetry, 1, 4, 1, 1)

        # Wyckoff site/bond.
        label_wyckoff_site = Label(parent, text="Draw Wyckoff Site(PG/SG/MPG/MSG)/Bond(PG/SG) (representative)", bold=True)
        label_ws_neighbor = Label(parent, text="neighbor")
        label_wyckoff_site_str = Label(parent, text="site")
        self.combo_wyckoff_site = Combo(parent)
        self.edit_ws_neighbor = LineEdit(parent, text="[1]", validator=("list_int", {"shape": (0,)}))
        self.button_wyckoff_bond = Button(parent, text="show bond")
        label_wyckoff_bond_str = Label(parent, text="bond")
        self.combo_wyckoff_bond = Combo(parent)

        panel9 = QWidget(parent)
        layout9 = Layout(panel9)
        layout9.addWidget(label_wyckoff_site, 0, 0, 1, 1)
        panel10 = QWidget(parent)
        layout10 = Layout(panel10)
        layout10.addWidget(label_wyckoff_site_str, 0, 0, 1, 1, Qt.AlignRight)
        layout10.addWidget(self.combo_wyckoff_site, 0, 1, 1, 1)
        layout10.addWidget(label_ws_neighbor, 0, 2, 1, 1, Qt.AlignRight)
        layout10.addWidget(self.edit_ws_neighbor, 0, 3, 1, 2)
        layout10.addWidget(label_wyckoff_bond_str, 1, 0, 1, 1, Qt.AlignRight)
        layout10.addWidget(self.combo_wyckoff_bond, 1, 1, 1, 1)
        layout10.addWidget(self.button_wyckoff_bond, 1, 4, 1, 1, Qt.AlignRight)

        # atomic multipole.
        label_atomic = Label(parent, text="Atomic Multipole (PG)", bold=True)
        self.button_atomic = Button(parent, text="show")
        label_atomic_type = Label(parent, text="type")
        self.combo_atomic_type = Combo(parent, ["", "Q", "G", "T", "M"])
        self.combo_atomic_basis_type = Combo(parent, ["lg", "lgs", "jml"])
        label_atomic_braket = Label(parent, text="bra(L)-ket(L)")
        self.combo_atomic_bra_basis = Combo(parent, ["s", "p", "d", "f"])
        self.combo_atomic_ket_basis = Combo(parent, ["s", "p", "d", "f"])
        self.check_tesseral = Check(parent, text="tesseral")

        panel11 = QWidget(parent)
        layout11 = Layout(panel11)
        layout11.addWidget(label_atomic, 0, 0, 1, 1)
        layout11.addWidget(self.button_atomic, 0, 2, 1, 1, Qt.AlignRight)
        panel12 = QWidget(parent)
        layout12 = Layout(panel12)
        layout12.addWidget(label_atomic_type, 0, 1, 1, 1, Qt.AlignRight)
        layout12.addWidget(self.combo_atomic_type, 0, 2, 1, 1)
        layout12.addWidget(self.combo_atomic_basis_type, 0, 3, 1, 1)
        layout12.addWidget(self.check_tesseral, 1, 0, 1, 1, Qt.AlignRight)
        layout12.addWidget(label_atomic_braket, 1, 1, 1, 1, Qt.AlignRight)
        layout12.addWidget(self.combo_atomic_bra_basis, 1, 2, 1, 1)
        layout12.addWidget(self.combo_atomic_ket_basis, 1, 3, 1, 1)

        # response tensor.
        label_response = Label(parent, text="Response Tensor (MPG)", bold=True)
        self.button_response = Button(parent, text="show")
        self.combo_response_type = Combo(parent, ["Q", "G", "T", "M"])
        label_response_type = Label(parent, text="type")
        label_response_rank = Label(parent, text="rank")
        self.combo_response_rank = Combo(parent, map(str, range(5)))

        panel13 = QWidget(parent)
        layout13 = Layout(panel13)
        layout13.addWidget(label_response, 0, 0, 1, 1)
        layout13.addWidget(self.button_response, 0, 2, 1, 1, Qt.AlignRight)
        panel14 = QWidget(parent)
        layout14 = Layout(panel14)
        layout14.addWidget(label_response_type, 0, 0, 1, 1, Qt.AlignRight)
        layout14.addWidget(self.combo_response_type, 0, 1, 1, 1)
        layout14.addWidget(label_response_rank, 0, 2, 1, 1, Qt.AlignRight)
        layout14.addWidget(self.combo_response_rank, 0, 3, 1, 1)
        layout14.addItem(HSpacer(), 0, 4, 1, 1)

        # layout.
        layout.addWidget(panel1)
        layout.addWidget(panel2)
        layout.addWidget(HBar())

        layout.addWidget(panel3)
        layout.addWidget(panel4)
        layout.addWidget(HBar())

        layout.addWidget(panel5)
        layout.addWidget(panel6)
        layout.addWidget(HBar())

        layout.addWidget(panel7)
        layout.addWidget(panel8)
        layout.addWidget(HBar())

        layout.addWidget(panel9)
        layout.addWidget(panel10)
        layout.addWidget(HBar())

        layout.addWidget(panel11)
        layout.addWidget(panel12)
        layout.addWidget(HBar())

        layout.addWidget(panel13)
        layout.addWidget(panel14)

        layout.addItem(HSpacer(), 0, 10, 1, 1)
        layout.addItem(VSpacer())

        # connections.
        self.combo_irrep1.currentTextChanged.connect(self.set_irrep_decomp)
        self.combo_irrep2.currentTextChanged.connect(self.set_irrep_decomp)
        self.combo_irrep.currentTextChanged.connect(self.set_irrep_decomp)

        self.button_harmonics_decomp.released.connect(self.show_harmonics_decomp)

        self.combo_harmonics1_type.currentTextChanged.connect(self.set_harm_list)
        self.combo_harmonics1_rank.currentTextChanged.connect(self.set_harm_list)
        self.combo_harmonics1.currentIndexChanged.connect(self.show_harmonics)
        self.check_harmonics1_latex.checkStateChanged.connect(self.show_harmonics)
        self.button_harmonics_info.released.connect(self.show_harmonics_info)

        self.edit_find_wyckoff.returnPressed.connect(self.find_wyckoff_set)

        self.edit_ws_neighbor.returnPressed.connect(self.show_wyckoff_site)
        self.button_wyckoff_bond.released.connect(self.show_wyckoff_bond)

        self.button_atomic.released.connect(self.show_atomic)

        self.button_response.released.connect(self.show_response)

        self.combo_atomic_basis_type.currentTextChanged.connect(self.set_atomic_bra_ket)

    # ==================================================
    def set_irrep_list(self):
        group = self.data.p_group
        lst = list(group.character["table"].keys())
        self.combo_irrep1.set_item(lst)
        self.combo_irrep2.set_item(lst)
        self.combo_irrep.set_item(lst)
        self.set_irrep_decomp()

    # ==================================================
    def set_harm_list(self):
        group = self.data.p_group
        rank = int(self.combo_harmonics1_rank.currentText())
        head = self.combo_harmonics1_type.currentText()
        lst, self._harm_list = self.data._get_index_list(group.harmonics.select(l=rank, X=head).keys())
        self.combo_harmonics1.set_item(lst)
        self.combo_harmonics1.currentIndexChanged.emit(0)

    # ==================================================
    def set_wyckoff_list(self):
        group = self.data.ps_group

        self.combo_wyckoff_site.set_item(group.wyckoff["site"].keys())
        self.combo_wyckoff_bond.set_item(group.wyckoff["bond"].keys())

    # ==================================================
    def set_irrep_decomp(self, value=None):
        def _remove_latex(s):
            s = (
                s.replace("_{", "")
                .replace("}", "")
                .replace("^{", "")
                .replace(r"\prime", "'")
                .replace("(", "")
                .replace(")", "")
                .replace("0", "-")
            )
            return s

        pg = self.data.p_group

        irrep1 = self.combo_irrep1.currentText()
        irrep2 = self.combo_irrep2.currentText()
        irrep = self.combo_irrep.currentText()

        s = pg.character["symmetric_product"][(irrep1, irrep2)]
        a = pg.character["anti_symmetric_product"][irrep]
        s = _remove_latex(str(sum([n * sp.Symbol(v) for n, v in s])))
        a = _remove_latex(str(sum([n * sp.Symbol(v) for n, v in a])))

        self.label_symmetric_decomp.setText("   =   " + s)
        self.label_antisymmetric_decomp.setText("   =   " + a)

    # ==================================================
    def show_harmonics_decomp(self):
        group = self.data.p_group
        head = self.combo_harmonics_type.currentText()
        rank = int(self.combo_harmonics_rank.currentText())
        basis = self.combo_harmonics_decomp.currentText()
        basis = basis.split(" ")[1]
        self._harmonics_decomp_dialog = show_harmonics_decomp(group, basis, rank, head, self)

    # ==================================================
    def show_harmonics(self):
        group = self.data.p_group
        harm, comp = self._harm_list[self.combo_harmonics1.currentIndex()]
        check = self.check_harmonics1_latex.is_checked()

        harm = group.harmonics[harm][0][comp]
        if check:
            harm = to_latex(harm)
        else:
            harm = str(harm)

        self.edit_harmonics1_ex.setText(harm)

    # ==================================================
    def show_harmonics_info(self):
        group = self.data.p_group
        head = self.combo_harmonics1_type.currentText()
        rank = int(self.combo_harmonics1_rank.currentText())

        if self._harmonics_info_dialog is not None:
            self._harmonics_info_dialog.close()
        self._harmonics_info_dialog = show_harmonics_info(group, head, rank, self)

    # ==================================================
    def show_wyckoff_site(self):
        group = self.data.group
        wp = self.combo_wyckoff_site.currentText()

        # plot sites.
        sites = group.wyckoff["site"][wp]["reference"].astype(float)
        mp = group.wyckoff["site"][wp]["mapping"]
        if len(sites) != len(mp):
            mp = mp * (len(sites) // len(mp))
        plot_cell_site(self.data, sites, wp=wp, label=mp)

        # plot bonds.
        neighbor = self.edit_ws_neighbor.text()
        neighbor = list(map(int, neighbor.strip("[]").split(",")))
        G = self.parent._pvw.G_matrix[0:3, 0:3]
        d = distance(sites, sites, G)
        dkey = list(d.keys())

        for i in neighbor:
            if i < len(d):
                name = f"{wp}_N{i}"
                bonds = []
                for idxs in d[dkey[i]]:
                    t, h = sites[idxs[0]], sites[idxs[1]]
                    c = (t + h) / 2
                    v = h - t
                    bonds.append(np.concatenate([v, c]).tolist())
                plot_cell_bond(self.data, bonds, name=name)

    # ==================================================
    def show_wyckoff_bond(self):
        group = self.data.ps_group
        wp = self.combo_wyckoff_bond.currentText()

        # plot bonds.
        bonds = group.wyckoff["bond"][wp]["reference"].astype(float)
        mp = group.wyckoff["bond"][wp]["mapping"]
        if len(bonds) != len(mp):
            mp = mp * (len(bonds) // len(mp))
        plot_cell_bond(self.data, bonds, wp=wp, label=mp)

    # ==================================================
    def find_wyckoff_set(self):
        text = self.edit_find_wyckoff.raw_text()
        self.data.set_group_find_wyckoff(text)

        if text.count("[") == 2:
            group = self.data.ps_group
            wp, r = group.find_wyckoff_bond(text)
            # sym = group.wyckoff["bond"][wp]["symmetry"]
            sym = ""
        else:
            group = self.data.group
            wp, r = group.find_wyckoff_site(text)
            sym = group.wyckoff["site"][wp]["symmetry"]

        self.edit_find_wyckoff_position.setText(wp)
        self.edit_find_wyckoff_symmetry.setText(sym)

    # ==================================================
    def set_atomic_bra_ket(self):
        basis_type = self.combo_atomic_basis_type.currentText()
        if basis_type == "jml":
            self.combo_atomic_bra_basis.set_item(
                [
                    "s : 1/2",
                    "p : 1/2, 3/2",
                    "p : 1/2",
                    "p : 3/2",
                    "d : 3/2, 5/2",
                    "d : 3/2",
                    "d : 5/2",
                    "f : 5/2, 7/2",
                    "f : 5/2",
                    "f : 7/2",
                ]
            )
            self.combo_atomic_ket_basis.set_item(
                [
                    "s : 1/2",
                    "p : 1/2, 3/2",
                    "p : 1/2",
                    "p : 3/2",
                    "d : 3/2, 5/2",
                    "d : 3/2",
                    "d : 5/2",
                    "f : 5/2, 7/2",
                    "f : 5/2",
                    "f : 7/2",
                ]
            )
        else:
            self.combo_atomic_bra_basis.set_item(["s", "P", "d", "f"])
            self.combo_atomic_ket_basis.set_item(["s", "P", "d", "f"])

    # ==================================================
    def show_atomic(self):
        group = self.data.p_group
        head = self.combo_atomic_type.currentText()
        basis_type = self.combo_atomic_basis_type.currentText()
        bra = self.combo_atomic_bra_basis.currentText()
        ket = self.combo_atomic_ket_basis.currentText()
        tesseral = self.check_tesseral.is_checked()

        self._atomic_dialog = show_atomic_multipole(group, bra, ket, head, basis_type, tesseral, self)

    # ==================================================
    def show_response(self):
        group = self.data.mp_group
        rank = int(self.combo_response_rank.currentText())
        r_type = self.combo_response_type.currentText()

        self._response_dialog = show_response(group, rank, r_type, self)

    # ==================================================
    def closeEvent(self, event):
        self.clear_data()
        super().closeEvent(event)

    # ==================================================
    def set_data(self):
        find_wyckoff = self.data.status["group"]["find_wyckoff"]
        self.edit_find_wyckoff.setText(find_wyckoff)

        self._harmonics_decomp_dialog = None
        self._harmonics_info_dialog = None
        self._atomic_dialog = None
        self._response_dialog = None

    # ==================================================
    def clear_data(self):
        if self._harmonics_decomp_dialog is not None:
            self._harmonics_decomp_dialog.close()
        if self._harmonics_info_dialog is not None:
            self._harmonics_info_dialog.close()
        if self._atomic_dialog is not None:
            self._atomic_dialog.close()
        if self._response_dialog is not None:
            self._response_dialog.close()

        self._harmonics_decomp_dialog = None
        self._harmonics_info_dialog = None
        self._atomic_dialog = None
        self._response_dialog = None
