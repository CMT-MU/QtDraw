import sympy as sp
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt

from qtdraw.util.util import distance, to_latex
from qtdraw.widget.custom_widget import Label, Layout, Button, Combo, VSpacer, HSpacer, HBar, LineEdit, Check
from qtdraw.multipie.info_dialog import show_harmonics_decomp, show_atomic_multipole, show_response
from qtdraw.multipie.multipie_setting import setting_detail as detail


# ==================================================
class TabGroup(QWidget):
    # ==================================================
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

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
        point_group_all_list = sum([i[0] for i in self.parent._crystal_list.values()], [])
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
        label_harmonics_ex = Label(parent, text="expression")
        self.edit_harmonics1_ex = LineEdit(parent)
        self.check_harmonics1_latex = Check(parent, text="LaTeX")

        panel5 = QWidget(parent)
        layout5 = Layout(panel5)
        layout5.addWidget(label_harmonics1, 0, 0, 1, 1)
        panel6 = QWidget(parent)
        layout6 = Layout(panel6)
        layout6.addWidget(self.combo_harmonics1_type, 0, 0, 1, 1)
        layout6.addWidget(self.combo_harmonics1_rank, 0, 1, 1, 1)
        layout6.addWidget(self.combo_harmonics1, 0, 2, 1, 1)
        layout6.addWidget(self.check_harmonics1_latex, 0, 3, 1, 1, Qt.AlignRight)
        layout6.addWidget(label_harmonics_ex, 1, 0, 1, 1)
        layout6.addWidget(self.edit_harmonics1_ex, 1, 1, 1, 3)

        # find Wyckoff.
        label_fwyckoff = Label(parent, text="Find Wyckoff Site/Bond (PG/SG)", bold=True)
        label_fwyckoff_sb = Label(parent, text="site/bond")
        self.edit_find_wyckoff = LineEdit(parent, text="[0,0,0]", validator=("site_bond", {"use_var": False}))
        label_wyckoff = Label(parent, text="Wyckoff")
        self.edit_find_wyckoff_position = Label(parent, text="")
        self.edit_find_wyckoff_position.set_background(True)
        label_symmetry = Label(parent, text="LS")
        self.edit_find_wyckoff_symmetry = Label(parent, text="")
        self.edit_find_wyckoff_symmetry.set_background(True)

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
        label_wyckoff_site = Label(parent, text="Wyckoff Site/Bond (representative) (PG/SG)", bold=True)
        label_ws_neighbor = Label(parent, text="neighbor")
        label_wyckoff_site_str = Label(parent, text="site")
        self.combo_wyckoff_site = Combo(parent)
        self.edit_ws_neighbor = LineEdit(parent, text="[1]", validator=("list_int", {"shape": (0,)}))
        self.button_wyckoff_bond = Button(parent, text="show")
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

        panel11 = QWidget(parent)
        layout11 = Layout(panel11)
        layout11.addWidget(label_atomic, 0, 0, 1, 1)
        layout11.addWidget(self.button_atomic, 0, 2, 1, 1, Qt.AlignRight)
        panel12 = QWidget(parent)
        layout12 = Layout(panel12)
        layout12.addWidget(label_atomic_type, 0, 0, 1, 1, Qt.AlignRight)
        layout12.addWidget(self.combo_atomic_type, 0, 1, 1, 1)
        layout12.addWidget(self.combo_atomic_basis_type, 0, 2, 1, 1)
        layout12.addWidget(label_atomic_braket, 1, 0, 1, 1, Qt.AlignRight)
        layout12.addWidget(self.combo_atomic_bra_basis, 1, 1, 1, 1)
        layout12.addWidget(self.combo_atomic_ket_basis, 1, 2, 1, 1)

        # response tensor.
        label_response = Label(parent, text="Response Tensor (PG/MPG)", bold=True)
        self.button_response = Button(parent, text="show")
        self.combo_response_type = Combo(parent, ["Q", "G", "T", "M"])
        label_response_type = Label(parent, text="type")
        label_response_rank = Label(parent, text="rank")
        self.combo_response_rank = Combo(parent, map(str, range(1, 5)))

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

        self.button_harmonics_decomp.clicked.connect(self.show_harmonics_decomp)

        self.combo_harmonics1_type.currentTextChanged.connect(self.set_harm_list)
        self.combo_harmonics1_rank.currentTextChanged.connect(self.set_harm_list)
        self.combo_harmonics1.currentTextChanged.connect(self.show_harmonics)
        self.check_harmonics1_latex.checkStateChanged.connect(self.show_harmonics)

        self.edit_find_wyckoff.returnPressed.connect(self.find_wyckoff_set)

        self.edit_ws_neighbor.returnPressed.connect(self.show_wyckoff_site)
        self.button_wyckoff_bond.clicked.connect(self.show_wyckoff_bond)

        self.button_atomic.clicked.connect(self.show_atomic)

        self.button_response.clicked.connect(self.show_response)

        self._harmonics_decomp_dialog = None
        self._atomic_dialog = None
        self._response_dialog = None

    # ==================================================
    def set_irrep_list(self):
        group = self.parent.group(0)  # PG.
        lst = list(group["character"]["table"].keys())
        self.combo_irrep1.set_item(lst)
        self.combo_irrep2.set_item(lst)
        self.combo_irrep.set_item(lst)
        self.set_irrep_decomp()

    # ==================================================
    def set_harm_list(self):
        group = self.parent.group(0)  # PG.
        rank = int(self.combo_harmonics1_rank.currentText())
        head = self.combo_harmonics1_type.currentText()
        lst0 = [f"{i[2]}({i[3]})" if i[3] != -1 else f"{i[2]}" for i in group["harmonics"].select(l=rank, X=head).keys()]
        lst = []
        for i in lst0:
            if i[0] == "E":
                lst.append(i + ",1")
                lst.append(i + ",2")
            elif i[0] == "T":
                lst.append(i + ",1")
                lst.append(i + ",2")
                lst.append(i + ",3")
            else:
                lst.append(i)
        self.combo_harmonics1.set_item(lst)
        self.combo_harmonics1.currentTextChanged.emit(lst[0])

    # ==================================================
    def set_wyckoff_list(self):
        if self.parent._type in [0, 2]:
            group = self.parent.group(0)  # PG.
        else:
            group = self.parent.group(1)  # SG.

        self.combo_wyckoff_site.set_item(group["wyckoff"]["site"].keys())
        self.combo_wyckoff_bond.set_item(group["wyckoff"]["bond"].keys())

    # ==================================================
    def set_irrep_decomp(self, value=None):
        def remove_latex(s):
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

        pg = self.parent.group(0)  # PG.

        irrep1 = self.combo_irrep1.currentText()
        irrep2 = self.combo_irrep2.currentText()
        irrep = self.combo_irrep.currentText()

        s = pg["character"]["symmetric_product"][(irrep1, irrep2)]
        a = pg["character"]["anti_symmetric_product"][irrep]
        s = remove_latex(str(sum([n * sp.Symbol(v) for n, v in s])))
        a = remove_latex(str(sum([n * sp.Symbol(v) for n, v in a])))

        self.label_symmetric_decomp.setText("   =   " + s)
        self.label_antisymmetric_decomp.setText("   =   " + a)

    # ==================================================
    def show_harmonics_decomp(self):
        group = self.parent.group(0)  # PG.
        head = self.combo_harmonics_type.currentText()
        rank = int(self.combo_harmonics_rank.currentText())
        basis = self.combo_harmonics_decomp.currentText()
        basis = basis.split(" ")[1]
        self._harmonics_decomp_dialog = show_harmonics_decomp(group, basis, rank, head, self)

    # ==================================================
    def show_harmonics(self):
        group = self.parent.group(0)  # PG.
        rank = int(self.combo_harmonics1_rank.currentText())
        head = self.combo_harmonics1_type.currentText()
        harm = self.combo_harmonics1.currentText()
        check = self.check_harmonics1_latex.is_checked()

        harm = harm.replace("(", " ").replace(")", "")
        comp = int(harm.split(",")[1]) - 1 if harm.count(",") > 0 else 0
        harm = harm.split(",")[0] if harm.count(",") > 0 else harm
        harm = harm.split(" ")
        irrep = harm[0]
        n = -1 if len(harm) == 1 else int(harm[1])

        harm = group["harmonics"].select(X=head, l=rank, Gamma=irrep, n=n)
        harm = harm[next(iter(harm))][0][comp]
        if check:
            harm = to_latex(harm)
        else:
            harm = str(harm)

        self.edit_harmonics1_ex.setText(harm)

    # ==================================================
    def show_wyckoff_site(self):
        if self.parent._type in [0, 2]:
            group = self.parent.group(0)  # PG.
        else:
            group = self.parent.group(1)  # SG.
        wp = self.combo_wyckoff_site.currentText()

        # plot sites.
        sites = group["wyckoff"]["site"][wp]["fractional"].astype(float)
        mp = group["wyckoff"]["site"][wp]["mapping"]

        default = detail["site"]
        size = default["size"]
        color = default["color"]
        opacity = default["opacity"]
        width = default["width"]

        for no, (pt, m) in enumerate(zip(sites, mp)):
            label = f"S{no+1}: " + f"{m}".replace(" ", "")
            self.parent._pvw.add_site(position=pt, name=wp, label=label, size=size, color=color, opacity=opacity)

        # plot bonds.
        bond = self.edit_ws_neighbor.text()
        bond = list(map(int, bond.strip("[]").split(",")))
        G = self.parent._pvw.G_matrix[0:3, 0:3]
        d = distance(sites, sites, G)
        dkey = list(d.keys())

        for i in bond:
            name = f"b{i:02}"
            if i < len(d):
                for idxs in d[dkey[i]]:
                    t, h = sites[idxs[0]], sites[idxs[1]]
                    c = (t + h) / 2
                    v = h - t
                    self.parent._pvw.add_bond(position=c, direction=v, width=width, name=name)

    # ==================================================
    def show_wyckoff_bond(self):
        if self.parent._type in [0, 2]:
            group = self.parent.group(0)  # PG.
        else:
            group = self.parent.group(1)  # SG.
        wp = self.combo_wyckoff_bond.currentText()

        # plot bonds.
        bonds = group["wyckoff"]["bond"][wp]["fractional"].astype(float)
        mp = group["wyckoff"]["bond"][wp]["mapping"]

        default = detail["bond"]
        width = default["width"]
        color = default["color1"]
        color2 = default["color2"]
        opacity = default["opacity"]

        directional = not any(x < 0 for x in sum(mp, []))
        if not directional:
            color2 = color
        for no, (b, m) in enumerate(zip(bonds, mp)):
            v, c = b[0:3], b[3:6]
            label = f"B{no+1}: " + f"{m}".replace(" ", "")
            self.parent._pvw.add_bond(
                direction=v, position=c, width=width, color=color, color2=color2, opacity=opacity, name=wp, label=label
            )

    # ==================================================
    def find_wyckoff_set(self):
        if self.parent._type in [0, 2]:
            group = self.parent.group(0)  # PG.
        else:
            group = self.parent.group(1)  # SG.
        text = self.edit_find_wyckoff.raw_text()

        if "@" in text:
            wp, r = group.find_wyckoff_bond(text)
            # sym = group["wyckoff"]["bond"][wp]["symmetry"]
            sym = ""
        else:
            wp, r = group.find_wyckoff_site(text)
            sym = group["wyckoff"]["site"][wp]["symmetry"]

        self.edit_find_wyckoff_position.setText(wp)
        self.edit_find_wyckoff_symmetry.setText(sym)

    # ==================================================
    def show_atomic(self):
        head = self.combo_atomic_type.currentText()
        basis_type = self.combo_atomic_basis_type.currentText()
        bra = self.combo_atomic_bra_basis.currentText()
        ket = self.combo_atomic_ket_basis.currentText()
        group = self.parent.group(0)

        self._atomic_dialog = show_atomic_multipole(group, bra, ket, head, basis_type, self)

    # ==================================================
    def show_response(self):
        group = self.parent.group(2)  # MPG.
        rank = int(self.combo_response_rank.currentText())
        r_type = self.combo_response_type.currentText()

        self._response_dialog = show_response(group, rank, r_type, self)

    # ==================================================
    def closeEvent(self, event):
        if self._harmonics_decomp_dialog is not None:
            self._harmonics_decomp_dialog.close()
        if self._atomic_dialog is not None:
            self._atomic_dialog.close()
        if self._response_dialog is not None:
            self._response_dialog.close()
        super().closeEvent(event)
