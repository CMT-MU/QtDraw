import numpy as np
from qtpy.QtWidgets import QDialog, QLabel, QGridLayout, QDialogButtonBox, QPushButton, QLineEdit
from qtpy.QtCore import Qt
from gcoreutils.dataset import DataSet
from gcoreutils.nsarray import NSArray
from qtdraw.core.group_view import GroupView
from qtdraw.multipie.plot_object import (
    check_get_site,
    parse_modulation_list,
    create_modulated_samb_object,
    plot_modulated_vector_cluster,
    plot_modulated_orbital_cluster,
)


# ==================================================
class DialogModulation(QDialog):
    # ==================================================
    def __init__(self, basis, modulation, head, is_orbital=False, parent=None):
        """
        initialize the class.

        Args:
            basis (list): valid basis list
            modulation (str): modulation list.
            head (str): multipole type.
            is_orbital (bool, optional): orbital plot ?
            parent (QWidget, optional): parent object (DialogGroup).
        """
        super().__init__(parent)
        title = "Modulation"
        if is_orbital:
            title += " - " + "orbital"
        else:
            title += " - " + "vector"
        self.setWindowTitle(title)

        self.parent = parent
        self.basis = basis
        self.head = head
        self.is_orbital = is_orbital
        self.org_range = parent._qtdraw.setting["view_range"]
        if is_orbital:
            self.name = "Z_" + self.parent._qtdraw._get_name("orbital")
        else:
            self.name = "Z_" + self.parent._qtdraw._get_name("vector")

        # set modulation data.
        data = parse_modulation_list(modulation)
        if data is None:
            data = [[]]
        data = [[str(no), basis.index(i[1]), i[0], i[2], i[3]] for no, i in enumerate(data)]
        self.count = len(data)

        role = [
            ("hide", "0"),
            ("combo", basis, 0),
            ("math", "s_scalar", "1"),
            ("math", "s_vector", "[0,0,0]"),
            ("combo", ["cos", "sin"], 0),
        ]
        form = {"list": [["No", "basis", "coeff", "k", "phase"], role, data]}
        self.modulation_data = DataSet(form)

        # modulation panel.
        self.modulation = GroupView(self.modulation_data, "list", parent=parent)
        self.modulation.add_button.hide()
        self.modulation.insert_button.hide()
        self.modulation.remove_button.hide()

        # range.
        self.offset_label = QLabel("lower", self)
        self.offset = QLineEdit(str(self.parent._qtdraw._ilower), self)
        self.repeat_label = QLabel("repeat", self)
        self.repeat = QLineEdit(str(self.parent._qtdraw._dims), self)

        # buttons.
        self.add_button = QPushButton("add", self)
        self.add_button.setFocusPolicy(Qt.NoFocus)
        self.remove_button = QPushButton("remove", self)
        self.remove_button.setFocusPolicy(Qt.NoFocus)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.buttonBox.clicked.connect(self.apply)

        # main layout.
        self.resize(512, 400)
        self.layout = QGridLayout(self)
        self.layout.addWidget(self.modulation, 0, 0, 8, 4)
        self.layout.addWidget(self.add_button, 8, 0, 1, 2)
        self.layout.addWidget(self.remove_button, 8, 2, 1, 2)

        self.layout.addWidget(self.offset_label, 9, 0, 1, 1)
        self.layout.addWidget(self.offset, 9, 1, 1, 1)
        self.layout.addWidget(self.repeat_label, 9, 2, 1, 1)
        self.layout.addWidget(self.repeat, 9, 3, 1, 1)

        self.layout.addWidget(self.buttonBox, 10, 1, 1, 3)

        # connections.
        self.add_button.clicked.connect(self.add_data)
        self.remove_button.clicked.connect(self.remove_data)
        self.finished.connect(self.close)

    # ==================================================
    def add_data(self):
        self.modulation.model.appendRow(name=str(self.count))
        self.count += 1

    # ==================================================
    def remove_data(self):
        index = self.modulation.view.selectedIndexes()
        if len(index) != 0:
            self.modulation.model.removeRow(index[0])

    # ==================================================
    def accept(self):
        self.remove_plot_data(self.name)
        self.plot_modulation()
        self.parent._qtdraw._garbage_collection()
        data_str = self.get_raw_data()[1]
        if data_str is not None:
            if self.is_orbital:
                self.parent.tab2_orbital_modulation_list.setText(data_str)
            else:
                self.parent.tab2_vector_modulation_list.setText(data_str)
        super().accept()

    # ==================================================
    def reject(self):
        self.parent._qtdraw.set_range(self.org_range)
        self.remove_plot_data(self.name)
        self.parent._qtdraw._garbage_collection()
        super().reject()

    # ==================================================
    def apply(self, button):
        if self.buttonBox.standardButton(button) == QDialogButtonBox.Apply:
            self.remove_plot_data(self.name)
            self.parent._qtdraw._garbage_collection()
            self.plot_modulation()

    # ==================================================
    def get_raw_data(self):
        """
        get raw modulation list.

        Returns: tuple.
            - list: modulation list.
            - str: modulation list in str.
        """
        data = self.modulation_data.to_data()["list"][2]
        data = [[self.basis[i[1]]] + i[2:] for i in data if i[0] != ""]
        if len(data) < 1:
            return None, None
        data_str = str([i[:-1] + ["cos"] if i[-1] == 0 else i[:-1] + ["sin"] for i in data]).replace("'", "")

        return data, data_str

    # ==================================================
    def plot_modulation(self):
        """
        plot modulation.
        """
        rng_lu, rng = self.get_range()
        if rng_lu is None:
            return
        data = self.get_raw_data()[0]
        if data is None:
            return

        self.parent._qtdraw.set_range(rng_lu)

        v = NSArray.vector3d()
        if self.is_orbital:
            site = self.parent.tab2_orbital_proj_site
            obj, igrid = create_modulated_samb_object(
                self.parent.tab2_orbital_proj_z_samb,
                site,
                self.parent.tab2_orbital_proj_c_samb,
                self.parent._pgroup,
                v,
                self.head,
                data,
                rng[1],
                rng[0],
                self.parent.pset,
            )

            plot_modulated_orbital_cluster(self.parent._qtdraw, site, obj, self.name, self.parent.pset, igrid, self.head)

        else:
            site = self.parent.tab2_vector_proj_site
            obj, igrid = create_modulated_samb_object(
                self.parent.tab2_vector_proj_z_samb,
                site,
                self.parent.tab2_vector_proj_c_samb,
                self.parent._pgroup,
                v,
                self.head,
                data,
                rng[1],
                rng[0],
                self.parent.pset,
            )

            plot_modulated_vector_cluster(self.parent._qtdraw, site, obj, self.name, self.parent.pset, igrid, self.head, v)

    # ==================================================
    def get_range(self):
        """
        get view range.

        Returns: tuple.
            - list: offset, upper.
            - list: offset, repeat.
        """
        offset = check_get_site(self.offset.text())
        if offset is None:
            return None
        else:
            offset = offset.numpy().astype(int).tolist()
        repeat = check_get_site(self.repeat.text())
        if repeat is None:
            return None
        else:
            repeat = repeat.numpy().astype(int).tolist()

        upper = (np.array(offset) + np.array(repeat)).tolist()
        return [offset, upper], [offset, repeat]

    # ==================================================
    def remove_plot_data(self, name):
        """
        remove plot data from qtdraw.

        Args:
            name (str): vector or orbital.
        """
        group = "orbital" if self.is_orbital else "vector"
        df = self.parent._qtdraw.dataset[group]
        if len(df) > 0:
            df0 = df[df["name"] == name].copy().reset_index(drop=True)
            for i in range(len(df0)):
                obj_id = df0.at[i, "AD"]
                lbl_id = df0.at[i, "AL"]
                if obj_id != "":
                    self.parent._qtdraw._remove_actor(obj_id)
                if lbl_id != "":
                    self.parent._qtdraw._remove_actor(lbl_id)
                self.parent._qtdraw.dataset[group].at[i, "name"] = ""

    # ==================================================
    def keyPressEvent(self, event):
        """
        to prevent enter input.
        """
        return

    # ==================================================
    def close(self):
        if self.is_orbital:
            self.parent.tab2_modulated_orbital_active = False
        else:
            self.parent.tab2_modulated_vector_active = False
        super().close()
