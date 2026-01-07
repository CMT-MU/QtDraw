"""
MultiPie modulation dialog.

This module provides a dialog for modulation editor.
"""

import copy
from PySide6.QtWidgets import QDialog
from PySide6.QtCore import Qt

from qtdraw.widget.custom_widget import Layout, Button, LineEdit, Label, Check
from qtdraw.widget.group_model import GroupModel
from qtdraw.widget.group_view import GroupView

# ==================================================
modulation_panel = {
    "id": ("hide", {}, "0"),
    "basis": ("combo", ["Q01"], "Q01"),
    "coeff": ("math", {"var": [""]}, "1"),
    "k_vector": ("math", {"shape": (3,), "var": [""]}, "[1,0,0]"),
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
        self._var = var

        title = "Modulation - vector" if vec else "Modulation - orbital"
        self.setWindowTitle(title)
        self.resize(600, 300)

        # widget.
        button_add = Button(self, text="Add")
        button_remove = Button(self, text="Remove")
        button_reset = Button(self, text="Reset")
        button_cancel = Button(self, text="Cancel")
        button_ok = Button(self, text="OK")
        label_repeat = Label(self, text="repeat")
        self.edit_range = LineEdit(self, text="[1,1,1]", validator=("list_int", {"shape": (3,)}))
        self.check_magnetic = Check(self, "magnetic")

        # modulation data.
        if modulation_range.count(":"):
            modulation, rng = modulation_range.split(":")
        else:
            modulation = modulation_range
            rng = "[1,1,1]"

        self.edit_range.setText(rng)

        mod_list, is_magnetic = self.parent.data._parse_modulation(modulation)
        self.mod_list = [[str(no), *i] for no, i in enumerate(mod_list)]
        self.check_magnetic.setChecked(is_magnetic)
        self.view = self.create_panel()

        # main layout.
        self.layout = Layout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(5)

        self.layout.addWidget(self.view, 0, 0, 1, 4)
        self.layout.addWidget(self.check_magnetic, 1, 0, 1, 1)
        self.layout.addWidget(button_add, 1, 1, 1, 1)
        self.layout.addWidget(button_remove, 1, 2, 1, 1)
        self.layout.addWidget(label_repeat, 2, 0, 1, 1, Qt.AlignRight)
        self.layout.addWidget(self.edit_range, 2, 1, 1, 2)
        self.layout.addWidget(button_reset, 2, 3, 1, 1)
        self.layout.addWidget(button_cancel, 3, 2, 1, 1)
        self.layout.addWidget(button_ok, 3, 3, 1, 1)

        # connections.
        button_add.clicked.connect(self.add_data)
        button_remove.clicked.connect(self.remove_data)
        button_reset.clicked.connect(self.reset)
        button_cancel.clicked.connect(self.reject_data)
        button_ok.clicked.connect(self.accept_data)
        self.edit_range.returnPressed.connect(self.create_modulation)
        self.check_magnetic.checkStateChanged.connect(self.set_view)

        self.show()

    # ==================================================
    def create_panel(self):
        magnetic = self.check_magnetic.is_checked()
        if magnetic:
            var = self._var["T"] + self._var["M"]
        else:
            var = self._var["Q"] + self._var["G"]

        mod_panel = copy.deepcopy(modulation_panel)
        mod_panel["basis"] = ("combo", var, var[0])

        model = GroupModel(self, "modulation", mod_panel)
        model.set_data(self.mod_list)
        view = GroupView(self, model)
        view.customContextMenuRequested.disconnect()

        return view

    # ==================================================
    def set_view(self):
        self.layout.removeWidget(self.view)
        self.view = self.create_panel()
        self.layout.addWidget(self.view, 0, 0, 1, 4)

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
