"""
Multipie dialog.

This module provides a dialog for drawing objects with the help of MultiPie.
"""

import sympy as sp
import numpy as np
from PySide6.QtWidgets import QDialog, QTabWidget, QWidget
from PySide6.QtCore import Qt


from qtdraw.widget.custom_widget import Label, Layout, Button, Combo, LineEdit, Check, VSpacer, HSpacer, HBar
from qtdraw.util.util import remove_space, vector3d, str_to_sympy
from qtdraw.multipie.util_multipie import create_samb_object, check_linear_combination

# from qtdraw.multipie.plugin_multipie_setting import crystal_list, point_group_list, space_group_list, point_group_all_list
# from qtdraw.multipie.dialog_info import (
#    show_symmetry_operation,
#    show_character_table,
#    show_wyckoff,
#    show_product_table,
#    show_harmonics,
#    show_harmonics_decomp,
#    show_virtual_cluster,
#    show_atomic_multipole,
#    show_response,
# )
from qtdraw.multipie.plugin_multipie_setting import plugin_detail as detail

from multipie import __version__


# ==================================================
class MultiPieDialog(QDialog):
    # ==================================================
    def __init__(self, parent):
        """
        MultiPie dialog.

        Args:
            parent (MultiPiePlugin): parent.
        """
        super().__init__()
        self._qtdraw = parent  # QtDraw.
        self._pvw = parent.pyvista_widget  # PyVistaWidget.
        self._status = {"version": __version__}

        self.set_title()
        self.resize(600, 500)

        self._pvw.update_preference("label", "default_check", detail["general"]["label"])

        # sub_panel = self.create_sub_group_panel(self)
        # group_panel = self.create_group_panel(self)
        # object_panel = self.create_object_panel(self)
        # basis_panel = self.create_basis_panel(self)

        # self.set_group_panel_value()
        # self.set_object_panel_value()
        # self.set_basis_panel_value()

        # self.set_group_connection()
        # self.set_object_connection()
        # self.set_basis_connection()

        # tab content.
        tab = QTabWidget(self)
        # tab.addTab(group_panel, "Group Info.")
        # tab.addTab(object_panel, "Object Drawing")
        # tab.addTab(basis_panel, "Basis Drawing")

        # main layout.
        layout = Layout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        # layout.addWidget(sub_panel, 0, 0, 1, 1)
        # layout.addWidget(tab, 0, 1, 1, 1)

        # self._symmetry_operation_dialog = None
        # self._character_table_dialog = None
        # self._wyckoff_dialog = None
        # self._product_table_dialog = None
        # self._harmonics_dialog = None
        # self._harmonics_decomp_dialog = None
        # self._virtual_cluster_dialog = None
        # self._atomic_dialog = None
        # self._response_dialog = None

        # self._vector_modulation_dialog = None
        # self._orbital_modulation_dialog = None

        self.show()

    # ==================================================
    def set_title(self):
        title = self._pvw.window_title.replace("QtDraw", "MultiPie Plugin")
        self.setWindowTitle(title)

    # ==================================================
    def clear_data(self):
        # set counter zero.
        pass

    # ==================================================
    def close(self):
        # close all panels.
        super().close()
