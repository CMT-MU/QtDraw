import numpy as np
import sympy as sp
from qtpy.QtWidgets import (
    QDialog,
    QLabel,
    QTabWidget,
    QGridLayout,
    QWidget,
    QSpacerItem,
    QSizePolicy,
    QComboBox,
    QPushButton,
    QLineEdit,
)
from qtpy.QtCore import Qt
from gcoreutils.nsarray import NSArray
from multipie.group.point_group import PointGroup
from multipie.group.space_group import SpaceGroup
from multipie.tag.tag_group import TagGroup
from multipie.model.material_model import MaterialModel
from multipie.const import __def_dict__
from qtdraw.multipie.dialog_group_info import (
    create_character_table,
    create_harmonics,
    create_harmonics_decomp,
    create_symmetry_operation,
    create_product_table,
    create_wyckoff,
    create_v_cluster,
    create_response,
    create_atomic_mp,
)
from qtdraw.multipie.setting import rcParams


# ==================================================
class DialogGroup(QDialog):
    # ==================================================
    def __init__(self, core, qtdraw, width=512, height=600, parent=None):
        super().__init__(parent)
        self._core = core
        self._qtdraw = qtdraw
        self.crystal = [{}, {}]  # space/point group.
        for crystal in __def_dict__["crystal"]:
            self.crystal[0][crystal] = [f"{i.no}. {i}" for i in TagGroup.create(crystal=crystal, space_group=True)]
            self.crystal[1][crystal] = [f"{i.no}. {i}" for i in TagGroup.create(crystal=crystal)]

        self.setWindowTitle(f"QtDraw - Group Operations with MultiPie Ver. {self._qtdraw._multipie_loaded}")
        self.resize(width, height)

        # default.
        tag = rcParams["group_tag"]

        self.set_group_object(tag)
        crystal = self._group.tag.crystal

        # group selector.
        self.main_g_type = QComboBox(self)
        self.main_g_type.setFocusPolicy(Qt.NoFocus)
        self.main_g_type.addItems(["space group", "point group"])
        self.main_g_type.setCurrentIndex(self.pg)

        self.main_c_type = QComboBox(self)
        self.main_c_type.setFocusPolicy(Qt.NoFocus)
        self.main_c_type.addItems(list(self.crystal[self.pg].keys()))
        self.main_c_type.setCurrentIndex(0)

        self.main_group = QComboBox(self)
        self.main_group.setFocusPolicy(Qt.NoFocus)
        self.main_group.addItems(self.crystal[self.pg][crystal])
        self.main_group.setCurrentIndex(0)

        self.main_symmetry_operation = QPushButton("symmetry operation", self)
        self.main_symmetry_operation.setFocusPolicy(Qt.NoFocus)
        self.main_character_table = QPushButton("character table", self)
        self.main_character_table.setFocusPolicy(Qt.NoFocus)
        self.main_wyckoff = QPushButton("Wyckoff position", self)
        self.main_wyckoff.setFocusPolicy(Qt.NoFocus)
        self.main_product_table = QPushButton("product table", self)
        self.main_product_table.setFocusPolicy(Qt.NoFocus)

        self.main_harmonics = QPushButton("harmonics", self)
        self.main_harmonics.setFocusPolicy(Qt.NoFocus)
        self.main_harmonics_type = QComboBox(self)
        self.main_harmonics_type.setFocusPolicy(Qt.NoFocus)
        self.main_harmonics_type.addItems(["Q", "G", "T", "M"])
        self.main_harmonics_type.setCurrentIndex(0)
        self.main_harmonics_rank_label = QLabel("rank", self)
        self.main_harmonics_rank = QComboBox(self)
        self.main_harmonics_rank.setFocusPolicy(Qt.NoFocus)
        self.main_harmonics_rank.addItems(map(str, range(12)))
        self.main_harmonics_rank.setCurrentIndex(0)
        self.main_harmonics_to_label = QLabel("irrep. decomp.", self)
        self.main_harmonics_to_pg = QComboBox(self)
        self.main_harmonics_to_pg.setFocusPolicy(Qt.NoFocus)
        self.main_harmonics_to_pg.addItems([f"{i.no}. {i}" for i in TagGroup.create()])
        self.main_harmonics_to_pg.setCurrentIndex(0)
        self.main_harmonics_to_gen = QPushButton("gen", self)
        self.main_harmonics_to_gen.setFocusPolicy(Qt.NoFocus)

        self.main_response = QPushButton("response tensor", self)
        self.main_response.setFocusPolicy(Qt.NoFocus)
        self.main_response_rank_label = QLabel("rank", self)
        self.main_response_rank = QComboBox(self)
        self.main_response_rank.setFocusPolicy(Qt.NoFocus)
        self.main_response_rank.addItems(map(str, range(1, 5)))
        self.main_response_rank.setCurrentIndex(1)
        self.main_response_i_type = QComboBox(self)
        self.main_response_i_type.setFocusPolicy(Qt.NoFocus)
        self.main_response_i_type.addItems(["polar", "axial"])
        self.main_response_i_type.setCurrentIndex(0)
        self.main_response_t_type = QComboBox(self)
        self.main_response_t_type.setFocusPolicy(Qt.NoFocus)
        self.main_response_t_type.addItems(["E", "M"])
        self.main_response_t_type.setCurrentIndex(0)

        self.main_atomic_mp = QPushButton("atomic multipole", self)
        self.main_atomic_mp.setFocusPolicy(Qt.NoFocus)
        self.main_atomic_mp_head = QComboBox(self)
        self.main_atomic_mp_head.setFocusPolicy(Qt.NoFocus)
        self.main_atomic_mp_head.addItems(["", "Q", "G", "T", "M"])
        self.main_atomic_mp_head.setCurrentIndex(0)
        self.main_atomic_mp_btype = QComboBox(self)
        self.main_atomic_mp_btype.setFocusPolicy(Qt.NoFocus)
        self.main_atomic_mp_btype.addItems(["lm", "jm"])
        self.main_atomic_mp_btype.setCurrentIndex(0)
        self.main_atomic_mp_braket_label = QLabel("bra-ket", self)
        self.main_atomic_mp_bra_basis = QComboBox(self)
        self.main_atomic_mp_bra_basis.setFocusPolicy(Qt.NoFocus)
        self.main_atomic_mp_bra_basis.addItems(["s", "p", "d", "f"])
        self.main_atomic_mp_bra_basis.setCurrentIndex(0)
        self.main_atomic_mp_ket_basis = QComboBox(self)
        self.main_atomic_mp_ket_basis.setFocusPolicy(Qt.NoFocus)
        self.main_atomic_mp_ket_basis.addItems(["s", "p", "d", "f"])
        self.main_atomic_mp_ket_basis.setCurrentIndex(0)

        self.main_v_cluster = QPushButton("virtual cluster", self)
        self.main_v_cluster.setFocusPolicy(Qt.NoFocus)
        self.main_v_cluster_wp = QComboBox(self)
        self.main_v_cluster_wp.setFocusPolicy(Qt.NoFocus)
        self.main_v_cluster_wp.addItems(self.wp)
        self.main_v_cluster_wp.setCurrentIndex(0)
        self.main_v_cluster_bond = QLineEdit("1", self)

        self.main_irrep_sym_label = QLabel("symmetric", self)
        self.main_irrep_sym_label.setFocusPolicy(Qt.NoFocus)
        self.main_irrep_asym_label = QLabel("anti-sym.", self)
        self.main_irrep_asym_label.setFocusPolicy(Qt.NoFocus)
        self.main_irrep1 = QComboBox(self)
        self.main_irrep1.setFocusPolicy(Qt.NoFocus)
        self.main_irrep1.addItems(self.irrep)
        self.main_irrep1.setCurrentIndex(0)
        self.main_irrep2 = QComboBox(self)
        self.main_irrep2.setFocusPolicy(Qt.NoFocus)
        self.main_irrep2.addItems(self.irrep)
        self.main_irrep2.setCurrentIndex(0)
        self.main_irrep_sym = QLabel("", self)
        self.main_irrep_sym.setFocusPolicy(Qt.NoFocus)
        self.main_irrep = QComboBox(self)
        self.main_irrep.setFocusPolicy(Qt.NoFocus)
        self.main_irrep.addItems(self.irrep)
        self.main_irrep.setCurrentIndex(0)
        self.main_irrep_asym = QLabel("", self)
        self.main_irrep_asym.setFocusPolicy(Qt.NoFocus)
        self.set_product_irrep("")

        self.main_clear = QPushButton("clear")
        self.main_clear.setFocusPolicy(Qt.NoFocus)

        # connections.
        self.main_g_type.currentIndexChanged.connect(self.set_group_type)
        self.main_c_type.currentTextChanged.connect(self.set_crystal_type)
        self.main_group.currentTextChanged.connect(self.set_group)

        self.main_symmetry_operation.clicked.connect(self.show_symmetry_operation)
        self.main_character_table.clicked.connect(self.show_character_table)
        self.main_wyckoff.clicked.connect(self.show_wyckoff)
        self.main_product_table.clicked.connect(self.show_product_table)

        self.main_harmonics.clicked.connect(self.show_harmonics)
        self.main_harmonics_to_gen.clicked.connect(self.show_harmonics_decomp)

        self.main_response.clicked.connect(self.show_response)

        self.main_atomic_mp.clicked.connect(self.show_atomic_mp)
        self.main_atomic_mp_btype.currentIndexChanged.connect(self.set_atomic_mp_btype)

        self.main_v_cluster.clicked.connect(self.show_v_cluster)

        self.main_irrep1.currentTextChanged.connect(self.set_product_irrep)
        self.main_irrep2.currentTextChanged.connect(self.set_product_irrep)
        self.main_irrep.currentTextChanged.connect(self.set_product_irrep)

        self.main_clear.clicked.connect(self.clear_data)

        # tab contents.
        self.tab = QTabWidget(self)
        self.create_tab1()
        self.create_tab2()

        # main layout
        self.layout = QGridLayout(self)
        self.layout.addWidget(self.main_g_type, 0, 0, 1, 2)
        self.layout.addWidget(self.main_c_type, 0, 2, 1, 3)
        self.layout.addWidget(self.main_group, 0, 5, 1, 2)

        self.layout.addWidget(self.main_symmetry_operation, 1, 0, 1, 2)
        self.layout.addWidget(self.main_character_table, 1, 2, 1, 3)
        self.layout.addWidget(self.main_wyckoff, 1, 5, 1, 2)
        self.layout.addWidget(self.main_product_table, 1, 7, 1, 2)

        self.layout.addWidget(self.main_irrep_sym_label, 2, 0, 1, 1)
        self.layout.addWidget(self.main_irrep1, 2, 1, 1, 1)
        self.layout.addWidget(self.main_irrep2, 2, 2, 1, 2)
        self.layout.addWidget(self.main_irrep_sym, 2, 4, 1, 2)
        self.layout.addWidget(self.main_irrep_asym_label, 2, 6, 1, 1)
        self.layout.addWidget(self.main_irrep, 2, 7, 1, 2)
        self.layout.addWidget(self.main_irrep_asym, 2, 9, 1, 1)

        self.layout.addWidget(self.main_harmonics, 3, 0, 1, 2)
        self.layout.addWidget(self.main_harmonics_type, 3, 2, 1, 1)
        self.layout.addWidget(self.main_harmonics_rank_label, 3, 3, 1, 1)
        self.layout.addWidget(self.main_harmonics_rank, 3, 4, 1, 1)
        self.layout.addWidget(self.main_harmonics_to_label, 3, 6, 1, 1)
        self.layout.addWidget(self.main_harmonics_to_pg, 3, 7, 1, 1)
        self.layout.addWidget(self.main_harmonics_to_gen, 3, 8, 1, 1)

        self.layout.addWidget(self.main_response, 4, 0, 1, 2)
        self.layout.addWidget(self.main_response_t_type, 4, 2, 1, 1)
        self.layout.addWidget(self.main_response_i_type, 4, 3, 1, 1)
        self.layout.addWidget(self.main_response_rank_label, 4, 4, 1, 1)
        self.layout.addWidget(self.main_response_rank, 4, 5, 1, 1)

        self.layout.addWidget(self.main_atomic_mp, 5, 0, 1, 2)
        self.layout.addWidget(self.main_atomic_mp_head, 5, 2, 1, 1)
        self.layout.addWidget(self.main_atomic_mp_btype, 5, 3, 1, 1)
        self.layout.addWidget(self.main_atomic_mp_braket_label, 5, 4, 1, 1)
        self.layout.addWidget(self.main_atomic_mp_bra_basis, 5, 5, 1, 2)
        self.layout.addWidget(self.main_atomic_mp_ket_basis, 5, 7, 1, 2)

        self.layout.addWidget(self.main_v_cluster, 6, 0, 1, 2)
        self.layout.addWidget(self.main_v_cluster_wp, 6, 2, 1, 2)
        self.layout.addWidget(self.main_v_cluster_bond, 6, 4, 1, 2)

        self.layout.addWidget(self.main_clear, 7, 9, 1, 1)

        self.layout.addWidget(self.tab, 8, 0, 1, 10)

    # ==================================================
    def set_group_object(self, tag):
        """
        set group object and properties.

        Args:
            tag (TagGroup or str): group tag.

        Notes:
            - set the following properties, self.pg, self._group, self._pgroup, self.wp, self.irrep, self.n_op, self.n_pset.
        """
        if type(tag) == str:
            if tag.count(" ") > 0:
                tag = tag.split(" ")[1]
            tag = TagGroup(tag)
        self.pg = tag.is_point_group()
        if self.pg:
            self._group = PointGroup(tag, self._core)
            self._pgroup = self._group
            self._qtdraw.setting["cluster"] = True
            self._qtdraw._toggle_clip(False)
            self._qtdraw.button_repeat.hide()
            self.n_pset = 1
        else:
            self._group = SpaceGroup(tag, self._core)
            self._pgroup = self._group.pg
            self._qtdraw.setting["cluster"] = False
            self._qtdraw._toggle_clip(True)
            self._qtdraw.button_repeat.show()
            self.n_pset = len(self._group.symmetry_operation.plus_set)
        self.wp = list(map(str, self._pgroup.wyckoff.keys()))[::-1]
        self.irrep = list(map(str, self._pgroup.character.irrep_list))
        self.n_op = len(self._group.symmetry_operation)

    # ==================================================
    def set_group(self, tag):
        if tag == "":
            return

        self.set_group_object(tag)

        self.main_v_cluster_wp.clear()
        self.main_v_cluster_wp.addItems(self.wp)
        self.main_v_cluster_wp.setCurrentIndex(0)

        self.main_irrep1.clear()
        self.main_irrep1.addItems(self.irrep)
        self.main_irrep1.setCurrentIndex(0)
        self.main_irrep2.clear()
        self.main_irrep2.addItems(self.irrep)
        self.main_irrep2.setCurrentIndex(0)
        self.main_irrep.clear()
        self.main_irrep.addItems(self.irrep)
        self.main_irrep.setCurrentIndex(0)

    # ==================================================
    def set_group_type(self, point_group):
        if point_group:
            tag = str(self._pgroup.tag)
        else:
            tag = self.main_group.currentText()
            if tag[-2:] == "-1":
                tag = tag[:-2]
            tag = tag.split(" ")[1] + "^1"
        self.set_group_object(tag)

        crystal = self.main_c_type.currentText()
        self.main_group.clear()
        lst = self.crystal[self.pg][crystal]
        no = lst.index(str(self._group.tag.no) + ". " + tag)
        self.main_group.addItems(lst)
        self.main_group.setCurrentIndex(no)

    # ==================================================
    def set_crystal_type(self, crystal):
        tags = self.crystal[self.pg][crystal]
        self.set_group_object(tags[0])

        self.main_group.clear()
        self.main_group.addItems(tags)
        self.main_group.setCurrentIndex(0)
        self._qtdraw.set_crystal(crystal)

    # ==================================================
    def set_product_irrep(self, _):
        irrep1 = self.main_irrep1.currentText()
        if irrep1 not in self.irrep:
            return
        irrep2 = self.main_irrep2.currentText()
        if irrep2 not in self.irrep:
            return
        irrep = self.main_irrep.currentText()
        if irrep not in self.irrep:
            return

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

        sym = self._pgroup.character.symmetric_product_decomposition((irrep1, irrep2), ret_ex=True)
        asym = self._pgroup.character.anti_symmetric_product_decomposition(irrep, ret_ex=True)
        self.main_irrep_sym.setText(remove_latex(str(sym)))
        self.main_irrep_asym.setText(remove_latex(str(asym)))

    # ==================================================
    def show_symmetry_operation(self):
        create_symmetry_operation(self._group, self)

    # ==================================================
    def show_character_table(self):
        create_character_table(self._pgroup, self)

    # ==================================================
    def show_wyckoff(self):
        create_wyckoff(self._group, self)

    # ==================================================
    def show_product_table(self):
        create_product_table(self._pgroup, self)

    # ==================================================
    def show_harmonics(self):
        head = self.main_harmonics_type.currentText()
        rank = int(self.main_harmonics_rank.currentText())
        create_harmonics(self._pgroup, rank, head, self._qtdraw, self)

    # ==================================================
    def show_harmonics_decomp(self):
        head = self.main_harmonics_type.currentText()
        rank = int(self.main_harmonics_rank.currentText())
        to_pg = self.main_harmonics_to_pg.currentText()
        create_harmonics_decomp(self._pgroup, rank, head, to_pg, self)

    # ==================================================
    def show_response(self):
        rank = int(self.main_response_rank.currentText())
        i_type = self.main_response_i_type.currentText()
        t_type = self.main_response_t_type.currentText()
        create_response(self._pgroup, rank, i_type, t_type, self)

    # ==================================================
    def show_atomic_mp(self):
        head = self.main_atomic_mp_head.currentText()
        btype = self.main_atomic_mp_btype.currentText()
        bra = self.main_atomic_mp_bra_basis.currentText()
        ket = self.main_atomic_mp_ket_basis.currentText()

        spinful = btype == "jm"
        am = self._pgroup.atomic_multipole_basis(bra, ket, spinful)
        if head != "":
            am = am.select(head=head)

        create_atomic_mp(self._pgroup, bra, ket, am, self)

    # ==================================================
    def set_atomic_mp_btype(self, g):
        if g == 0:
            lst = ["s", "p", "d", "f"]
        else:  # jm
            lst = ["(1/2,0)", "(1/2,1)", "(3/2,1)", "(3/2,2)", "(5/2,2)", "(5/2,3)", "(7/2,3)"]
        self.main_atomic_mp_bra_basis.clear()
        self.main_atomic_mp_ket_basis.clear()
        self.main_atomic_mp_bra_basis.addItems(lst)
        self.main_atomic_mp_ket_basis.addItems(lst)
        self.main_atomic_mp_bra_basis.setCurrentIndex(0)
        self.main_atomic_mp_ket_basis.setCurrentIndex(0)

    # ==================================================
    def show_v_cluster(self):
        wp = self.main_v_cluster_wp.currentText()
        bond = self.main_v_cluster_bond.text()
        create_v_cluster(self._pgroup, wp, bond, self._qtdraw, self)

    # ==================================================
    def clear_data(self):
        self._qtdraw._clear()
        self._qtdraw.set_crystal(self.main_c_type.currentText())

    # ==================================================
    def create_tab1(self):
        self.tab1 = QWidget()
        self.tab.addTab(self.tab1, "object drawing")

        site_label = QLabel("SITE\ne.g., [1/2,1/2,0] (position).", self)
        site_pos = QLineEdit("[ 1/2, 1/2, 0 ]", self)

        bond_label = QLabel(
            "BOND\ne.g., [0,0,0];[1/2,1/2,0] (tail-head), [1/2,1/2,0]@[1/4,1/4,0] (vector-center), [0,0,0]:[1/2,1/2,0] (start-vector).",
            self,
        )
        bond_pos = QLineEdit("[ 0, 0, 0 ]; [ 1/2, 1/2, 0 ]", self)

        vector_label = QLabel(
            "VECTOR\ne.g., [0,0,1]@[1/2,1/2,0] (vector-center)",
            self,
        )
        vector_pos = QLineEdit("[ 0, 0, 1 ] @ [ 1/2, 1/2, 0 ]", self)
        vector_type = QComboBox(self)
        vector_type.addItems(["Q", "G", "T", "M"])
        vector_type.setCurrentIndex(0)

        orbital_label = QLabel(
            "ORBITAL\ne.g., 3z**2-r**2@[1/4,1/4,0] (orbital-center)",
            self,
        )
        orbital_pos = QLineEdit("3z**2 - r**2 @ [ 1/4, 1/4, 0 ]", self)
        orbital_type = QComboBox(self)
        orbital_type.addItems(["Q", "G", "T", "M"])
        orbital_type.setCurrentIndex(0)

        tab1_v_spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        tab1_grid = QGridLayout(self.tab1)
        tab1_grid.addWidget(site_label, 0, 0, 1, 9)
        tab1_grid.addWidget(site_pos, 1, 0, 1, 9)

        tab1_grid.addWidget(bond_label, 2, 0, 1, 9)
        tab1_grid.addWidget(bond_pos, 3, 0, 1, 9)

        tab1_grid.addWidget(vector_label, 4, 0, 1, 9)
        tab1_grid.addWidget(vector_pos, 5, 0, 1, 8)
        tab1_grid.addWidget(vector_type, 5, 8, 1, 1)

        tab1_grid.addWidget(orbital_label, 6, 0, 1, 9)
        tab1_grid.addWidget(orbital_pos, 7, 0, 1, 8)
        tab1_grid.addWidget(orbital_type, 7, 8, 1, 1)

        tab1_grid.addItem(tab1_v_spacer, 8, 1, 1, 1)

        show_lbl = rcParams["show_label"]

        # --- plot site ---
        def plot_site():
            pos = site_pos.text()
            try:
                if self.pg:
                    r = self._group.site_mapping(pos)
                else:
                    r = self._group.site_mapping(pos, plus_set=True)
                basic_num = len(r) // self.n_pset
            except Exception:
                return
            pname = self._qtdraw._get_name("site")
            pname0 = f"S{int(pname[1:])+1}"
            self._qtdraw._close_dialog()
            color = rcParams["site_color"]
            for no, (s, mp) in enumerate(r.items()):
                mp = MaterialModel._mapping_str(mp)
                idx = no % basic_num
                pset = no // basic_num
                if self.n_pset > 1:
                    pname = pname0 + f"({pset+1})"
                else:
                    pname = pname0
                label = f"s{idx+1}:{mp}"
                self._qtdraw.plot_site(s, color=color, name=pname, label=label, show_lbl=show_lbl)
            self._qtdraw._plot_all_object()

        site_pos.returnPressed.connect(plot_site)

        # --- plot bond ---
        def plot_bond():
            pos = bond_pos.text()
            try:
                if self.pg:
                    r, nd = self._group.bond_mapping(pos)
                else:
                    r, nd = self._group.bond_mapping(pos, plus_set=True)
                basic_num = len(r) // self.n_pset
            except Exception:
                return
            pname = self._qtdraw._get_name("bond")
            pname0 = f"B{int(pname[1:])+1}"
            self._qtdraw._close_dialog()
            color1 = rcParams["bond_color1"]
            if nd:
                color2 = color1
            else:
                color2 = rcParams["bond_color2"]
            for no, (b, mp) in enumerate(r.items()):
                b = NSArray(b)
                v, c = b.convert_bond("bond")
                mp = MaterialModel._mapping_str(mp)
                idx = no % basic_num
                pset = no // basic_num
                if self.n_pset > 1:
                    pname = pname0 + f"({pset+1})"
                else:
                    pname = pname0
                label = f"b{idx+1}:{mp}"
                self._qtdraw.plot_bond(c, v, color=color1, color2=color2, name=pname, label=label, show_lbl=show_lbl)
            self._qtdraw._plot_all_object()

        bond_pos.returnPressed.connect(plot_bond)

        # --- plot vector ---
        def plot_vector():
            pos = vector_pos.text()
            head = vector_type.currentText()
            try:
                vc = pos.split("@")
                if self.pg:
                    c_mapping = self._group.site_mapping(vc[1])
                else:
                    c_mapping = self._group.site_mapping(vc[1], plus_set=True)
                basic_num = len(c_mapping) // self.n_pset
                c = NSArray.from_str(c_mapping.keys())
                v = vc[0]
            except Exception:
                return
            pname = self._qtdraw._get_name("vector")
            pname0 = f"V{int(pname[3:])+1}"
            self._qtdraw._close_dialog()
            color = rcParams["vector_color_" + head]
            for no in range(len(c)):
                idx = no % basic_num
                pset = no // basic_num
                if self.n_pset > 1:
                    pname = pname0 + f"({pset+1})"
                else:
                    pname = pname0
                label = f"v{idx+1}"
                self._qtdraw.plot_vector(c[no], v, color=color, name=pname, label=label, show_lbl=show_lbl)
            self._qtdraw._plot_all_object()

        vector_pos.returnPressed.connect(plot_vector)

        # --- plot orbital ---
        def plot_orbital():
            pos = orbital_pos.text()
            head = orbital_type.currentText()
            try:
                sc = pos.split("@")
                if self.pg:
                    c_mapping = self._group.site_mapping(sc[1])
                else:
                    c_mapping = self._group.site_mapping(sc[1], plus_set=True)
                basic_num = len(c_mapping) // self.n_pset
                c = NSArray.from_str(c_mapping.keys())
                s = sc[0]
            except Exception:
                return
            pname = self._qtdraw._get_name("orbital")
            pname0 = f"O{int(pname[3:])+1}"
            self._qtdraw._close_dialog()
            color = rcParams["orbital_color_" + head]
            for no in range(len(c)):
                idx = no % basic_num
                pset = no // basic_num
                if self.n_pset > 1:
                    pname = pname0 + f"({pset+1})"
                else:
                    pname = pname0
                label = f"o{idx+1}"
                self._qtdraw.plot_orbital(c[no], s, size=0.3, color=color, name=pname, label=label, show_lbl=show_lbl)
            self._qtdraw._plot_all_object()

        orbital_pos.returnPressed.connect(plot_orbital)

    # ==================================================
    def create_tab2(self):
        self.tab2 = QWidget()
        self.tab.addTab(self.tab2, "basis drawing")

        site_proj_label = QLabel(
            "SITE\ne.g., [1/2,1/2,0] (position)   [head]   →   [head] [SAMB]",
            self,
        )
        site_proj_pos = QLineEdit("[ 1/2, 1/2, 0 ]", self)
        site_proj_label1 = QLabel("→", self)
        site_proj_label1.setAlignment(Qt.AlignCenter)
        site_proj_irrep1 = QComboBox(self)
        site_proj_irrep1.addItems([""])
        site_proj_irrep1.setCurrentIndex(0)
        site_proj_draw_button = QPushButton("draw", self)
        site_proj_draw_button.setFocusPolicy(Qt.NoFocus)

        bond_proj_label = QLabel(
            "BOND\ne.g., [0,0,0];[1/2,1/2,0] (tail-head), [1/2,1/2,0]@[1/4,1/4,0] (vector-center), [0,0,0]:[1/2,1/2,0] (start-vector)   [head]   →   [head] [SAMB]",
            self,
        )
        bond_proj_pos = QLineEdit("[ 1/2, 1/2, 0 ] @ [ 1/4, 1/4, 0 ]", self)
        bond_proj_label1 = QLabel("→", self)
        bond_proj_label1.setAlignment(Qt.AlignCenter)
        bond_proj_irrep1 = QComboBox(self)
        bond_proj_irrep1.addItems([""])
        bond_proj_irrep1.setCurrentIndex(0)
        bond_proj_draw_button = QPushButton("draw", self)
        bond_proj_draw_button.setFocusPolicy(Qt.NoFocus)

        vector_proj_label = QLabel(
            "VECTOR\ne.g., [1/2,1/2,0] (site) or [0,0,0];[1/2,1/2,0] (bond)   [head]   →   [head] [SAMB]",
            self,
        )
        vector_proj_pos = QLineEdit("[ 1/2, 1/2, 0 ]", self)
        vector_proj_type = QComboBox(self)
        vector_proj_type.addItems(["Q", "G", "T", "M"])
        vector_proj_type.setCurrentIndex(0)
        vector_proj_type1 = QComboBox(self)
        vector_proj_type1.addItems(["Q", "G", "T", "M"])
        vector_proj_type1.setCurrentIndex(0)
        vector_proj_label1 = QLabel("→", self)
        vector_proj_label1.setAlignment(Qt.AlignCenter)
        vector_proj_irrep1 = QComboBox(self)
        vector_proj_irrep1.addItems([""])
        vector_proj_irrep1.setCurrentIndex(0)
        vector_proj_draw_button = QPushButton("draw", self)
        vector_proj_draw_button.setFocusPolicy(Qt.NoFocus)

        orbital_proj_label = QLabel(
            "ORBITAL\ne.g., [1/2,1/2,0] (site) or [0,0,0];[1/2/1,2/0] (bond)   [head] [rank]   →   [head] [SAMB]",
            self,
        )
        orbital_proj_pos = QLineEdit("[ 0, 0, 0 ]; [ 1/2, 1/2, 0 ]", self)
        orbital_proj_type = QComboBox(self)
        orbital_proj_type.addItems(["Q", "G", "T", "M"])
        orbital_proj_type.setCurrentIndex(0)
        orbital_proj_type1 = QComboBox(self)
        orbital_proj_type1.addItems(["Q", "G", "T", "M"])
        orbital_proj_type1.setCurrentIndex(0)
        orbital_proj_label1 = QLabel("→", self)
        orbital_proj_label1.setAlignment(Qt.AlignCenter)
        orbital_proj_irrep1 = QComboBox(self)
        orbital_proj_irrep1.addItems([""])
        orbital_proj_irrep1.setCurrentIndex(0)
        orbital_proj_rank = QComboBox(self)
        orbital_proj_rank.setFocusPolicy(Qt.NoFocus)
        orbital_proj_rank.addItems(map(str, range(12)))
        orbital_proj_rank.setCurrentIndex(0)
        orbital_proj_draw_button = QPushButton("draw", self)
        orbital_proj_draw_button.setFocusPolicy(Qt.NoFocus)

        hopping_proj_label = QLabel(
            "HOPPING (imag)\ne.g., [0,0,0];[1/2,1/2,0] (bond)",
            self,
        )
        hopping_proj_pos = QLineEdit("[0, 0, 0]; [1/2, 1/2, 0]", self)

        tab2_v_spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        tab2_grid = QGridLayout(self.tab2)

        tab2_grid.addWidget(site_proj_label, 0, 0, 1, 9)
        tab2_grid.addWidget(site_proj_pos, 1, 0, 1, 7)
        tab2_grid.addWidget(site_proj_label1, 2, 0, 1, 1)
        tab2_grid.addWidget(site_proj_irrep1, 2, 1, 1, 7)
        tab2_grid.addWidget(site_proj_draw_button, 2, 8, 1, 1)

        tab2_grid.addWidget(bond_proj_label, 3, 0, 1, 9)
        tab2_grid.addWidget(bond_proj_pos, 4, 0, 1, 7)
        tab2_grid.addWidget(bond_proj_label1, 5, 0, 1, 1)
        tab2_grid.addWidget(bond_proj_irrep1, 5, 1, 1, 7)
        tab2_grid.addWidget(bond_proj_draw_button, 5, 8, 1, 1)

        tab2_grid.addWidget(vector_proj_label, 6, 0, 1, 9)
        tab2_grid.addWidget(vector_proj_pos, 7, 0, 1, 7)
        tab2_grid.addWidget(vector_proj_type, 7, 7, 1, 1)
        tab2_grid.addWidget(vector_proj_label1, 8, 0, 1, 1)
        tab2_grid.addWidget(vector_proj_type1, 8, 1, 1, 1)
        tab2_grid.addWidget(vector_proj_irrep1, 8, 2, 1, 6)
        tab2_grid.addWidget(vector_proj_draw_button, 8, 8, 1, 1)

        tab2_grid.addWidget(orbital_proj_label, 9, 0, 1, 9)
        tab2_grid.addWidget(orbital_proj_pos, 10, 0, 1, 7)
        tab2_grid.addWidget(orbital_proj_type, 10, 7, 1, 1)
        tab2_grid.addWidget(orbital_proj_rank, 10, 8, 1, 1)
        tab2_grid.addWidget(orbital_proj_label1, 11, 0, 1, 1)
        tab2_grid.addWidget(orbital_proj_type1, 11, 1, 1, 1)
        tab2_grid.addWidget(orbital_proj_irrep1, 11, 2, 1, 6)
        tab2_grid.addWidget(orbital_proj_draw_button, 11, 8, 1, 1)

        tab2_grid.addWidget(hopping_proj_label, 12, 0, 1, 9)
        tab2_grid.addWidget(hopping_proj_pos, 13, 0, 1, 9)

        tab2_grid.addItem(tab2_v_spacer, 14, 1, 1, 1)

        show_lbl = rcParams["show_label"]

        # --- plot site_cluster SAMB ---
        def gen_site_cluster():
            combined_info = self._create_combined(site_proj_pos.text(), 0, "Q")
            if combined_info is None:
                return

            self.tab2_site_proj_c_samb, self.tab2_site_proj_site, self.tab2_site_proj_z_samb = combined_info

            site_cluster_samb_select()

        def site_cluster_samb_select():
            self.tab2_site_proj_comb_select = self.tab2_site_proj_z_samb["Q"]
            site_proj_irrep1.clear()
            comb = [self._combined_format(i) for i in self.tab2_site_proj_comb_select]
            site_proj_irrep1.addItems(comb)
            site_proj_irrep1.setCurrentIndex(0)

        def plot_site_cluster_samb():
            irrep = site_proj_irrep1.currentIndex()
            try:
                eq = self.tab2_site_proj_comb_select[irrep][1]
            except (IndexError, AttributeError):
                return
            cluster_obj = NSArray(str([0] * len(self.tab2_site_proj_site)))
            for i in eq:
                coeff, _, tag_c = i
                cluster = self.tab2_site_proj_c_samb[tag_c]
                cluster_obj += coeff * cluster

            color = []
            for orb in cluster_obj:
                if orb > 0:
                    c = "salmon"
                elif orb < 0:
                    c = "aqua"
                else:
                    c = "silver"
                color.append(c)

            cluster_obj /= np.abs(cluster_obj).max()

            self._qtdraw._close_dialog()
            lbl = site_proj_irrep1.currentText().replace("(", "[").replace(")", "]")
            pname = "Z_" + self._qtdraw._get_name("site")
            if self.n_pset == 1:
                for s, orb, cl in zip(self.tab2_site_proj_site, cluster_obj, color):
                    if cl == "silver":
                        orb = 1
                    self._qtdraw.plot_site(
                        s,
                        size=abs(orb),
                        color=cl,
                        name=pname,
                        label=lbl,
                        show_lbl=show_lbl,
                    )
            else:
                for p in self._group.symmetry_operation.plus_set:
                    for s, orb, cl in zip(self.tab2_site_proj_site, cluster_obj, color):
                        if cl == "silver":
                            orb = 1
                        self._qtdraw.plot_site(
                            s + p,
                            size=abs(orb),
                            color=cl,
                            name=pname,
                            label=lbl,
                            show_lbl=show_lbl,
                        )
            self._qtdraw._plot_all_object()

        site_proj_pos.returnPressed.connect(gen_site_cluster)
        site_proj_draw_button.clicked.connect(plot_site_cluster_samb)

        # --- plot bond_cluster SAMB ---
        def gen_bond_cluster():
            combined_info = self._create_combined(bond_proj_pos.text(), 0, "Q", ret_bond=True)
            if combined_info is None:
                return

            self.tab2_bond_proj_c_samb, self.tab2_bond_proj_site, self.tab2_bond_proj_z_samb = combined_info

            bond_cluster_samb_select()

        def bond_cluster_samb_select():
            self.tab2_bond_proj_comb_select = self.tab2_bond_proj_z_samb["Q"] + self.tab2_bond_proj_z_samb["T"]
            bond_proj_irrep1.clear()
            comb = [self._combined_format(i) for i in self.tab2_bond_proj_comb_select]
            bond_proj_irrep1.addItems(comb)
            bond_proj_irrep1.setCurrentIndex(0)

        def plot_bond_cluster_samb():
            irrep = bond_proj_irrep1.currentIndex()
            head = bond_proj_irrep1.currentText()[0]
            try:
                eq = self.tab2_bond_proj_comb_select[irrep][1]
            except (IndexError, AttributeError):
                return
            cluster_obj = NSArray(str([0] * len(self.tab2_bond_proj_site)))
            for i in eq:
                coeff, _, tag_c = i
                if head == "Q":
                    cluster = self.tab2_bond_proj_c_samb[tag_c]
                else:
                    cluster = self.tab2_bond_proj_c_samb[tag_c].im()
                cluster_obj += coeff * cluster
            color = []
            if head == "Q":
                for orb in cluster_obj:
                    if orb > 0:
                        c = "salmon"
                    elif orb < 0:
                        c = "aqua"
                    else:
                        c = "silver"
                    color.append(c)
            else:
                for orb in cluster_obj:
                    if orb == 0:
                        c = "silver"
                    else:
                        c = "salmon"
                    color.append(c)

            cluster_obj /= np.abs(cluster_obj).max()

            self._qtdraw._close_dialog()
            lbl = bond_proj_irrep1.currentText().replace("(", "[").replace(")", "]")
            pname = "Z_" + self._qtdraw._get_name("bond")
            if head == "Q":
                if self.n_pset == 1:
                    for s, orb, cl in zip(self.tab2_bond_proj_site, cluster_obj, color):
                        v, c = s.convert_bond("bond")
                        if cl == "silver":
                            orb = 1
                        self._qtdraw.plot_bond(
                            c, v, color=cl, color2=cl, width=abs(orb), name=pname, label=lbl, show_lbl=show_lbl
                        )
                else:
                    for p in self._group.symmetry_operation.plus_set:
                        for s, orb, cl in zip(self.tab2_bond_proj_site, cluster_obj, color):
                            v, c = s.convert_bond("bond")
                            if cl == "silver":
                                orb = 1
                            self._qtdraw.plot_bond(
                                c + p, v, color=cl, color2=cl, width=abs(orb), name=pname, label=lbl, show_lbl=show_lbl
                            )
            else:
                if self.n_pset == 1:
                    for s, orb, cl in zip(self.tab2_bond_proj_site, cluster_obj, color):
                        v, c = s.convert_bond("bond")
                        if cl == "silver":
                            orb = 1
                            self._qtdraw.plot_bond(
                                c, v, color=cl, color2=cl, width=abs(orb), name=pname, label=lbl, show_lbl=show_lbl
                            )
                        else:
                            v = v.transform(self._qtdraw._A)
                            if orb < 0:
                                v = -v
                            norm = v.norm() * 0.7
                            self._qtdraw.plot_vector(
                                c, v, color=cl, width=abs(orb), length=norm, offset=-0.5, name=pname, label=lbl, show_lbl=show_lbl
                            )
                else:
                    for p in self._group.symmetry_operation.plus_set:
                        for s, orb, cl in zip(self.tab2_bond_proj_site, cluster_obj, color):
                            v, c = s.convert_bond("bond")
                            if cl == "silver":
                                orb = 1
                                self._qtdraw.plot_bond(
                                    c + p, v, color=cl, color2=cl, width=abs(orb), name=pname, label=lbl, show_lbl=show_lbl
                                )
                            else:
                                v = v.transform(self._qtdraw._A)
                                if orb < 0:
                                    v = -v
                                norm = v.norm() * 0.7
                                self._qtdraw.plot_vector(
                                    c + p,
                                    v,
                                    color=cl,
                                    width=abs(orb),
                                    length=norm,
                                    offset=-0.5,
                                    name=pname,
                                    label=lbl,
                                    show_lbl=show_lbl,
                                )

            self._qtdraw._plot_all_object()

        bond_proj_pos.returnPressed.connect(gen_bond_cluster)
        bond_proj_draw_button.clicked.connect(plot_bond_cluster_samb)

        # --- plot combined SAMB (vector) ---
        def gen_z_samb_vector():
            combined_info = self._create_combined(vector_proj_pos.text(), 1, vector_proj_type.currentText())
            if combined_info is None:
                return

            self.tab2_vector_proj_c_samb, self.tab2_vector_proj_site, self.tab2_vector_proj_z_samb = combined_info

            select_z_samb_vector()

        def select_z_samb_vector():
            self.tab2_vector_proj_comb_select = self.tab2_vector_proj_z_samb[vector_proj_type1.currentText()]
            vector_proj_irrep1.clear()
            comb = [i[0] for i in self.tab2_vector_proj_comb_select]
            vector_proj_irrep1.addItems(comb)
            vector_proj_irrep1.setCurrentIndex(0)

        def plot_vector_object(site, obj, rep, pname, label, color):
            if self.n_pset == 1:
                for s, c in zip(site, obj):
                    if c != 0:
                        c = str(c.subs(rep).T[:])
                        c = NSArray(c)
                        d = c.norm()
                        self._qtdraw.plot_vector(s, c, length=d, color=color, name=pname, label=label, show_lbl=show_lbl)
            else:
                for p in self._group.symmetry_operation.plus_set:
                    for s, c in zip(site, obj):
                        if c != 0:
                            c = str(c.subs(rep).T[:])
                            c = NSArray(c)
                            d = c.norm()
                            self._qtdraw.plot_vector(s + p, c, length=d, color=color, name=pname, label=label, show_lbl=show_lbl)

        def plot_z_samb_vector():
            irrep = vector_proj_irrep1.currentIndex()
            try:
                eq = self.tab2_vector_proj_comb_select[irrep][1]
            except (IndexError, AttributeError):
                return
            cluster_obj = NSArray(str([0] * len(self.tab2_vector_proj_site)))
            v = NSArray.vector3d()

            for i in eq:
                coeff, tag_h, tag_c = i
                harm = self._pgroup.harmonics[tag_h].expression(v=v)
                cluster = self.tab2_vector_proj_c_samb[tag_c]
                cluster_obj += coeff * harm * cluster
            if self._different_time_reversal(vector_proj_type.currentText(), vector_proj_type1.currentText()):
                cluster_obj *= -sp.I

            rep = {v[0]: sp.Matrix([1, 0, 0]), v[1]: sp.Matrix([0, 1, 0]), v[2]: sp.Matrix([0, 0, 1])}
            color = rcParams["vector_color_" + vector_proj_type.currentText()]
            self._qtdraw._close_dialog()
            lbl = vector_proj_irrep1.currentText().replace("(", "[").replace(")", "]")
            pname = "Z_" + self._qtdraw._get_name("vector")

            plot_vector_object(self.tab2_vector_proj_site, cluster_obj, rep, pname, lbl, color)

            self._qtdraw._plot_all_object()

        vector_proj_pos.returnPressed.connect(gen_z_samb_vector)
        vector_proj_type1.currentIndexChanged.connect(select_z_samb_vector)
        vector_proj_draw_button.clicked.connect(plot_z_samb_vector)

        # --- plot combined SAMB (orbital) ---
        def gen_z_samb_orbital():
            combined_info = self._create_combined(
                orbital_proj_pos.text(), orbital_proj_rank.currentText(), orbital_proj_type.currentText()
            )
            if combined_info is None:
                return

            self.tab2_orbital_proj_c_samb, self.tab2_orbital_proj_site, self.tab2_orbital_proj_z_samb = combined_info

            select_z_samb_orbital()

        def select_z_samb_orbital():
            self.tab2_orbital_proj_comb_select = self.tab2_orbital_proj_z_samb[orbital_proj_type1.currentText()]
            orbital_proj_irrep1.clear()
            comb = [i[0] for i in self.tab2_orbital_proj_comb_select]
            orbital_proj_irrep1.addItems(comb)
            orbital_proj_irrep1.setCurrentIndex(0)

        def plot_orbital_object(site, obj, pname, label, color):
            if self.n_pset == 1:
                for s, orb in zip(site, obj):
                    self._qtdraw.plot_orbital(
                        s,
                        orb,
                        size=0.6,
                        scale=False,
                        color=color,
                        name=pname,
                        label=label,
                        show_lbl=show_lbl,
                    )
            else:
                for p in self._group.symmetry_operation.plus_set:
                    for s, orb in zip(site, obj):
                        self._qtdraw.plot_orbital(
                            s + p,
                            orb,
                            size=0.6,
                            scale=False,
                            color=color,
                            name=pname,
                            label=label,
                            show_lbl=show_lbl,
                        )

        def plot_z_samb_orbital():
            irrep = orbital_proj_irrep1.currentIndex()
            try:
                eq = self.tab2_orbital_proj_comb_select[irrep][1]
            except (IndexError, AttributeError):
                return
            cluster_obj = NSArray(str([0] * len(self.tab2_orbital_proj_site)))
            for i in eq:
                coeff, tag_h, tag_c = i
                harm = self._pgroup.harmonics[tag_h].expression()
                cluster = self.tab2_orbital_proj_c_samb[tag_c]
                cluster_obj += coeff * harm * cluster
            if self._different_time_reversal(orbital_proj_type.currentText(), orbital_proj_type1.currentText()):
                cluster_obj *= -sp.I

            self._qtdraw._close_dialog()
            color = rcParams["orbital_color_" + orbital_proj_type.currentText()]
            lbl = orbital_proj_irrep1.currentText().replace("(", "[").replace(")", "]")
            pname = "Z_" + self._qtdraw._get_name("orbital")

            plot_orbital_object(self.tab2_orbital_proj_site, cluster_obj, pname, lbl, color)

            self._qtdraw._plot_all_object()

        orbital_proj_pos.returnPressed.connect(gen_z_samb_orbital)
        orbital_proj_type1.currentIndexChanged.connect(select_z_samb_orbital)
        orbital_proj_draw_button.clicked.connect(plot_z_samb_orbital)

        # --- plot hopping ---
        def plot_z_samb_hopping():
            combined_info = self._create_combined(hopping_proj_pos.text(), 1, "T")
            if combined_info is None:
                return

            c_samb, site, z_samb = combined_info

            try:
                eq = z_samb["Q"][0][1]
            except (IndexError, AttributeError):
                return
            cluster_obj = NSArray(str([0] * len(site)))
            v = NSArray.vector3d()

            for coeff, tag_h, tag_c in eq:
                harm = self._pgroup.harmonics[tag_h].expression(v=v)
                cluster = c_samb[tag_c]
                cluster_obj += coeff * harm * cluster

            cluster_obj *= -sp.I

            rep = {v[0]: sp.Matrix([1, 0, 0]), v[1]: sp.Matrix([0, 1, 0]), v[2]: sp.Matrix([0, 0, 1])}
            color = rcParams["vector_color_T"]
            self._qtdraw._close_dialog()
            lbl = "t_imag"
            pname = "Z_" + self._qtdraw._get_name("vector")

            plot_vector_object(site, cluster_obj, rep, pname, lbl, color)

            self._qtdraw._plot_all_object()

        hopping_proj_pos.returnPressed.connect(plot_z_samb_hopping)

    # ==================================================
    def _different_time_reversal(self, t1, t2):
        tp = {"Q": "E", "G": "E", "T": "M", "M": "M"}
        return tp[t1] != tp[t2]

    # ==================================================
    def _combined_format(self, tag_list):
        z_tag, x_tag, y_tag = tag_list
        t1 = (",".join(str(x_tag).split(",")[:-1]) + ")").replace("h", "a")
        t2 = ",".join(str(y_tag).split(",")[:-1]) + ")"
        tag = f"{z_tag} = {t1} x {t2}"
        return tag

    # ==================================================
    def _create_combined(self, site_bond, harm_rank, harm_head, ret_bond=False):
        t_rev = {"Q": "Q", "G": "G", "T": "Q", "M": "G"}

        try:
            pos = NSArray(site_bond)
            is_site = pos.style == "vector"
        except Exception:
            return None

        if is_site:
            c_samb, site = self._group.site_cluster_samb(pos)
        else:
            c_samb, bond = self._group.bond_cluster_samb(pos)
            if ret_bond:
                site = bond
            else:
                site = bond.convert_bond("bond")[1]

        x_tag = self._pgroup.harmonics.key_list().select(rank=int(harm_rank), head=t_rev[harm_head])
        if harm_head in ["T", "M"]:
            x_tag = [tag.reverse_t_type() for tag in x_tag]
        y_tag = list(c_samb.keys())
        z_samb_all = self._group.z_samb(x_tag, y_tag)
        z_samb = {"Q": [], "G": [], "T": [], "M": []}
        for tag, c in z_samb_all.items():
            tag_str = self._combined_format(tag)
            z_samb[tag[0].head].append((tag_str, c))
        for k in z_samb.keys():
            z_samb[k] = list(sorted(z_samb[k], key=lambda i: i[0]))

        return c_samb, site, z_samb
