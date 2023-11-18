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
    QCheckBox,
    QMessageBox,
)
from qtpy.QtCore import Qt
from gcoreutils.nsarray import NSArray
from gcoreutils.string_util import remove_space
from multipie.group.point_group import PointGroup
from multipie.group.space_group import SpaceGroup
from multipie.tag.tag_group import TagGroup
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
from qtdraw.multipie.plot_object import (
    check_get_site,
    check_get_bond,
    check_get_site_bond,
    check_linear_combination,
    create_samb_object,
    create_combined,
    plot_equivalent_site,
    plot_equivalent_bond,
    plot_vector_equivalent_site,
    plot_orbital_equivalent_site,
    plot_site_cluster,
    plot_bond_cluster,
    plot_vector_cluster,
    plot_orbital_cluster,
)
from qtdraw.multipie.dialog_modulation import DialogModulation
from qtdraw.core.qt_logging import dprint


# ==================================================
class DialogGroup(QDialog):
    # ==================================================
    def __init__(self, core, qtdraw, width=512, height=600, parent=None):
        """
        initialize the class.

        Args:
            core (MultiPieCore): MultiPie core.
            qtdraw (QtDraw): QtDraw.
            width (int, optional): window width.
            height (int, optional): window height.
            parent (_type_, optional): Qt parent object.
        """
        super().__init__(parent)
        self._core = core
        self._qtdraw = qtdraw
        self.crystal = [{}, {}]  # space/point group.
        for crystal in __def_dict__["crystal"]:
            self.crystal[0][crystal] = [
                f"{i.no}. {i} ({i.IS})"
                for i in TagGroup.create(crystal=crystal, space_group=True)
            ]
            self.crystal[1][crystal] = [
                f"{i.no}. {i} ({i.IS})" for i in TagGroup.create(crystal=crystal)
            ]

        self.setWindowTitle(
            f"QtDraw - Group Operations with MultiPie Ver. {self._qtdraw._multipie_loaded}"
        )
        self.resize(width, height)

        # default.
        tag = rcParams["group_tag"]

        self.set_group_object(tag)

        self.create_main_panel()

    # ==================================================
    def closeEvent(self, event):
        if not self.force_close:
            ret = QMessageBox.question(
                self, "", "Quit MultiPie Panel ?", QMessageBox.Ok, QMessageBox.Cancel
            )
            if ret != QMessageBox.Ok:
                event.ignore()
            else:
                self.close()
        else:
            self.close()

    # ==================================================
    def close(self):
        if self.tab2_modulated_vector_active:
            self.dialog_modulation_vector.close()
        if self.tab2_modulated_orbital_active:
            self.dialog_modulation_orbital.close()
        self._qtdraw.button_clear.show()
        self._qtdraw.button_multipie.show()
        self._qtdraw.button_repeat.show()
        super().close()

    # ==================================================
    def create_main_panel(self):
        """
        create main panel.
        """
        # group type selector.
        self.main_g_type = QComboBox(self)
        self.main_g_type.setFocusPolicy(Qt.NoFocus)
        self.main_g_type.addItems(["space group", "point group"])
        self.main_g_type.setCurrentIndex(self.pg)

        # crystal selector.
        self.main_c_type = QComboBox(self)
        self.main_c_type.setFocusPolicy(Qt.NoFocus)
        self.main_c_type.addItems(list(self.crystal[self.pg].keys()))
        self.main_c_type.setCurrentIndex(0)

        # group selector.
        self.main_group = QComboBox(self)
        self.main_group.setFocusPolicy(Qt.NoFocus)
        self.main_group.addItems(self.crystal[self.pg][self._group.tag.crystal])
        self.main_group.setCurrentIndex(0)

        # symmetry operation, character table, wyckoff, product table.
        self.main_symmetry_operation = QPushButton("symmetry operation", self)
        self.main_symmetry_operation.setFocusPolicy(Qt.NoFocus)
        self.main_character_table = QPushButton("character table", self)
        self.main_character_table.setFocusPolicy(Qt.NoFocus)
        self.main_wyckoff = QPushButton("Wyckoff position", self)
        self.main_wyckoff.setFocusPolicy(Qt.NoFocus)
        self.main_product_table = QPushButton("product table", self)
        self.main_product_table.setFocusPolicy(Qt.NoFocus)

        # harmonics.
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

        # response.
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

        # atomic multipole.
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

        # virtual cluster.
        self.main_v_cluster = QPushButton("virtual cluster", self)
        self.main_v_cluster.setFocusPolicy(Qt.NoFocus)
        self.main_v_cluster_wp = QComboBox(self)
        self.main_v_cluster_wp.setFocusPolicy(Qt.NoFocus)
        self.main_v_cluster_wp.addItems(self.wp)
        self.main_v_cluster_wp.setCurrentIndex(0)
        self.main_v_cluster_bond = QLineEdit("1", self)

        # product irrep. decomposition.
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

        # clear button.
        self.main_clear = QPushButton("clear")
        self.main_clear.setFocusPolicy(Qt.NoFocus)

        # site bond description.
        self.main_site_bond_label = QLabel(
            "SITE: [x,y,z],    BOND: [tail];[head] / [vector]@[center] / [start]:[vector]",
            self,
        )
        self.main_site_bond_label.setFocusPolicy(Qt.NoFocus)

        # tab contents.
        self.tab = QTabWidget(self)
        self.create_tab1_panel()
        self.create_tab2_panel()

        # main layout
        self.layout = QGridLayout(self)
        self.layout.addWidget(self.main_g_type, 0, 0, 1, 2)
        self.layout.addWidget(self.main_c_type, 0, 2, 1, 3)
        self.layout.addWidget(self.main_group, 0, 5, 1, 4)

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

        self.layout.addWidget(self.main_site_bond_label, 8, 0, 1, 9)

        self.layout.addWidget(self.tab, 9, 0, 1, 10)

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

    # ==================================================
    def set_group_object(self, tag):
        """
        set group object and properties.

        Args:
            tag (TagGroup or str): group tag.

        Notes:
            - set the following properties, self.pg, self._group, self._pgroup, self.wp, self.irrep, self.n_op, self.n_pset, self.pset.
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
            self.pset = NSArray("{[0,0,0]}")
        else:
            self._group = SpaceGroup(tag, self._core)
            self._pgroup = self._group.pg
            self._qtdraw.setting["cluster"] = False
            self._qtdraw._toggle_clip(True)
            self._qtdraw.button_repeat.show()
            self.n_pset = len(self._group.symmetry_operation.plus_set)
            self.pset = self._group.symmetry_operation.plus_set
        self.wp = list(map(str, self._pgroup.wyckoff.keys()))[::-1]
        self.irrep = list(map(str, self._pgroup.character.irrep_list))
        self.n_op = len(self._group.symmetry_operation)

    # ==================================================
    def set_group(self, tag):
        """
        set current group.

        Args:
            tag (TagGroup or str): group tag.
        """
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

        self.tab1_pgharm_type.setCurrentIndex(0)
        self.tab1_pgharm_rank.setCurrentIndex(0)
        self.tab1_pgharm_rank_select()

    # ==================================================
    def set_group_type(self, is_point_group):
        """
        set group type (point or space).

        Args:
            is_point_group (bool): point group ?
        """
        if is_point_group:
            tag = str(self._pgroup.tag)
        else:
            tag = self.main_group.currentText().split(" ")[1]
            if tag[-2:] == "-1":
                tag = tag[:-2]
            tag = tag + "^1"

        self.set_group_object(tag)

        crystal = self.main_c_type.currentText()
        self.main_group.clear()
        lst = self.crystal[self.pg][crystal]
        no = lst.index(
            str(self._group.tag.no) + ". " + tag + " (" + self._group.tag.IS + ")"
        )
        self.main_group.addItems(lst)
        self.main_group.setCurrentIndex(no)

    # ==================================================
    def set_crystal_type(self, crystal):
        """
        set crystal type.

        Args:
            crystal (str): crystal type.
        """
        tags = self.crystal[self.pg][crystal]
        self.set_group_object(tags[0])

        self.main_group.clear()
        self.main_group.addItems(tags)
        self.main_group.setCurrentIndex(0)
        self._qtdraw.set_crystal(crystal)

    # ==================================================
    def set_product_irrep(self, _):
        """
        set product irrep decomposition.
        """
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

        sym = self._pgroup.character.symmetric_product_decomposition(
            (irrep1, irrep2), ret_ex=True
        )
        asym = self._pgroup.character.anti_symmetric_product_decomposition(
            irrep, ret_ex=True
        )
        self.main_irrep_sym.setText(remove_latex(str(sym)))
        self.main_irrep_asym.setText(remove_latex(str(asym)))

    # ==================================================
    def show_symmetry_operation(self):
        """
        show symmetry operation panel.
        """
        create_symmetry_operation(self._group, self)

    # ==================================================
    def show_character_table(self):
        """
        show character table panel.
        """
        create_character_table(self._pgroup, self)

    # ==================================================
    def show_wyckoff(self):
        """
        show wyckoff panel.
        """
        create_wyckoff(self._group, self)

    # ==================================================
    def show_product_table(self):
        """
        show product table panel.
        """
        create_product_table(self._pgroup, self)

    # ==================================================
    def show_harmonics(self):
        """
        show harmonics panel.
        """
        head = self.main_harmonics_type.currentText()
        rank = int(self.main_harmonics_rank.currentText())
        create_harmonics(self._pgroup, rank, head, self._qtdraw, self)

    # ==================================================
    def show_harmonics_decomp(self):
        """
        show harmonics decomposition panel.
        """
        head = self.main_harmonics_type.currentText()
        rank = int(self.main_harmonics_rank.currentText())
        to_pg = self.main_harmonics_to_pg.currentText()
        create_harmonics_decomp(self._pgroup, rank, head, to_pg, self)

    # ==================================================
    def show_response(self):
        """
        show response panel.
        """
        rank = int(self.main_response_rank.currentText())
        i_type = self.main_response_i_type.currentText()
        t_type = self.main_response_t_type.currentText()
        create_response(self._pgroup, rank, i_type, t_type, self)

    # ==================================================
    def show_atomic_mp(self):
        """
        show atomic multipole panel.
        """
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
        """
        set atomic multipole basis type.

        Args:
            g (int): spinless or not.
        """
        if g == 0:
            lst = ["s", "p", "d", "f"]
        else:  # jm
            lst = [
                "(1/2,0)",
                "(1/2,1)",
                "(3/2,1)",
                "(3/2,2)",
                "(5/2,2)",
                "(5/2,3)",
                "(7/2,3)",
            ]
        self.main_atomic_mp_bra_basis.clear()
        self.main_atomic_mp_ket_basis.clear()
        self.main_atomic_mp_bra_basis.addItems(lst)
        self.main_atomic_mp_ket_basis.addItems(lst)
        self.main_atomic_mp_bra_basis.setCurrentIndex(0)
        self.main_atomic_mp_ket_basis.setCurrentIndex(0)

    # ==================================================
    def show_v_cluster(self):
        """
        show virtual cluster panel.
        """
        wp = self.main_v_cluster_wp.currentText()
        bond = self.main_v_cluster_bond.text()
        create_v_cluster(self._pgroup, wp, bond, self._qtdraw, self)

    # ==================================================
    def clear_data(self):
        """
        clear all data.
        """
        self._qtdraw._clear()
        self._qtdraw.set_crystal(self.main_c_type.currentText())

    # ==================================================
    def create_tab1_panel(self):
        """
        create tab1 panel.
        """
        self.tab1 = QWidget()
        self.tab.addTab(self.tab1, "object drawing")

        self.tab1_site_label = QLabel(
            "SITE: draw equivalent sites.\n 1. input representative SITE, + ENTER.",
            self,
        )
        self.tab1_site_pos = QLineEdit("[ 1/2, 1/2, 0 ]", self)

        self.tab1_bond_label = QLabel(
            "BOND: draw equivalent bonds.\n 1. input representative BOND, + ENTER.",
            self,
        )
        self.tab1_bond_pos = QLineEdit("[ 0, 0, 0 ] ; [ 1/2, 1/2, 0 ]", self)

        self.tab1_vector_label = QLabel(
            "VECTOR: draw vectors at equivalent sites or bonds.\n 1. choose type, 2. input vector [x,y,z] # representative SITE/BOND, + ENTER.",
            self,
        )
        self.tab1_vector_pos = QLineEdit("[ 0, 0, 1 ] # [ 1/2, 1/2, 0 ]", self)
        self.tab1_vector_type = QComboBox(self)
        self.tab1_vector_type.addItems(["Q", "G", "T", "M"])
        self.tab1_vector_type.setCurrentIndex(0)

        self.tab1_orbital_label = QLabel(
            "ORBITAL: draw orbitals at equivalent sites or bonds.\n 1. choose type, 2. input orbital (xyz polynomial) # representative SITE/BOND, + ENTER.",
            self,
        )
        self.tab1_orbital_pos = QLineEdit("3z**2 - r**2 # [ 1/4, 1/4, 0 ]", self)
        self.tab1_orbital_type = QComboBox(self)
        self.tab1_orbital_type.addItems(["Q", "G", "T", "M"])
        self.tab1_orbital_type.setCurrentIndex(0)

        self.tab1_pgharm_label = QLabel(
            "POINT-GROUP HARMONICS: draw point-group harmonics at equivalent sites or bonds.\n 1. choose (type,rank,irrep.), 2. input representative SITE/BOND, + ENTER.\n \u21d2  used expression is shown (in LaTeX form).",
            self,
        )
        self.tab1_pgharm_pos = QLineEdit("[ 0, 0, 0 ]", self)
        self.tab1_pgharm_type = QComboBox(self)
        self.tab1_pgharm_type.addItems(["Q", "G", "T", "M"])
        self.tab1_pgharm_type.setCurrentIndex(0)
        self.tab1_pgharm_rank = QComboBox(self)
        self.tab1_pgharm_rank.setFocusPolicy(Qt.NoFocus)
        self.tab1_pgharm_rank.addItems(map(str, range(12)))
        self.tab1_pgharm_rank.setCurrentIndex(0)
        self.tab1_pgharm_irrep = QComboBox(self)
        self.tab1_pgharm_irrep.setFocusPolicy(Qt.NoFocus)
        hs0 = self._pgroup.harmonics.select(rank=0, head="Q")
        self.tab1_pgharm_irrep.addItems(["Q" + str(i)[2:] for i in hs0])
        self.tab1_pgharm_irrep.setCurrentIndex(0)
        self.tab1_pgharm_exp_label = QLabel("expression", self)
        self.tab1_pgharm_exp = QLineEdit("1", self)
        self.tab1_pgharm_exp_latex = QCheckBox("LaTeX", self)
        self.tab1_pgharm_exp_latex.setChecked(False)
        self.tab1_wyckoff_label = QLabel(
            "WYCKOFF: find wyckoff position and local symmetry. 1. input representative SITE/BOND, + ENTER.\n \u21d2  wyckoff position and its local symmetry are shown.",
            self,
        )
        self.tab1_wyckoff_pos = QLineEdit("[ 0, 0, 0 ]", self)
        self.tab1_wyckoff_letter_label = QLabel(" \u21d2 Wyckoff position", self)
        self.tab1_wyckoff_letter = QLineEdit("", self)
        self.tab1_wyckoff_sym_label = QLabel("local symmetry", self)
        self.tab1_wyckoff_sym = QLineEdit("", self)

        self.tab1_v_spacer = QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding
        )

        self.tab1_grid = QGridLayout(self.tab1)
        self.tab1_grid.addWidget(self.tab1_site_label, 0, 0, 1, 9)
        self.tab1_grid.addWidget(self.tab1_site_pos, 1, 0, 1, 9)

        self.tab1_grid.addWidget(self.tab1_bond_label, 2, 0, 1, 9)
        self.tab1_grid.addWidget(self.tab1_bond_pos, 3, 0, 1, 9)

        self.tab1_grid.addWidget(self.tab1_vector_label, 4, 0, 1, 9)
        self.tab1_grid.addWidget(self.tab1_vector_type, 5, 0, 1, 1)
        self.tab1_grid.addWidget(self.tab1_vector_pos, 5, 1, 1, 8)

        self.tab1_grid.addWidget(self.tab1_orbital_label, 6, 0, 1, 9)
        self.tab1_grid.addWidget(self.tab1_orbital_type, 7, 0, 1, 1)
        self.tab1_grid.addWidget(self.tab1_orbital_pos, 7, 1, 1, 8)

        self.tab1_grid.addWidget(self.tab1_pgharm_label, 8, 0, 1, 9)
        self.tab1_grid.addWidget(self.tab1_pgharm_type, 9, 0, 1, 1)
        self.tab1_grid.addWidget(self.tab1_pgharm_rank, 9, 1, 1, 1)
        self.tab1_grid.addWidget(self.tab1_pgharm_irrep, 9, 2, 1, 2)
        self.tab1_grid.addWidget(self.tab1_pgharm_pos, 9, 4, 1, 5)
        self.tab1_grid.addWidget(self.tab1_pgharm_exp_label, 10, 0, 1, 1)
        self.tab1_grid.addWidget(self.tab1_pgharm_exp, 10, 1, 1, 7)
        self.tab1_grid.addWidget(self.tab1_pgharm_exp_latex, 10, 8, 1, 1)

        self.tab1_grid.addWidget(self.tab1_wyckoff_label, 11, 0, 1, 9)
        self.tab1_grid.addWidget(self.tab1_wyckoff_pos, 12, 0, 1, 4)
        self.tab1_grid.addWidget(self.tab1_wyckoff_letter_label, 12, 4, 1, 2)
        self.tab1_grid.addWidget(self.tab1_wyckoff_letter, 12, 6, 1, 1)
        self.tab1_grid.addWidget(self.tab1_wyckoff_sym_label, 12, 7, 1, 1)
        self.tab1_grid.addWidget(self.tab1_wyckoff_sym, 12, 8, 1, 1)

        self.tab1_grid.addItem(self.tab1_v_spacer, 13, 1, 1, 1)

        # connections.
        self.tab1_site_pos.returnPressed.connect(self.tab1_plot_site)
        self.tab1_bond_pos.returnPressed.connect(self.tab1_plot_bond)
        self.tab1_vector_pos.returnPressed.connect(self.tab1_plot_vector)
        self.tab1_orbital_pos.returnPressed.connect(self.tab1_plot_orbital)
        self.tab1_pgharm_type.currentIndexChanged.connect(self.tab1_pgharm_rank_select)
        self.tab1_pgharm_rank.currentIndexChanged.connect(self.tab1_pgharm_rank_select)
        self.tab1_pgharm_irrep.currentIndexChanged.connect(
            self.tab1_select_pg_harmonics
        )
        self.tab1_pgharm_type.currentIndexChanged.connect(self.tab1_select_pg_harmonics)
        self.tab1_pgharm_rank.currentIndexChanged.connect(self.tab1_select_pg_harmonics)
        self.tab1_pgharm_exp_latex.toggled.connect(self.tab1_select_pg_harmonics)
        self.tab1_pgharm_pos.returnPressed.connect(self.tab1_plot_pg_harmonics)
        self.tab1_wyckoff_pos.returnPressed.connect(self.tab1_find_wyckoff)

    # ==================================================
    def tab1_plot_site(self):
        """
        plot equivalent sites.
        """
        r_site = check_get_site(self.tab1_site_pos.text())
        if r_site is None:
            return

        if self.pg:
            site = self._group.site_mapping(r_site)
        else:
            site = self._group.site_mapping(r_site, plus_set=True)

        plot_equivalent_site(self._qtdraw, site, self.n_pset)

    # ==================================================
    def tab1_plot_bond(self):
        """
        plot equivalent bonds.
        """
        r_bond = check_get_bond(self.tab1_bond_pos.text())
        if r_bond is None:
            return

        if self.pg:
            bond, nondirectional = self._group.bond_mapping(r_bond)
        else:
            bond, nondirectional = self._group.bond_mapping(r_bond, plus_set=True)

        plot_equivalent_bond(self._qtdraw, bond, nondirectional, self.n_pset)

    # ==================================================
    def tab1_plot_vector(self):
        """
        plot vectors at equivalent sites/bonds.
        """
        head = self.tab1_vector_type.currentText()
        txt = self.tab1_vector_pos.text().split("#")
        if len(txt) != 2:
            return
        vector, r_site_bond = txt
        vector = check_get_site(vector)
        if vector is None:
            return
        r_site = check_get_site_bond(r_site_bond, ret_site=True)
        if r_site is None:
            return

        if self.pg:
            site = self._group.site_mapping(r_site)
        else:
            site = self._group.site_mapping(r_site, plus_set=True)
        site = NSArray.from_str(site.keys())

        plot_vector_equivalent_site(self._qtdraw, site, vector, head, self.n_pset)

    # ==================================================
    def tab1_plot_orbital(self):
        """
        plot orbitals at equivalent sites/bonds.
        """
        head = self.tab1_orbital_type.currentText()
        txt = self.tab1_orbital_pos.text().split("#")
        if len(txt) != 2:
            return
        orbital, r_site_bond = txt
        r_site = check_get_site_bond(r_site_bond, ret_site=True)
        if r_site is None:
            return

        if self.pg:
            site = self._group.site_mapping(r_site)
        else:
            site = self._group.site_mapping(r_site, plus_set=True)
        site = NSArray.from_str(site.keys())

        plot_orbital_equivalent_site(self._qtdraw, site, orbital, head, self.n_pset)

    # ==================================================
    def tab1_select_pg_harmonics(self):
        """
        select poing-group harmonics.
        """
        head = self.tab1_pgharm_type.currentText()
        head1 = head.replace("T", "Q").replace("M", "G")
        rank = int(self.tab1_pgharm_rank.currentText())
        hs = self._pgroup.harmonics.select(rank=rank, head=head1)
        h = hs[self.tab1_pgharm_irrep.currentIndex()]
        ex = h.expression(v=NSArray.vector3d("Q"))
        if self.tab1_pgharm_exp_latex.checkState():
            ex = ex.latex()
        self.tab1_pgharm_exp.setText(str(ex))

    # ==================================================
    def tab1_pgharm_rank_select(self):
        """
        select point-group harmonics rank.
        """
        head = self.tab1_pgharm_type.currentText()
        head1 = head.replace("T", "Q").replace("M", "G")
        rank = int(self.tab1_pgharm_rank.currentText())
        hs = self._pgroup.harmonics.select(rank=rank, head=head1)
        self.tab1_pgharm_irrep.clear()
        comb = [head + str(i)[2:] for i in hs]
        self.tab1_pgharm_irrep.addItems(comb)
        self.tab1_pgharm_irrep.setCurrentIndex(0)
        self.tab1_pgharm_exp.setText("1")

    # ==================================================
    def tab1_plot_pg_harmonics(self):
        """
        plot poing-group harmonics at equivalent sites/bonds.
        """
        head = self.tab1_pgharm_type.currentText()
        rank = int(self.tab1_pgharm_rank.currentText())
        harmonics_set = self._pgroup.harmonics.select(
            rank=rank, head=head.replace("T", "Q").replace("M", "G")
        )
        harmonics = harmonics_set[self.tab1_pgharm_irrep.currentIndex()]
        orbital = harmonics.expression(v=NSArray.vector3d("Q"))

        r_site = check_get_site_bond(self.tab1_pgharm_pos.text(), ret_site=True)
        if r_site is None:
            return

        if self.pg:
            site = self._group.site_mapping(r_site)
        else:
            site = self._group.site_mapping(r_site, plus_set=True)
        site = NSArray.from_str(site.keys())

        plot_orbital_equivalent_site(self._qtdraw, site, orbital, head, self.n_pset)

    # ==================================================
    def tab1_find_wyckoff(self):
        """
        find wyckoff position.
        """
        r_site_bond = self.tab1_wyckoff_pos.text()
        r_site = check_get_site_bond(r_site_bond, ret_site=True)
        if r_site is None:
            return

        wp = self._group.find_wyckoff_position(r_site)
        self.tab1_wyckoff_letter.setText(str(wp))
        sym = self._group.wyckoff.site_symmetry(wp)
        self.tab1_wyckoff_sym.setText(sym)

    # ==================================================
    def create_tab2_panel(self):
        """
        create tab2 panel.
        """
        self.tab2 = QWidget()
        self.tab.addTab(self.tab2, "basis drawing")

        self.tab2_site_proj_label = QLabel(
            "SITE: draw site-cluster basis.\n 1. input representative SITE, + ENTER,\n \u21d2  2. choose basis, 3. push `draw`.",
            self,
        )
        self.tab2_site_proj_pos = QLineEdit("[ 1/2, 1/2, 0 ]", self)
        self.tab2_site_proj_label1 = QLabel("\u21d2", self)
        self.tab2_site_proj_label1.setAlignment(Qt.AlignCenter)
        self.tab2_site_proj_irrep1 = QComboBox(self)
        self.tab2_site_proj_irrep1.addItems([""])
        self.tab2_site_proj_irrep1.setCurrentIndex(0)
        self.tab2_site_proj_draw_button = QPushButton("draw", self)
        self.tab2_site_proj_draw_button.setFocusPolicy(Qt.NoFocus)

        self.tab2_bond_proj_label = QLabel(
            "BOND: draw bond-cluster basis.\n 1. input representative BOND, + ENTER,\n \u21d2  2. choose basis, 3. push `draw`.",
            self,
        )
        self.tab2_bond_proj_pos = QLineEdit("[ 1/2, 1/2, 0 ] @ [ 1/4, 1/4, 0 ]", self)
        self.tab2_bond_proj_label1 = QLabel("\u21d2", self)
        self.tab2_bond_proj_label1.setAlignment(Qt.AlignCenter)
        self.tab2_bond_proj_irrep1 = QComboBox(self)
        self.tab2_bond_proj_irrep1.addItems([""])
        self.tab2_bond_proj_irrep1.setCurrentIndex(0)
        self.tab2_bond_proj_draw_button = QPushButton("draw", self)
        self.tab2_bond_proj_draw_button.setFocusPolicy(Qt.NoFocus)

        self.tab2_vector_proj_label = QLabel(
            "VECTOR: draw symmetry-adapted vector.\n 1. choose type, 2. input representative SITE/BOND, + ENTER,\n \u21d2  3. choose (type,basis), 4. push `draw` or 3. input linear combination (LC), + ENTER or 3. push `modulation`.",
            self,
        )
        self.tab2_vector_proj_pos = QLineEdit("[ 1/2, 1/2, 0 ]", self)
        self.tab2_vector_proj_type = QComboBox(self)
        self.tab2_vector_proj_type.addItems(["Q", "G", "T", "M"])
        self.tab2_vector_proj_type.setCurrentIndex(0)
        self.tab2_vector_proj_type1 = QComboBox(self)
        self.tab2_vector_proj_type1.addItems(["Q", "G", "T", "M"])
        self.tab2_vector_proj_type1.setCurrentIndex(0)
        self.tab2_vector_proj_label1 = QLabel("\u21d2", self)
        self.tab2_vector_proj_label1.setAlignment(Qt.AlignCenter)
        self.tab2_vector_proj_irrep1 = QComboBox(self)
        self.tab2_vector_proj_irrep1.addItems([""])
        self.tab2_vector_proj_irrep1.setCurrentIndex(0)
        self.tab2_vector_proj_draw_button = QPushButton("draw", self)
        self.tab2_vector_proj_draw_button.setFocusPolicy(Qt.NoFocus)
        self.tab2_vector_proj_lc_label = QLabel("LC", self)
        self.tab2_vector_proj_lc_label.setAlignment(Qt.AlignCenter)
        self.tab2_vector_proj_lc = QLineEdit("(Q01+Q02)/sqrt(2)", self)
        self.tab2_vector_modulation_button = QPushButton("modulation", self)
        self.tab2_vector_modulation_button.setFocusPolicy(Qt.NoFocus)
        self.tab2_vector_modulation_type = QComboBox(self)
        self.tab2_vector_modulation_type.addItems(["Q,G", "T,M"])
        self.tab2_vector_modulation_type.setCurrentIndex(0)
        self.tab2_vector_modulation_list = QLineEdit("", self)

        self.tab2_orbital_proj_label = QLabel(
            "ORBITAL draw symmetry-adapted orbital.\n 1. choose (type,rank), 2. input representative SITE/BOND, + ENTER,\n \u21d2  3. choose (type,basis), 4. push `draw` or 3. input linear combination (LC), + ENTER or 3. push `modulation`.",
            self,
        )
        self.tab2_orbital_proj_pos = QLineEdit("[ 0, 0, 0 ]; [ 1/2, 1/2, 0 ]", self)
        self.tab2_orbital_proj_type = QComboBox(self)
        self.tab2_orbital_proj_type.addItems(["Q", "G", "T", "M"])
        self.tab2_orbital_proj_type.setCurrentIndex(0)
        self.tab2_orbital_proj_type1 = QComboBox(self)
        self.tab2_orbital_proj_type1.addItems(["Q", "G", "T", "M"])
        self.tab2_orbital_proj_type1.setCurrentIndex(0)
        self.tab2_orbital_proj_label1 = QLabel("\u21d2", self)
        self.tab2_orbital_proj_label1.setAlignment(Qt.AlignCenter)
        self.tab2_orbital_proj_irrep1 = QComboBox(self)
        self.tab2_orbital_proj_irrep1.addItems([""])
        self.tab2_orbital_proj_irrep1.setCurrentIndex(0)
        self.tab2_orbital_proj_rank = QComboBox(self)
        self.tab2_orbital_proj_rank.setFocusPolicy(Qt.NoFocus)
        self.tab2_orbital_proj_rank.addItems(map(str, range(12)))
        self.tab2_orbital_proj_rank.setCurrentIndex(1)
        self.tab2_orbital_proj_draw_button = QPushButton("draw", self)
        self.tab2_orbital_proj_draw_button.setFocusPolicy(Qt.NoFocus)
        self.tab2_orbital_proj_lc_label = QLabel("LC", self)
        self.tab2_orbital_proj_lc_label.setAlignment(Qt.AlignCenter)
        self.tab2_orbital_proj_lc = QLineEdit("(Q01+Q02)/sqrt(2)", self)
        self.tab2_orbital_modulation_button = QPushButton("modulation", self)
        self.tab2_orbital_modulation_button.setFocusPolicy(Qt.NoFocus)
        self.tab2_orbital_modulation_type = QComboBox(self)
        self.tab2_orbital_modulation_type.addItems(["Q,G", "T,M"])
        self.tab2_orbital_modulation_type.setCurrentIndex(0)
        self.tab2_orbital_modulation_list = QLineEdit("", self)

        self.tab2_hopping_proj_label = QLabel(
            "HOPPING: draw hopping direction.\n 1. input representative BOND, + ENTER.",
            self,
        )
        self.tab2_hopping_proj_pos = QLineEdit("[ 0, 0, 0 ] ; [ 1/2, 1/2, 0 ]", self)

        self.tab2_vspacer = QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding
        )

        self.tab2_grid = QGridLayout(self.tab2)

        self.tab2_grid.addWidget(self.tab2_site_proj_label, 0, 0, 1, 9)
        self.tab2_grid.addWidget(self.tab2_site_proj_pos, 1, 0, 1, 9)
        self.tab2_grid.addWidget(self.tab2_site_proj_label1, 2, 0, 1, 1)
        self.tab2_grid.addWidget(self.tab2_site_proj_irrep1, 2, 1, 1, 7)
        self.tab2_grid.addWidget(self.tab2_site_proj_draw_button, 2, 8, 1, 1)

        self.tab2_grid.addWidget(self.tab2_bond_proj_label, 3, 0, 1, 9)
        self.tab2_grid.addWidget(self.tab2_bond_proj_pos, 4, 0, 1, 9)
        self.tab2_grid.addWidget(self.tab2_bond_proj_label1, 5, 0, 1, 1)
        self.tab2_grid.addWidget(self.tab2_bond_proj_irrep1, 5, 1, 1, 7)
        self.tab2_grid.addWidget(self.tab2_bond_proj_draw_button, 5, 8, 1, 1)

        self.tab2_grid.addWidget(self.tab2_vector_proj_label, 6, 0, 1, 9)
        self.tab2_grid.addWidget(self.tab2_vector_proj_type, 7, 0, 1, 1)
        self.tab2_grid.addWidget(self.tab2_vector_proj_pos, 7, 1, 1, 8)
        self.tab2_grid.addWidget(self.tab2_vector_proj_label1, 8, 0, 1, 1)
        self.tab2_grid.addWidget(self.tab2_vector_proj_type1, 8, 1, 1, 1)
        self.tab2_grid.addWidget(self.tab2_vector_proj_irrep1, 8, 2, 1, 6)
        self.tab2_grid.addWidget(self.tab2_vector_proj_draw_button, 8, 8, 1, 1)
        self.tab2_grid.addWidget(self.tab2_vector_proj_lc_label, 9, 0, 1, 1)
        self.tab2_grid.addWidget(self.tab2_vector_proj_lc, 9, 1, 1, 8)
        self.tab2_grid.addWidget(self.tab2_vector_modulation_button, 10, 0, 1, 2)
        self.tab2_grid.addWidget(self.tab2_vector_modulation_type, 10, 2, 1, 1)
        self.tab2_grid.addWidget(self.tab2_vector_modulation_list, 10, 3, 1, 6)

        self.tab2_grid.addWidget(self.tab2_orbital_proj_label, 11, 0, 1, 9)
        self.tab2_grid.addWidget(self.tab2_orbital_proj_type, 12, 0, 1, 1)
        self.tab2_grid.addWidget(self.tab2_orbital_proj_rank, 12, 1, 1, 1)
        self.tab2_grid.addWidget(self.tab2_orbital_proj_pos, 12, 2, 1, 7)
        self.tab2_grid.addWidget(self.tab2_orbital_proj_label1, 13, 0, 1, 1)
        self.tab2_grid.addWidget(self.tab2_orbital_proj_type1, 13, 1, 1, 1)
        self.tab2_grid.addWidget(self.tab2_orbital_proj_irrep1, 13, 2, 1, 6)
        self.tab2_grid.addWidget(self.tab2_orbital_proj_draw_button, 13, 8, 1, 1)
        self.tab2_grid.addWidget(self.tab2_orbital_proj_lc_label, 14, 0, 1, 1)
        self.tab2_grid.addWidget(self.tab2_orbital_proj_lc, 14, 1, 1, 8)
        self.tab2_grid.addWidget(self.tab2_orbital_modulation_button, 15, 0, 1, 2)
        self.tab2_grid.addWidget(self.tab2_orbital_modulation_type, 15, 2, 1, 1)
        self.tab2_grid.addWidget(self.tab2_orbital_modulation_list, 15, 3, 1, 6)

        self.tab2_grid.addWidget(self.tab2_hopping_proj_label, 16, 0, 1, 9)
        self.tab2_grid.addWidget(self.tab2_hopping_proj_pos, 17, 0, 1, 9)

        self.tab2_grid.addItem(self.tab2_vspacer, 18, 1, 1, 1)

        # connections.
        self.tab2_site_proj_pos.returnPressed.connect(self.tab2_gen_site_cluster)
        self.tab2_site_proj_draw_button.clicked.connect(
            self.tab2_plot_site_cluster_samb
        )
        self.tab2_bond_proj_pos.returnPressed.connect(self.tab2_gen_bond_cluster)
        self.tab2_bond_proj_draw_button.clicked.connect(
            self.tab2_plot_bond_cluster_samb
        )
        self.tab2_vector_proj_pos.returnPressed.connect(self.tab2_gen_z_samb_vector)
        self.tab2_vector_proj_type1.currentIndexChanged.connect(
            self.tab2_select_z_samb_vector
        )
        self.tab2_vector_proj_draw_button.clicked.connect(self.tab2_plot_z_samb_vector)
        self.tab2_vector_proj_lc.returnPressed.connect(self.tab2_plot_z_samb_vector_lc)
        self.tab2_vector_modulation_button.clicked.connect(
            self.tab2_create_modulated_vector
        )
        self.tab2_orbital_proj_pos.returnPressed.connect(self.tab2_gen_z_samb_orbital)
        self.tab2_orbital_proj_type1.currentIndexChanged.connect(
            self.tab2_select_z_samb_orbital
        )
        self.tab2_orbital_proj_draw_button.clicked.connect(
            self.tab2_plot_z_samb_orbital
        )
        self.tab2_orbital_proj_lc.returnPressed.connect(
            self.tab2_plot_z_samb_orbital_lc
        )
        self.tab2_orbital_modulation_button.clicked.connect(
            self.tab2_create_modulated_orbital
        )
        self.tab2_hopping_proj_pos.returnPressed.connect(self.tab2_plot_z_samb_hopping)

        self.tab2_modulated_vector_active = False
        self.tab2_modulated_orbital_active = False

    # ==================================================
    def tab2_gen_site_cluster(self):
        """
        generate site cluster SAMB.
        """
        pos = check_get_site(self.tab2_site_proj_pos.text())
        if pos is None:
            return

        combined_info = create_combined(self._group, self._pgroup, pos, 0, "Q")

        (
            self.tab2_site_proj_c_samb,
            self.tab2_site_proj_site,
            self.tab2_site_proj_z_samb,
        ) = combined_info

        self.tab2_site_cluster_samb_select()

    # ==================================================
    def tab2_site_cluster_samb_select(self):
        """
        create site cluster SAMB select list.
        """
        self.tab2_site_proj_comb_select = self.tab2_site_proj_z_samb["Q"]
        self.tab2_site_proj_irrep1.clear()
        comb = [
            f"{i[0][0]}{no+1:02d}: {i[0]}"
            for no, i in enumerate(self.tab2_site_proj_comb_select)
        ]
        self.tab2_site_proj_irrep1.addItems(comb)
        self.tab2_site_proj_irrep1.setCurrentIndex(0)

    # ==================================================
    def tab2_plot_site_cluster_samb(self):
        """
        plot site cluster SAMB.
        """
        if not hasattr(self, "tab2_site_proj_z_samb"):
            return
        irrep = self.tab2_site_proj_irrep1.currentIndex()

        v = NSArray.vector3d()
        cluster_obj = create_samb_object(
            self.tab2_site_proj_z_samb,
            self.tab2_site_proj_site,
            self.tab2_site_proj_c_samb,
            "Q",
            irrep,
            self._pgroup,
            v,
            False,
        )

        label = (
            self.tab2_site_proj_irrep1.currentText()[:3]
            + " \u21d0 "
            + remove_space(self.tab2_site_proj_pos.text())
        )
        plot_site_cluster(
            self._qtdraw,
            self.tab2_site_proj_site,
            cluster_obj,
            label,
            self.pset,
            self.pg,
        )

    # ==================================================
    def tab2_gen_bond_cluster(self):
        """
        generate bond cluster SAMB.
        """
        pos = check_get_bond(self.tab2_bond_proj_pos.text())
        if pos is None:
            return

        combined_info = create_combined(
            self._group, self._pgroup, pos, 0, "Q", ret_bond=True
        )

        (
            self.tab2_bond_proj_c_samb,
            self.tab2_bond_proj_site,
            self.tab2_bond_proj_z_samb,
        ) = combined_info

        self.tab2_bond_cluster_samb_select()

    # ==================================================
    def tab2_bond_cluster_samb_select(self):
        """
        create bond cluster SAMB select list.
        """
        self.tab2_bond_proj_comb_select = (
            self.tab2_bond_proj_z_samb["Q"] + self.tab2_bond_proj_z_samb["T"]
        )
        qn = len(self.tab2_bond_proj_z_samb["Q"])
        self.tab2_bond_proj_irrep1.clear()
        comb = [
            f"Q{no+1:02d}: {i[0]}" if i[0][0] == "Q" else f"T{no+1-qn:02d}: {i[0]}"
            for no, i in enumerate(self.tab2_bond_proj_comb_select)
        ]
        self.tab2_bond_proj_irrep1.addItems(comb)
        self.tab2_bond_proj_irrep1.setCurrentIndex(0)

    # ==================================================
    def tab2_plot_bond_cluster_samb(self):
        """
        plot bond cluster SAMB.
        """
        if not hasattr(self, "tab2_bond_proj_z_samb"):
            return
        irrep = self.tab2_bond_proj_irrep1.currentIndex()
        z_head = self.tab2_bond_proj_irrep1.currentText()[0]
        if z_head == "T":
            irrep -= len(self.tab2_bond_proj_z_samb["Q"])
        t_odd = z_head != "Q"

        v = NSArray.vector3d()
        cluster_obj = create_samb_object(
            self.tab2_bond_proj_z_samb,
            self.tab2_bond_proj_site,
            self.tab2_bond_proj_c_samb,
            z_head,
            irrep,
            self._pgroup,
            v,
            t_odd,
        )

        label = (
            self.tab2_bond_proj_irrep1.currentText()[:3]
            + " \u21d0 "
            + remove_space(self.tab2_bond_proj_pos.text())
        )
        plot_bond_cluster(
            self._qtdraw,
            self.tab2_bond_proj_site,
            cluster_obj,
            label,
            self.pset,
            z_head,
            self.pg,
        )

    # ==================================================
    def tab2_gen_z_samb_vector(self):
        """
        generate vector cluster SAMB for given site/bond.
        """
        pos = check_get_site_bond(self.tab2_vector_proj_pos.text())
        if pos is None:
            return

        combined_info = create_combined(
            self._group, self._pgroup, pos, 1, self.tab2_vector_proj_type.currentText()
        )

        (
            self.tab2_vector_proj_c_samb,
            self.tab2_vector_proj_site,
            self.tab2_vector_proj_z_samb,
        ) = combined_info

        self.tab2_select_z_samb_vector()

    # ==================================================
    def tab2_select_z_samb_vector(self):
        """
        create vector cluster SAMB select list.
        """
        self.tab2_vector_proj_comb_select = self.tab2_vector_proj_z_samb[
            self.tab2_vector_proj_type1.currentText()
        ]
        self.tab2_vector_proj_irrep1.clear()
        comb = [
            f"{i[0][0]}{no+1:02d}: {i[0]}"
            for no, i in enumerate(self.tab2_vector_proj_comb_select)
        ]
        self.tab2_vector_proj_irrep1.addItems(comb)
        self.tab2_vector_proj_irrep1.setCurrentIndex(0)

    # ==================================================
    def tab2_plot_z_samb_vector(self):
        """
        plot vector SAMB.
        """
        if not hasattr(self, "tab2_vector_proj_z_samb"):
            return
        z_head = self.tab2_vector_proj_type1.currentText()
        head = self.tab2_vector_proj_type.currentText()
        irrep = self.tab2_vector_proj_irrep1.currentIndex()
        t_odd = head.replace("M", "T").replace("G", "Q") != z_head.replace(
            "M", "T"
        ).replace("G", "Q")

        v = NSArray.vector3d()
        cluster_obj = create_samb_object(
            self.tab2_vector_proj_z_samb,
            self.tab2_vector_proj_site,
            self.tab2_vector_proj_c_samb,
            z_head,
            irrep,
            self._pgroup,
            v,
            t_odd,
        )

        label = (
            self.tab2_vector_proj_irrep1.currentText()[:3]
            + " \u21d0 "
            + head
            + ", "
            + remove_space(self.tab2_vector_proj_pos.text())
        )
        plot_vector_cluster(
            self._qtdraw,
            self.tab2_vector_proj_site,
            cluster_obj,
            label,
            self.pset,
            head,
            v,
            self.pg,
        )

    # ==================================================
    def tab2_plot_z_samb_vector_lc(self):
        """
        plot linear combination of vector SAMB.
        """
        if not hasattr(self, "tab2_vector_proj_z_samb"):
            return
        head = self.tab2_vector_proj_type.currentText()
        form, ex_var, t_odd = check_linear_combination(
            self.tab2_vector_proj_z_samb, self.tab2_vector_proj_lc.text(), head
        )
        if form is None:
            return

        v = NSArray.vector3d()
        lc_basis = {
            i: sp.Matrix(
                create_samb_object(
                    self.tab2_vector_proj_z_samb,
                    self.tab2_vector_proj_site,
                    self.tab2_vector_proj_c_samb,
                    i[0].upper(),
                    int(i[1:]) - 1,
                    self._pgroup,
                    v,
                    t_odd,
                ).tolist()
            )
            for i in ex_var
        }
        cluster_obj = NSArray(str(NSArray(form).subs(lc_basis).tolist().T.tolist()[0]))

        label = (
            remove_space(self.tab2_vector_proj_lc.text())
            + " \u21d0 "
            + head
            + ", "
            + remove_space(self.tab2_vector_proj_pos.text())
        )

        plot_vector_cluster(
            self._qtdraw,
            self.tab2_vector_proj_site,
            cluster_obj,
            label,
            self.pset,
            head,
            v,
            self.pg,
        )

    # ==================================================
    def tab2_create_modulated_vector(self):
        """
        create modulated vector.
        """
        if not hasattr(self, "tab2_vector_proj_z_samb"):
            return
        if self.tab2_vector_modulation_type.currentIndex() == 0:
            basis = [
                f"Q{i+1:02d}" for i in range(len(self.tab2_vector_proj_z_samb["Q"]))
            ] + [f"G{i+1:02d}" for i in range(len(self.tab2_vector_proj_z_samb["G"]))]
        else:
            basis = [
                f"T{i+1:02d}" for i in range(len(self.tab2_vector_proj_z_samb["T"]))
            ] + [f"M{i+1:02d}" for i in range(len(self.tab2_vector_proj_z_samb["M"]))]
        if len(basis) < 1:
            return

        head = self.tab2_vector_proj_type.currentText()
        modulation = self.tab2_vector_modulation_list.text()

        if not self.tab2_modulated_vector_active:
            self.tab2_modulated_vector_active = True
            self.dialog_modulation_vector = DialogModulation(
                basis, modulation, head, False, self
            )
            self.dialog_modulation_vector.show()

    # ==================================================
    def tab2_gen_z_samb_orbital(self):
        """
        generate orbital cluster SAMB for given site/bond.
        """
        pos = check_get_site_bond(self.tab2_orbital_proj_pos.text())
        if pos is None:
            return

        combined_info = create_combined(
            self._group,
            self._pgroup,
            pos,
            self.tab2_orbital_proj_rank.currentText(),
            self.tab2_orbital_proj_type.currentText(),
        )

        (
            self.tab2_orbital_proj_c_samb,
            self.tab2_orbital_proj_site,
            self.tab2_orbital_proj_z_samb,
        ) = combined_info

        self.tab2_select_z_samb_orbital()

    # ==================================================
    def tab2_select_z_samb_orbital(self):
        """
        create orbital cluster SAMB select list.
        """
        self.tab2_orbital_proj_comb_select = self.tab2_orbital_proj_z_samb[
            self.tab2_orbital_proj_type1.currentText()
        ]
        self.tab2_orbital_proj_irrep1.clear()
        comb = [
            f"{i[0][0]}{no+1:02d}: {i[0]}"
            for no, i in enumerate(self.tab2_orbital_proj_comb_select)
        ]
        self.tab2_orbital_proj_irrep1.addItems(comb)
        self.tab2_orbital_proj_irrep1.setCurrentIndex(0)

    # ==================================================
    def tab2_plot_z_samb_orbital(self):
        """
        plot orbital SAMB.
        """
        if not hasattr(self, "tab2_orbital_proj_z_samb"):
            return
        z_head = self.tab2_orbital_proj_type1.currentText()
        head = self.tab2_orbital_proj_type.currentText()
        irrep = self.tab2_orbital_proj_irrep1.currentIndex()
        t_odd = head.replace("M", "T").replace("G", "Q") != z_head.replace(
            "M", "T"
        ).replace("G", "Q")

        v = NSArray.vector3d()
        cluster_obj = create_samb_object(
            self.tab2_orbital_proj_z_samb,
            self.tab2_orbital_proj_site,
            self.tab2_orbital_proj_c_samb,
            z_head,
            irrep,
            self._pgroup,
            v,
            t_odd,
        )

        label = (
            self.tab2_orbital_proj_irrep1.currentText()[:3]
            + " \u21d0 "
            + head
            + self.tab2_orbital_proj_rank.currentText()
            + ", "
            + remove_space(self.tab2_orbital_proj_pos.text())
        )
        plot_orbital_cluster(
            self._qtdraw,
            self.tab2_orbital_proj_site,
            cluster_obj,
            label,
            self.pset,
            head,
            self.pg,
        )

    # ==================================================
    def tab2_plot_z_samb_orbital_lc(self):
        """
        plot linear combination of orbital SAMB.
        """
        if not hasattr(self, "tab2_orbital_proj_z_samb"):
            return
        head = self.tab2_orbital_proj_type.currentText()
        form, ex_var, t_odd = check_linear_combination(
            self.tab2_orbital_proj_z_samb, self.tab2_orbital_proj_lc.text(), head
        )
        if form is None:
            return

        v = NSArray.vector3d()
        lc_basis = {
            i: sp.Matrix(
                create_samb_object(
                    self.tab2_orbital_proj_z_samb,
                    self.tab2_orbital_proj_site,
                    self.tab2_orbital_proj_c_samb,
                    i[0].upper(),
                    int(i[1:]) - 1,
                    self._pgroup,
                    v,
                    t_odd,
                ).tolist()
            )
            for i in ex_var
        }
        cluster_obj = NSArray(str(NSArray(form).subs(lc_basis).tolist().T.tolist()[0]))

        label = (
            remove_space(self.tab2_orbital_proj_lc.text())
            + " \u21d0 "
            + head
            + self.tab2_orbital_proj_rank.currentText()
            + ", "
            + remove_space(self.tab2_orbital_proj_pos.text())
        )
        plot_orbital_cluster(
            self._qtdraw,
            self.tab2_orbital_proj_site,
            cluster_obj,
            label,
            self.pset,
            head,
            self.pg,
        )

    # ==================================================
    def tab2_create_modulated_orbital(self):
        """
        create modulated orbital.
        """
        if not hasattr(self, "tab2_orbital_proj_z_samb"):
            return
        if self.tab2_orbital_modulation_type.currentIndex() == 0:
            basis = [
                f"Q{i+1:02d}" for i in range(len(self.tab2_orbital_proj_z_samb["Q"]))
            ] + [f"G{i+1:02d}" for i in range(len(self.tab2_orbital_proj_z_samb["G"]))]
        else:
            basis = [
                f"T{i+1:02d}" for i in range(len(self.tab2_orbital_proj_z_samb["T"]))
            ] + [f"M{i+1:02d}" for i in range(len(self.tab2_orbital_proj_z_samb["M"]))]
        if len(basis) < 1:
            return

        head = self.tab2_orbital_proj_type.currentText()
        modulation = self.tab2_orbital_modulation_list.text()

        if not self.tab2_modulated_orbital_active:
            self.tab2_modulated_orbital_active = True
            self.dialog_modulation_orbital = DialogModulation(
                basis, modulation, head, True, self
            )
            self.dialog_modulation_orbital.show()

    # ==================================================
    def tab2_plot_z_samb_hopping(self):
        """
        plot hopping direction.
        """
        pos = check_get_bond(self.tab2_hopping_proj_pos.text())
        if pos is None:
            return

        head = "T"
        combined_info = create_combined(self._group, self._pgroup, pos, 1, head)

        c_samb, site, z_samb = combined_info

        v = NSArray.vector3d()
        cluster_obj = create_samb_object(
            z_samb, site, c_samb, "Q", 0, self._pgroup, v, True
        )

        label = "t_dir \u21d0 " + remove_space(self.tab2_hopping_proj_pos.text())
        plot_vector_cluster(
            self._qtdraw, site, cluster_obj, label, self.pset, head, v, self.pg
        )

    # ==================================================
    def save_dict(self):
        """
        create qtdraw dict (MultiPie part).

        Returns:
            dict: qtdraw-multipie dict.
        """
        dic = {
            "version": self._qtdraw._multipie_loaded,
            "main": {
                "group": (
                    self.main_g_type.currentIndex(),
                    self.main_c_type.currentIndex(),
                    self.main_group.currentIndex(),
                )
            },
            "tab1": {
                "site": (self.tab1_site_pos.text(),),
                "bond": (self.tab1_bond_pos.text(),),
                "vector": (
                    self.tab1_vector_pos.text(),
                    self.tab1_vector_type.currentIndex(),
                ),
                "orbital": (
                    self.tab1_orbital_pos.text(),
                    self.tab1_orbital_type.currentIndex(),
                ),
                "harmonics": (
                    self.tab1_pgharm_pos.text(),
                    self.tab1_pgharm_type.currentIndex(),
                    self.tab1_pgharm_rank.currentIndex(),
                    self.tab1_pgharm_irrep.currentIndex(),
                ),
                "wyckoff": (
                    self.tab1_wyckoff_pos.text(),
                    self.tab1_wyckoff_letter.text(),
                    self.tab1_wyckoff_sym.text(),
                ),
            },
            "tab2": {
                "site": (
                    self.tab2_site_proj_pos.text(),
                    self.tab2_site_proj_irrep1.currentIndex(),
                ),
                "bond": (
                    self.tab2_bond_proj_pos.text(),
                    self.tab2_bond_proj_irrep1.currentIndex(),
                ),
                "vector": (
                    self.tab2_vector_proj_pos.text(),
                    self.tab2_vector_proj_type.currentIndex(),
                    self.tab2_vector_proj_type1.currentIndex(),
                    self.tab2_vector_proj_irrep1.currentIndex(),
                    self.tab2_vector_proj_lc.text(),
                    self.tab2_vector_modulation_type.currentIndex(),
                    self.tab2_vector_modulation_list.text(),
                ),
                "orbital": (
                    self.tab2_orbital_proj_pos.text(),
                    self.tab2_orbital_proj_type.currentIndex(),
                    self.tab2_orbital_proj_rank.currentIndex(),
                    self.tab2_orbital_proj_type1.currentIndex(),
                    self.tab2_orbital_proj_irrep1.currentIndex(),
                    self.tab2_orbital_proj_lc.text(),
                    self.tab2_orbital_modulation_type.currentIndex(),
                    self.tab2_orbital_modulation_list.text(),
                ),
                "hopping": (self.tab2_hopping_proj_pos.text(),),
            },
        }

        return dic

    # ==================================================
    def load_dict(self, dic):
        """
        load dict and set.

        Args:
            dic (dict): loaded qtdraw dict.
        """
        group_type, crystal_type, group = dic["main"]["group"]
        self.main_g_type.setCurrentIndex(group_type)
        self.main_c_type.setCurrentIndex(crystal_type)
        self.main_group.setCurrentIndex(group)

        t1_site_pos = dic["tab1"]["site"][0]
        self.tab1_site_pos.setText(t1_site_pos)
        t1_bond_pos = dic["tab1"]["bond"][0]
        self.tab1_bond_pos.setText(t1_bond_pos)
        t1_vector_pos, t1_vector_type = dic["tab1"]["vector"]
        self.tab1_vector_pos.setText(t1_vector_pos)
        self.tab1_vector_type.setCurrentIndex(t1_vector_type)
        t1_orbital_pos, t1_orbital_type = dic["tab1"]["orbital"]
        self.tab1_orbital_pos.setText(t1_orbital_pos)
        self.tab1_orbital_type.setCurrentIndex(t1_orbital_type)
        (
            t1_harmonics_pos,
            t1_harmonics_type,
            t1_harmonics_rank,
            t1_harmonics_irrep,
        ) = dic["tab1"]["harmonics"]
        self.tab1_pgharm_pos.setText(t1_harmonics_pos)
        self.tab1_pgharm_type.setCurrentIndex(t1_harmonics_type)
        self.tab1_pgharm_rank.setCurrentIndex(t1_harmonics_rank)
        self.tab1_pgharm_irrep.setCurrentIndex(t1_harmonics_irrep)
        t1_wyckoff_pos, t1_wyckoff_letter, t1_wyckoff_sym = dic["tab1"]["wyckoff"]
        self.tab1_wyckoff_pos.setText(t1_wyckoff_pos)
        self.tab1_wyckoff_letter.setText(t1_wyckoff_letter)
        self.tab1_wyckoff_sym.setText(t1_wyckoff_sym)

        t2_site_pos, t2_site_irrep1 = dic["tab2"]["site"]
        self.tab2_site_proj_pos.setText(t2_site_pos)
        self.tab2_site_proj_pos.returnPressed.emit()
        self.tab2_site_proj_irrep1.setCurrentIndex(t2_site_irrep1)
        t2_bond_pos, t2_bond_irrep1 = dic["tab2"]["bond"]
        self.tab2_bond_proj_pos.setText(t2_bond_pos)
        self.tab2_bond_proj_pos.returnPressed.emit()
        self.tab2_bond_proj_irrep1.setCurrentIndex(t2_bond_irrep1)
        (
            t2_vector_pos,
            t2_vector_type,
            t2_vector_type1,
            t2_vector_irrep1,
            t2_vector_lc,
            t2_vector_mod_type,
            t2_vector_mod_list,
        ) = dic["tab2"]["vector"]
        self.tab2_vector_proj_pos.setText(t2_vector_pos)
        self.tab2_vector_proj_type.setCurrentIndex(t2_vector_type)
        self.tab2_vector_proj_pos.returnPressed.emit()
        self.tab2_vector_proj_type1.setCurrentIndex(t2_vector_type1)
        self.tab2_vector_proj_irrep1.setCurrentIndex(t2_vector_irrep1)
        self.tab2_vector_proj_lc.setText(t2_vector_lc)
        self.tab2_vector_modulation_type.setCurrentIndex(t2_vector_mod_type)
        self.tab2_vector_modulation_list.setText(t2_vector_mod_list)
        (
            t2_orbital_pos,
            t2_orbital_type,
            t2_orbital_rank,
            t2_orbital_type1,
            t2_orbital_irrep1,
            t2_orbital_lc,
            t2_orbital_mod_type,
            t2_orbital_mod_list,
        ) = dic["tab2"]["orbital"]
        self.tab2_orbital_proj_pos.setText(t2_orbital_pos)
        self.tab2_orbital_proj_type.setCurrentIndex(t2_orbital_type)
        self.tab2_orbital_proj_rank.setCurrentIndex(t2_orbital_rank)
        self.tab2_orbital_proj_pos.returnPressed.emit()
        self.tab2_orbital_proj_type1.setCurrentIndex(t2_orbital_type1)
        self.tab2_orbital_proj_irrep1.setCurrentIndex(t2_orbital_irrep1)
        self.tab2_orbital_proj_lc.setText(t2_orbital_lc)
        self.tab2_orbital_modulation_type.setCurrentIndex(t2_orbital_mod_type)
        self.tab2_orbital_modulation_list.setText(t2_orbital_mod_list)
        t2_hopping_pos = dic["tab2"]["hopping"][0]
        self.tab2_hopping_proj_pos.setText(t2_hopping_pos)
