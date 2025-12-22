"""
Modulation dialog.

This module provides a dialog for modulation dialog.
"""

import copy
from PySide6.QtWidgets import QWidget, QDialog, QDialogButtonBox

from qtdraw.util.util import vector3d
from qtdraw.widget.custom_widget import Layout, Button
from qtdraw.widget.group_model import GroupModel
from qtdraw.widget.group_view import GroupView
from qtdraw.multipie.util_multipie import parse_modulation_list
from qtdraw.multipie.multipie_setting import modulation_panel


# ==================================================
class ModulationDialog(QDialog):
    # ==================================================
    def __init__(self, widget, basis, modulation, head, is_orbital=False, parent=None):
        """
        Modulation dialog.

        Args:
            widget (PyVistaWidget): widget.
            basis (list): valid basis list.
            modulation (str): modulation list.
            head (str): multipole type.
            is_orbital (bool, optional): orbital plot ?
            parent (QWidget, optional): parent.
        """
        super().__init__(parent)
        title = "Modulation"
        if is_orbital:
            title += " - " + "orbital"
        else:
            title += " - " + "vector"
        self.setWindowTitle(title)
        self.resize(600, 300)

        self.widget = widget
        self.basis = basis
        self.head = head
        self.is_orbital = is_orbital
        self.widget.save_current()

        data = parse_modulation_list(modulation)
        panel = self.create_panel(data, self)

        layout = Layout(self)
        layout.addWidget(panel, 0, 0, 1, 1)

        self.show()

    # ==================================================
    def create_panel(self, data, parent):
        """
        Create panel.

        Args:
            data (list): modulation data.
            parent (QWidget): parent.

        Returns:
            - (QWidget) -- panel widget.
        """
        panel = QWidget(parent)
        layout = Layout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        # modulation view.
        mod_panel = copy.deepcopy(modulation_panel)
        mod_panel["basis"] = ("combo", self.basis, self.basis[0])
        model = GroupModel(self.widget, "modulation", mod_panel)
        model.set_data(data)
        self.view = GroupView(parent, model, mathjax=self.parent().plugin._pvw._mathjax)
        self.view.customContextMenuRequested.disconnect()

        # buttons.
        button_add = Button(parent, text="add")
        button_remove = Button(parent, text="remove")

        # button.
        button = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply)
        button.accepted.connect(self.accept)
        button.rejected.connect(self.reject)
        button.button(QDialogButtonBox.Apply).clicked.connect(self.apply)

        # main layout.
        layout.addWidget(self.view, 0, 0, 1, 4)
        layout.addWidget(button_add, 1, 0, 1, 2)
        layout.addWidget(button_remove, 1, 2, 1, 2)
        layout.addWidget(button, 2, 0, 1, 4)

        # connections.
        # button_add.clicked.connect(self.add_data)
        # button_remove.clicked.connect(self.remove_data)

        return panel

    # ==================================================
    def get_raw_data(self):
        """
        Get raw modulation list.

        Returns:
            - (list) -- modulation list.
        """
        data = self.view.model().tolist()
        if len(data) < 1:
            return None
        data = [i[1:] for i in data]

        return data

    # ==================================================
    def add_modulation(self):
        """
        Add modulation.
        """
        ilower = self.parent().plugin._pvw._status["plus"]["ilower"]
        dims = self.parent().plugin._pvw._status["plus"]["dims"]
        data = self.get_raw_data()
        if data is None:
            return

        self.widget.set_repeat(False)

        v = vector3d()
        samb_type = "orbital" if self.is_orbital else "vector"
        obj, igrid = self.parent().plugin.create_samb_modulation(samb_type, v, self.head, data, dims, ilower)

        if self.is_orbital:
            self.parent().plugin.add_orbital_modulation(obj, igrid, self.head)
        else:
            self.parent().plugin.add_vector_modulation(obj, igrid, self.head, v)

    # ==================================================
    def add_data(self):
        """
        Add data in panel.
        """
        row_data = copy.deepcopy(self.view.model().column_default)
        n = self.view.model().rowCount()
        row_data[0] = str(n)
        self.view.model().append_row(row_data)

    # ==================================================
    def remove_data(self):
        """
        Remove data in panel.
        """
        index = self.view.selectedIndexes()
        if len(index) != 0:
            self.view.model().remove_row(index[0])

            data = self.view.model().tolist()
            for row in range(len(data)):
                data[row][0] = str(row)

            self.view.model().clear_data()
            self.view.model().set_data(data)

    # ==================================================
    def accept(self):
        """
        Accept input.
        """
        data = self.get_raw_data()
        if data is not None:
            data = str(data).replace("'", "")
            if self.is_orbital:
                self.parent().basis_edit_orbital_modulation.setText(data)
            else:
                self.parent().basis_edit_vector_modulation.setText(data)
        self.widget.restore()
        self.add_modulation()
        self.close()
        super().accept()

    # ==================================================
    def reject(self):
        """
        Reject input.
        """
        self.widget.restore()
        self.close()
        super().reject()

    # ==================================================
    def apply(self, button):
        """
        Apply input.
        """
        self.widget.restore()
        self.add_modulation()

    # ==================================================
    def close(self):
        """
        Close.
        """
        super().reject()
