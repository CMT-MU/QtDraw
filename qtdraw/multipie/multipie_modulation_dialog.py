import copy
from PySide6.QtWidgets import QDialog
from PySide6.QtCore import Qt

from qtdraw.widget.custom_widget import Layout, Button, LineEdit, Label
from qtdraw.widget.group_model import GroupModel
from qtdraw.widget.group_view import GroupView
from qtdraw.multipie.multipie_util import phase_factor

# ==================================================
modulation_panel = {
    "id": ("hide", {}, "0"),
    "basis": ("combo", ["Q01"], "Q01"),
    "coeff": ("list_float", {"digit": 4}, "1"),
    "k_vector": ("list_float", {"shape": (3,), "var": [""], "digit": 4}, "[1,0,0]"),
    "phase": ("combo", ["cos", "sin"], "cos"),
}


# ==================================================
class ModulationDialog(QDialog):
    # ==================================================
    def __init__(self, parent, modulation_range, var, vec):
        super().__init__(parent)
        self.parent = parent
        self.parent.parent._pvw.save_current()
        self._vec = vec
        mod_panel = copy.deepcopy(modulation_panel)
        mod_panel["basis"] = ("combo", var, var[0])

        title = "Modulation - vector" if vec else "Modulation - orbital"
        self.setWindowTitle(title)
        self.resize(600, 300)

        layout = Layout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        # widget.
        button_add = Button(self, text="Add")
        button_remove = Button(self, text="Remove")
        button_reset = Button(self, text="Reset")
        button_cancel = Button(self, text="Cancel")
        button_ok = Button(self, text="OK")
        label_repeat = Label(self, text="repeat")
        self.edit_range = LineEdit(self, text="[1,1,1]", validator=("list_int", {"shape": (3,)}))

        # modulation data.
        if modulation_range.count(":"):
            modulation, rng = modulation_range.split(":")
        else:
            modulation = modulation_range
            rng = "[1,1,1]"
        mod_list = self.parent._parse_modulation(modulation)
        self.mod_list = [[str(no), *i] for no, i in enumerate(mod_list)]

        model = GroupModel(self, "modulation", mod_panel)
        model.set_data(self.mod_list)
        self.view = GroupView(self, model)
        self.view.customContextMenuRequested.disconnect()
        self.edit_range.setText(rng)

        # main layout.
        layout.addWidget(self.view, 0, 0, 1, 4)
        layout.addWidget(button_add, 1, 0, 1, 1)
        layout.addWidget(button_remove, 1, 1, 1, 1)
        layout.addWidget(label_repeat, 2, 0, 1, 1, Qt.AlignRight)
        layout.addWidget(self.edit_range, 2, 1, 1, 2)
        layout.addWidget(button_reset, 2, 3, 1, 1)
        layout.addWidget(button_cancel, 3, 2, 1, 1)
        layout.addWidget(button_ok, 3, 3, 1, 1)

        # connections.
        button_add.clicked.connect(self.add_data)
        button_remove.clicked.connect(self.remove_data)
        button_reset.clicked.connect(self.reset)
        button_cancel.clicked.connect(self.reject_data)
        button_ok.clicked.connect(self.accept_data)
        self.edit_range.returnPressed.connect(self.create_modulation)

        self.show()

    # ==================================================
    def modulation_range(self):
        data = self.view.model().tolist()
        rng = self.edit_range.text()
        if len(data) < 1:
            return ""
        data = [i[1:] for i in data]
        s = str(data).replace("'", "") + " : " + rng
        return s

    # ==================================================
    def create_modulation(self):
        mr = self.modulation_range()
        if mr == "":
            return

        self.reset()
        if self._vec:
            self.parent.show_vector_samb_modulation(mr)
        else:
            self.parent.show_orbital_samb_modulation(mr)

    # ==================================================
    def add_data(self):
        row_data = copy.deepcopy(self.view.model().column_default)
        n = self.view.model().rowCount()
        row_data[0] = str(n)
        self.view.model().append_row(row_data)

    # ==================================================
    def remove_data(self):
        index = self.view.selectedIndexes()
        if len(index) != 0:
            self.view.model().remove_row(index[0])

            data = self.view.model().tolist()
            for row in range(len(data)):
                data[row][0] = str(row)

            self.view.model().clear_data()
            self.view.model().set_data(data)

    # ==================================================
    def accept_data(self):
        mr = self.modulation_range()
        if self._vec:
            self.parent.edit_vector_modulation.setText(mr)
        else:
            self.parent.edit_orbital_modulation.setText(mr)
        super().accept()

    # ==================================================
    def reject_data(self):
        self.parent.parent._pvw.restore()
        super().reject()

    # ==================================================
    def reset(self):
        self.parent.parent._pvw.restore()
