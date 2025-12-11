from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from qtdraw.widget.custom_widget import Label, Layout, Button, Combo, VSpacer, HSpacer, HBar, LineEdit


# ==================================================
class TabGroup(QWidget):
    # ==================================================
    def __init__(self, parent):
        super().__init__(parent)

        layout = Layout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setHorizontalSpacing(30)
        layout.setVerticalSpacing(10)

        # widget.
        label_decomp = Label(parent, text="Irrep. Decomposition", bold=True)
        label_symmetric = Label(parent, text="symmetric")
        label_antisymmetric = Label(parent, text="anti-symmetric")
        self.group_combo_irrep1 = Combo(parent)
        self.group_combo_irrep2 = Combo(parent)
        label_decomp_disp = Label(parent, text="decomposition")
        self.group_label_symmetric_decomp = Label(parent)
        self.group_combo_irrep = Combo(parent)
        self.group_label_antisymmetric_decomp = Label(parent)

        panel12 = QWidget(parent)
        layout12 = Layout(panel12)
        layout12.addWidget(label_decomp, 0, 0, 1, 1)
        layout12.addWidget(label_decomp_disp, 0, 1, 1, 1, Qt.AlignRight)

        panel3 = QWidget(parent)
        layout3 = Layout(panel3)
        layout3.addWidget(label_symmetric, 0, 0, 1, 1, Qt.AlignRight)
        layout3.addWidget(self.group_combo_irrep1, 0, 1, 1, 1)
        layout3.addWidget(self.group_combo_irrep2, 0, 2, 1, 1)
        layout3.addWidget(self.group_label_symmetric_decomp, 0, 3, 1, 1)
        layout3.addWidget(label_antisymmetric, 1, 0, 1, 1, Qt.AlignRight)
        layout3.addWidget(self.group_combo_irrep, 1, 1, 1, 1)
        layout3.addWidget(self.group_label_antisymmetric_decomp, 1, 3, 1, 1)

        label_harmonics = Label(parent, text="Harmonics", bold=True)
        self.group_button_harmonics = Button(parent, text="show")
        label_harmonics_type = Label(parent, text="type")
        self.group_combo_harmonics_type = Combo(parent, ["Q", "G", "T", "M"])
        label_harmonics_rank = Label(parent, text="rank")
        self.group_combo_harmonics_rank = Combo(parent, map(str, range(12)))

        label_harmonics_decomp = Label(parent, text="target PG")
        point_group_all_list = []
        self.group_combo_harmonics_decomp = Combo(parent, point_group_all_list)
        self.group_button_harmonics_decomp = Button(parent, text="decompose")

        panel5 = QWidget(parent)
        layout5 = Layout(panel5)
        layout5.addWidget(label_harmonics, 0, 0, 1, 1)
        layout5.addWidget(self.group_button_harmonics, 0, 1, 1, 1, Qt.AlignRight)

        panel4 = QWidget(parent)
        layout4 = Layout(panel4)
        layout4.addWidget(label_harmonics_type, 0, 0, 1, 1, Qt.AlignRight)
        layout4.addWidget(self.group_combo_harmonics_type, 0, 1, 1, 1)
        layout4.addWidget(label_harmonics_rank, 0, 2, 1, 1, Qt.AlignRight)
        layout4.addWidget(self.group_combo_harmonics_rank, 0, 3, 1, 1)
        layout4.addWidget(label_harmonics_decomp, 1, 0, 1, 1, Qt.AlignRight)
        layout4.addWidget(self.group_combo_harmonics_decomp, 1, 1, 1, 1)
        layout4.addWidget(self.group_button_harmonics_decomp, 1, 2, 1, 2)

        label_response = Label(parent, text="Response Tensor", bold=True)
        self.group_button_response = Button(parent, text="show")
        self.group_combo_response_type = Combo(parent, ["Q", "G", "T", "M"])
        label_response_type = Label(parent, text="type")
        label_response_rank = Label(parent, text="rank")
        self.group_combo_response_rank = Combo(parent, map(str, range(1, 5)))

        panel11 = QWidget(parent)
        layout11 = Layout(panel11)
        layout11.addWidget(label_response, 0, 0, 1, 1)
        layout11.addWidget(self.group_button_response, 0, 1, 1, 1, Qt.AlignRight)

        panel6 = QWidget(parent)
        layout6 = Layout(panel6)
        layout6.addWidget(label_response_type, 0, 0, 1, 1, Qt.AlignRight)
        layout6.addWidget(self.group_combo_response_type, 0, 1, 1, 1)
        layout6.addWidget(label_response_rank, 1, 0, 1, 1, Qt.AlignRight)
        layout6.addWidget(self.group_combo_response_rank, 1, 1, 1, 1)

        label_atomic = Label(parent, text="Atomic Multipole", bold=True)
        self.group_button_atomic = Button(parent, text="show")
        label_atomic_type = Label(parent, text="type")
        self.group_combo_atomic_type = Combo(parent, ["", "Q", "G", "T", "M"])
        self.group_combo_atomic_basis_type = Combo(parent, ["lm", "jm"])
        label_atomic_braket = Label(parent, text="bra-ket")
        self.group_combo_atomic_bra_basis = Combo(parent, ["s", "p", "d", "f"])
        self.group_combo_atomic_ket_basis = Combo(parent, ["s", "p", "d", "f"])

        panel10 = QWidget(parent)
        layout10 = Layout(panel10)
        layout10.addWidget(label_atomic, 0, 0, 1, 1)
        layout10.addWidget(self.group_button_atomic, 0, 1, 1, 1, Qt.AlignRight)

        panel7 = QWidget(parent)
        layout7 = Layout(panel7)
        layout7.addWidget(label_atomic_type, 0, 0, 1, 1, Qt.AlignRight)
        layout7.addWidget(self.group_combo_atomic_type, 0, 1, 1, 1)
        layout7.addWidget(self.group_combo_atomic_basis_type, 0, 2, 1, 1)
        layout7.addWidget(label_atomic_braket, 1, 0, 1, 1, Qt.AlignRight)
        layout7.addWidget(self.group_combo_atomic_bra_basis, 1, 1, 1, 1)
        layout7.addWidget(self.group_combo_atomic_ket_basis, 1, 2, 1, 1)

        label_virtual_cluster = Label(parent, text="Virtual Cluster", bold=True)
        self.group_button_virtual_cluster = Button(parent, text="show")
        label_vc_neighbor = Label(parent, text="neighbor")
        label_wyckoff = Label(parent, text="wyckoff")
        self.group_combo_vc_wyckoff = Combo(parent)
        self.group_edit_vc_neighbor = LineEdit(parent, text="", validator=("list_int", {"shape": (0,)}))

        panel9 = QWidget(parent)
        layout9 = Layout(panel9)
        layout9.addWidget(label_virtual_cluster, 0, 0, 1, 1)
        layout9.addWidget(self.group_button_virtual_cluster, 0, 1, 1, 1, Qt.AlignRight)

        panel8 = QWidget(parent)
        layout8 = Layout(panel8)
        layout8.addWidget(label_wyckoff, 0, 0, 1, 1, Qt.AlignRight)
        layout8.addWidget(self.group_combo_vc_wyckoff, 0, 1, 1, 1)
        layout8.addWidget(label_vc_neighbor, 1, 0, 1, 1, Qt.AlignRight)
        layout8.addWidget(self.group_edit_vc_neighbor, 1, 1, 1, 1)

        # layout.
        layout.addWidget(panel12, 0, 0, 1, 2)
        layout.addWidget(panel3, 1, 0, 1, 2)
        layout.addWidget(HBar(), 2, 0, 1, 2)

        layout.addWidget(panel5, 3, 0, 1, 1)
        layout.addWidget(panel9, 3, 1, 1, 1)
        layout.addWidget(panel4, 4, 0, 1, 1)
        layout.addWidget(panel8, 4, 1, 1, 1)
        layout.addWidget(HBar(), 5, 0, 1, 2)

        layout.addWidget(panel10, 6, 0, 1, 1)
        layout.addWidget(panel11, 6, 1, 1, 1)
        layout.addWidget(panel7, 7, 0, 1, 1)
        layout.addWidget(panel6, 7, 1, 1, 1)

        layout.addItem(HSpacer(), 0, 3, 1, 1)
        layout.addItem(VSpacer(), 8, 0, 1, 1)

    # ==================================================
