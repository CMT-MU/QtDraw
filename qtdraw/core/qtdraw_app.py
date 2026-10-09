"""
Application of QtDraw.

This module provides application of QtDraw.
"""

import os
import copy
import warnings
from pathlib import Path
import logging
from PySide6.QtWidgets import QWidget, QMessageBox, QFileDialog, QDialog, QApplication, QAbstractButton, QComboBox
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QKeySequence

from qtdraw.core.pyvista_widget import PyVistaWidget, Window, same_snapshot
from qtdraw.core.undo_history import UndoHistory
from qtdraw.core.pyvista_widget_setting import widget_detail as detail
from qtdraw.core.dialog_preference import PreferenceDialog
from qtdraw.core.dialog_about import AboutDialog
from qtdraw.core.dialog_about import get_version_info
from qtdraw.widget.custom_widget import Label, Layout, LineEdit, HBar, Button, Combo, VSpacer
from qtdraw.widget.logging_util import LogWidget
from qtdraw.widget.qt_event_util import busy_cursor, font_style_sheet
from qtdraw.util.util import check_multipie


# ==================================================
def add_extension(filename, ext):
    """
    Add extension to file name if it does not have it.

    Args:
        filename (Path): file name.
        ext (str): extension with ".".

    Returns:
        - (Path) -- file name with extension.
    """
    if filename.suffix == ext:
        return filename
    return filename.with_name(filename.name + ext)


# ==================================================
def help_text():
    """
    Mouse and key operations.

    Returns:
        - (str) -- help text.
    """
    open_key = QKeySequence(QKeySequence.Open).toString(QKeySequence.NativeText)
    save_key = QKeySequence(QKeySequence.Save).toString(QKeySequence.NativeText)
    quit_key = QKeySequence(QKeySequence.Quit).toString(QKeySequence.NativeText)
    undo_key = QKeySequence(QKeySequence.Undo).toString(QKeySequence.NativeText)
    redo_key = QKeySequence(QKeySequence.Redo).toString(QKeySequence.NativeText)
    return (
        "In the view:\n"
        "- Left drag: rotate. Shift + left drag: move. Wheel or right drag: zoom.\n"
        "- Right click (without dragging) on an object: menu to open it in the data table, hide or remove it.\n"
        f"- {detail['data_edit_key']}: open the data table of all objects.\n"
        "\n"
        "In the data table:\n"
        "- Right click: menu to create or copy an object.\n"
        "- Esc: clear the selection. Up, Down: move the selection.\n"
        "\n"
        f"{open_key}: open a file. {save_key}: save. {quit_key}: quit.\n"
        f"{undo_key}: undo. {redo_key}: redo (objects, unit cell, range and MultiPie group; not the camera)."
    )


# ==================================================
class QtDraw(Window):
    # ==================================================
    def __init__(self, filename=None, status=None, preference=None):
        """
        3D drawing tool.

        Args:
            filename (str, optional): filename.
            status (dict, optional): status.
            preference (dict, optional): preference.
        """
        log_id = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
            "critial": logging.CRITICAL,
        }
        level = detail["log_level"]
        super().__init__(log_id[level])
        self.debug = level == "debug"

        warnings.showwarning = lambda message, category, filename, lineno, file=None, line=None: logging.warning(str(message))
        warnings.filterwarnings("default", category=DeprecationWarning)

        self._is_view_updating = False
        self.pref_dialog = None  # preference dialog.
        self.multipie_dialog = None  # MultiPie dialog.
        self._history = UndoHistory(limit=50)  # document snapshots for undo.
        self._restoring = False  # restoring a snapshot ?
        if self.debug:
            self.actor_dialog = None  #  actor list dialog.
            self.data_dialog = None  # raw data dialog.
            self.status_dialog = None  # status data dialog.
            self.pref_data_dialog = None  # preference data dialog.
            self.camera_dialog = None  # camera dialog.

        self.create_gui()
        self.pyvista_widget.set_property(status, preference)
        self._saved_state = self._document_state()
        self._update_panel()
        self.create_connection()
        self._create_modified_check()
        self._history.reset(self.pyvista_widget.document_snapshot())
        self._update_undo_actions()
        self.pyvista_widget._tab_group_view.addActions([self.action_undo, self.action_redo])  # shortcuts in data table.

        # event loop.
        self.show()

        if filename is not None and os.path.exists(filename):
            self.load_file(filename)

    # ==================================================
    def create_gui(self):
        """
        create gui.

        :meta private:
        """
        self.resize(*detail["window_size"])

        # central grid.
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = Layout(central_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setVerticalSpacing(5)

        # PyVista widget.
        self.info_dialog = LogWidget(title="Information")
        txt = get_version_info()
        self.write_info(txt)
        self.pyvista_widget = PyVistaWidget(self)

        # Control panel.
        self.panel = self.create_panel(parent=self)

        # Status bar.
        self.status = Label(self, "")
        self.status.setAlignment(Qt.AlignRight)
        self.status.setContentsMargins(0, 0, 10, 0)
        self.status.setText(self.pyvista_widget.copyright)

        layout.addWidget(self.pyvista_widget, 0, 0, 1, 1)
        layout.addWidget(self.panel, 0, 1, 1, 1)
        layout.addWidget(self.status, 1, 0, 1, 2)

        self._create_menu()
        self._set_tool_tips()

    # ==================================================
    def _create_menu(self):
        """
        Create menu bar with standard shortcuts.

        :meta private:
        """

        def action(menu, text, slot, shortcut=None):
            act = QAction(text, self)
            if shortcut is not None:
                act.setShortcut(shortcut)
            act.triggered.connect(slot)
            menu.addAction(act)
            return act

        menu = self.menuBar().addMenu("&File")
        self.action_open = action(menu, "&Open...", self.open_file, QKeySequence.Open)
        self.action_save = action(menu, "&Save...", self.save_file, QKeySequence.Save)
        self.action_screenshot = action(menu, "Screens&hot...", self._save_screenshot)
        menu.addSeparator()
        self.action_clear = action(menu, "&Clear", self._clear_data)
        menu.addSeparator()
        self.action_quit = action(menu, "&Quit", self.close, QKeySequence.Quit)
        self.action_quit.setMenuRole(QAction.QuitRole)

        menu = self.menuBar().addMenu("&Edit")
        self.action_undo = action(menu, "&Undo", self.undo, QKeySequence.Undo)
        self.action_redo = action(menu, "&Redo", self.redo, QKeySequence.Redo)

        menu = self.menuBar().addMenu("&Window")
        self.action_info = action(menu, "&Info", lambda: self.info_dialog.show())
        self.action_log = action(menu, "&Log", lambda: self.logger.show())

        menu = self.menuBar().addMenu("&Help")
        self.action_help = action(menu, "&Mouse and Keys", self._show_help)
        self.action_about = action(menu, "&About QtDraw", self._show_about)
        self.action_about.setMenuRole(QAction.AboutRole)

    # ==================================================
    def _set_tool_tips(self):
        """
        Set tool tips of buttons.

        :meta private:
        """
        tips = {
            self.ds_button_edit: f"Open the data table of all objects (key: {detail['data_edit_key']}).",
            self.misc_button_pref: "Change preferences such as colors, fonts and lights.",
            self.misc_button_about: "Show the version and the authors.",
            self.view_button_default: "Reset the view to the default direction.",
            self.view_button_clip: "Hide objects outside the range lower-upper.",
            self.view_button_repeat: "Repeat the objects of the home cell in the range lower-upper.",
            self.view_button_bar: "Show the color bar.",
            self.view_button_parallel: "Use parallel projection.",
            self.view_button_grid: "Show the grid.",
        }
        if hasattr(self, "misc_button_multipie"):
            tips[self.misc_button_multipie] = "Open the MultiPie dialog for symmetry-adapted drawing."
        for button, tip in tips.items():
            if not button.toolTip():  # keep tool tips set elsewhere.
                button.setToolTip(tip)

    # ==================================================
    def _show_help(self):
        """
        Show mouse and key operations.

        :meta private:
        """
        QMessageBox.information(self, "Mouse and Keys", help_text())

    # ==================================================
    def open_file(self):
        """
        Open file dialog.

        :meta private:
        """
        self._commit_pending_input()
        if not self._confirm_unsaved("opening another file"):
            return

        ext = detail["extension"]
        mat = "*" + " *".join(detail["ext_material"])
        cwd = os.getcwd()
        ext_set = f"QtDraw, CIF, VESTA, XSF Files (*{ext} {mat})"
        filename, _ = QFileDialog.getOpenFileName(self, "Open File", cwd, ext_set, options=QFileDialog.Options())

        if filename:
            filename = Path(filename)
            cur_ext = str(filename.suffix)
            if cur_ext == "":
                filename = str(filename) + ext
            if ext in ext_set:
                self.load_file(str(filename))

    # ==================================================
    def load_file(self, filename):
        """
        Load file.

        Args:
            filename (str): full file name.

        :meta private:
        """
        self._flush()
        with busy_cursor():
            self.pyvista_widget.load(filename)

        self._update_panel_quietly()

        multipie = self.pyvista_widget._status.get("multipie", {})
        if multipie and self.pyvista_widget._mp_data is not None:
            self._show_multipie()
            if self.multipie_dialog is not None:
                self.multipie_dialog.set_data()

        self._mark_saved()
        self._reset_history()

    # ==================================================
    def _update_panel_quietly(self):
        """
        Update panel without applying its values to the document again.

        :meta private:
        """
        # to avoid redraw object twice.
        # disconnect unit cell.
        self.uc_combo_crystal.currentTextChanged.disconnect(self._set_crystal)
        self.uc_edit_origin.returnPressed.disconnect(self._set_origin)
        self.uc_edit_a.returnPressed.disconnect(self._set_a)
        self.uc_edit_b.returnPressed.disconnect(self._set_b)
        self.uc_edit_c.returnPressed.disconnect(self._set_c)
        self.uc_edit_alpha.returnPressed.disconnect(self._set_alpha)
        self.uc_edit_beta.returnPressed.disconnect(self._set_beta)
        self.uc_edit_gamma.returnPressed.disconnect(self._set_gamma)
        # disconnect view.
        self.view_button_clip.toggled.disconnect(self._set_clip)
        self.view_button_repeat.toggled.disconnect(self._set_repeat)
        self.view_button_nonrepeat.clicked.disconnect(self._nonrepeat)
        self.view_edit_lower.returnPressed.disconnect(self._set_lower)
        self.view_edit_upper.returnPressed.disconnect(self._set_upper)

        self._update_panel()

        # reconnect unit cell.
        self.uc_combo_crystal.currentTextChanged.connect(self._set_crystal)
        self.uc_edit_origin.returnPressed.connect(self._set_origin)
        self.uc_edit_a.returnPressed.connect(self._set_a)
        self.uc_edit_b.returnPressed.connect(self._set_b)
        self.uc_edit_c.returnPressed.connect(self._set_c)
        self.uc_edit_alpha.returnPressed.connect(self._set_alpha)
        self.uc_edit_beta.returnPressed.connect(self._set_beta)
        self.uc_edit_gamma.returnPressed.connect(self._set_gamma)
        # reconnect view.
        self.view_button_clip.toggled.connect(self._set_clip)
        self.view_button_repeat.toggled.connect(self._set_repeat)
        self.view_button_nonrepeat.clicked.connect(self._nonrepeat)
        self.view_edit_lower.returnPressed.connect(self._set_lower)
        self.view_edit_upper.returnPressed.connect(self._set_upper)

    # ==================================================
    def save_file(self):
        """
        Save file dialog.

        Returns:
            - (bool) -- saved ? (False if the dialog was cancelled)

        :meta private:
        """
        ext = detail["extension"]
        file = Path.cwd() / (self.pyvista_widget._status["model"] + ext)
        ext_set = f"QtDraw Files (*{ext})"
        filename, _ = QFileDialog.getSaveFileName(self, "Save File", str(file.name), ext_set, options=QFileDialog.Options())

        if not filename:  # cancelled.
            return False
        filename = add_extension(Path(filename), ext)
        self._save(str(filename))
        self._mark_saved()
        return True

    # ==================================================
    def _save_screenshot(self):
        """
        Save screenshot dialog.

        :meta private:
        """
        ifile = " ".join(detail["image_file"]).replace(".", "*.")
        gfile = " ".join(detail["vector_file"]).replace(".", "*.")
        ext = detail["image_file"][0]

        file = Path.cwd() / (self.pyvista_widget._status["model"] + ext)

        ext_set = f"Image Files ({ifile});;Graphic Files ({gfile})"
        filename, selected = QFileDialog.getSaveFileName(self, "Save Screenshot", str(file.name), ext_set)
        if not filename:  # cancelled.
            return

        # add extension of selected filter if not given.
        filename = Path(filename)
        if filename.suffix not in detail["image_file"] + detail["vector_file"]:
            ext = detail["vector_file"][0] if selected.startswith("Graphic") else detail["image_file"][0]
            filename = filename.with_name(filename.name + ext)
            # the dialog asked about the original name only.
            if filename.exists():
                ret = QMessageBox.question(
                    self, "Save Screenshot", f"{filename.name} already exists.\nReplace it?", QMessageBox.Ok | QMessageBox.Cancel
                )
                if ret != QMessageBox.Ok:
                    return

        self.pyvista_widget.save_screenshot(str(filename))

    # ==================================================
    def create_panel(self, parent):
        """
        create right panel.

        Args:
            parent (QWidget): parent.

        Returns:
            - (QWidget) -- right panel.

        :meta private:
        """
        panel = QWidget(parent)
        panel.setGeometry(60, 50, 180, 694)
        panel.setMaximumWidth(220)
        layout = Layout(panel)
        layout.setContentsMargins(10, 5, 5, 5)

        uc = self.create_gui_unit_cell(panel)
        view = self.create_gui_view(panel)
        buttons = self.create_gui_buttons(panel)
        if self.debug:
            debug = self.create_gui_debug(panel)

        layout.addWidget(uc, 0, 0, 1, 1)
        layout.addWidget(HBar(), 1, 0, 1, 1)
        layout.addWidget(view, 2, 0, 1, 1)
        layout.addWidget(HBar(), 3, 0, 1, 1)
        layout.addWidget(buttons, 4, 0, 1, 1)
        if self.debug:
            layout.addWidget(HBar(), 5, 0, 1, 1)
            layout.addWidget(debug, 6, 0, 1, 1)
            layout.addItem(VSpacer(), 7, 0, 1, 1)
        else:
            layout.addItem(VSpacer(), 5, 0, 1, 1)

        return panel

    # ==================================================
    def create_gui_unit_cell(self, parent):
        """
        Create unit cell panel.

        Args:
            parent (QWidget): parent.

        Returns:
            - (QWidget) -- unit cell panel.

        :meta private:
        """
        panel = QWidget(parent)
        layout = Layout(panel)

        label_uc = Label(parent, text="UnitCell", bold=True)

        label_crystal = Label(parent, text="Crystal")
        self.uc_combo_crystal = Combo(
            parent, ["", "triclinic", "monoclinic", "orthorhombic", "tetragonal", "trigonal", "hexagonal", "cubic"]
        )

        label_origin = Label(parent, text="Origin")
        self.uc_edit_origin = LineEdit(parent, "", validator=("list_float", {"shape": (3,), "var": [""], "digit": 2}))

        self.uc_label_volume = Label(parent)

        label_a = Label(parent, text="a")
        self.uc_edit_a = LineEdit(parent, "", validator=("float", {"digit": 4}))

        label_b = Label(parent, text="b")
        self.uc_edit_b = LineEdit(parent, "", validator=("float", {"digit": 4}))

        label_c = Label(parent, text="c")
        self.uc_edit_c = LineEdit(parent, "", validator=("float", {"digit": 4}))

        label_alpha = Label(parent, text="\u03b1")
        self.uc_edit_alpha = LineEdit(parent, "", validator=("float", {"digit": 2}))

        label_beta = Label(parent, text="\u03b2")
        self.uc_edit_beta = LineEdit(parent, "", validator=("float", {"digit": 2}))

        label_gamma = Label(parent, text="\u03b3")
        self.uc_edit_gamma = LineEdit(parent, "", validator=("float", {"digit": 2}))

        panel1 = QWidget(parent)
        layout1 = Layout(panel1)
        layout1.addWidget(label_uc, 0, 0, 1, 4)
        layout1.addWidget(self.uc_label_volume, 0, 4, 1, 4)

        panel2 = QWidget(parent)
        layout2 = Layout(panel2)
        layout2.setContentsMargins(0, 10, 0, 10)
        layout2.setVerticalSpacing(2)
        layout2.addWidget(label_a, 0, 0, 1, 1)
        layout2.addWidget(self.uc_edit_a, 0, 1, 1, 3)
        layout2.addWidget(label_alpha, 0, 4, 1, 1)
        layout2.addWidget(self.uc_edit_alpha, 0, 5, 1, 3)
        layout2.addWidget(label_b, 1, 0, 1, 1)
        layout2.addWidget(self.uc_edit_b, 1, 1, 1, 3)
        layout2.addWidget(label_beta, 1, 4, 1, 1)
        layout2.addWidget(self.uc_edit_beta, 1, 5, 1, 3)
        layout2.addWidget(label_c, 2, 0, 1, 1)
        layout2.addWidget(self.uc_edit_c, 2, 1, 1, 3)
        layout2.addWidget(label_gamma, 2, 4, 1, 1)
        layout2.addWidget(self.uc_edit_gamma, 2, 5, 1, 3)

        panel3 = QWidget(parent)
        layout3 = Layout(panel3)
        layout3.addWidget(label_crystal, 0, 0, 1, 2)
        layout3.addWidget(self.uc_combo_crystal, 0, 2, 1, 6)
        layout3.addWidget(label_origin, 1, 0, 1, 2)
        layout3.addWidget(self.uc_edit_origin, 1, 2, 1, 6)

        layout.addWidget(panel1, 0, 0, 1, 1)
        layout.addWidget(panel2, 1, 0, 1, 1)
        layout.addWidget(panel3, 2, 0, 1, 1)

        return panel

    # ==================================================
    def create_gui_view(self, parent):
        """
        Create view panel.

        Args:
            parent (QWidget): parent.

        Returns:
            - (QWidget) -- view panel.

        :meta private:
        """
        panel = QWidget(parent)
        layout = Layout(panel)

        label_view = Label(parent, text="View", bold=True)
        self.view_button_clip = Button(parent, text="clip", toggle=True)
        self.view_button_repeat = Button(parent, text="repeat", toggle=True)
        self.view_button_nonrepeat = Button(parent, text="non-repeat")
        self.view_button_nonrepeat.setToolTip(
            "Convert repeated copies into independent objects in the home cell (can be undone with Undo)."
        )

        label_lower = Label(parent, text="lower")
        self.view_edit_lower = LineEdit(parent, "", validator=("list_float", {"shape": (3,), "var": [""], "digit": 2}))
        label_upper = Label(parent, text="upper")
        self.view_edit_upper = LineEdit(parent, "", validator=("list_float", {"shape": (3,), "var": [""], "digit": 2}))

        self.view_button_x = Button(parent, text="+x")
        self.view_button_y = Button(parent, text="+y")
        self.view_button_z = Button(parent, text="+z")
        self.view_button_xm = Button(parent, text="-x")
        self.view_button_ym = Button(parent, text="-y")
        self.view_button_zm = Button(parent, text="-z")
        label_a = Label(parent, text="a")
        label_b = Label(parent, text="b")
        label_c = Label(parent, text="c")
        self.view_combo_a = Combo(parent, [str(i) for i in range(-9, 10)])
        self.view_combo_b = Combo(parent, [str(i) for i in range(-9, 10)])
        self.view_combo_c = Combo(parent, [str(i) for i in range(-9, 10)])

        self.view_button_default = Button(parent, text="default")
        self.view_button_bar = Button(parent, text="bar", toggle=True)
        self.view_button_parallel = Button(parent, text="parallel", toggle=True)
        self.view_button_grid = Button(parent, text="grid", toggle=True)

        label_axis = Label(parent, text="axis")
        self.view_combo_axis = Combo(parent, ["on", "axis", "full", "off"])
        label_cell = Label(parent, text="cell")
        self.view_combo_cell = Combo(parent, ["single", "all", "off"])

        panel1 = QWidget(parent)
        layout1 = Layout(panel1)
        layout1.addWidget(label_view, 0, 0, 1, 4)
        layout1.addWidget(self.view_button_nonrepeat, 0, 4, 1, 4)
        layout1.addWidget(self.view_button_clip, 1, 0, 1, 4)
        layout1.addWidget(self.view_button_repeat, 1, 4, 1, 4)

        panel2 = QWidget(parent)
        layout2 = Layout(panel2)
        layout2.setVerticalSpacing(2)
        layout2.addWidget(label_lower, 0, 0, 1, 2)
        layout2.addWidget(self.view_edit_lower, 0, 2, 1, 6)
        layout2.addWidget(label_upper, 1, 0, 1, 2)
        layout2.addWidget(self.view_edit_upper, 1, 2, 1, 6)

        panel3 = QWidget(parent)
        layout3 = Layout(panel3)
        layout3.setContentsMargins(0, 10, 0, 10)
        layout3.setVerticalSpacing(2)
        layout3.addWidget(self.view_button_default, 0, 0, 1, 3)
        layout3.addWidget(self.view_button_bar, 0, 4, 1, 4)
        layout3.addWidget(self.view_button_x, 1, 0, 1, 1)
        layout3.addWidget(self.view_button_xm, 1, 1, 1, 1)
        layout3.addWidget(label_a, 1, 4, 1, 1)
        layout3.addWidget(self.view_combo_a, 1, 5, 1, 3)
        layout3.addWidget(self.view_button_y, 2, 0, 1, 1)
        layout3.addWidget(self.view_button_ym, 2, 1, 1, 1)
        layout3.addWidget(label_b, 2, 4, 1, 1)
        layout3.addWidget(self.view_combo_b, 2, 5, 1, 3)
        layout3.addWidget(self.view_button_z, 3, 0, 1, 1)
        layout3.addWidget(self.view_button_zm, 3, 1, 1, 1)
        layout3.addWidget(label_c, 3, 4, 1, 1)
        layout3.addWidget(self.view_combo_c, 3, 5, 1, 3)

        panel4 = QWidget(parent)
        layout4 = Layout(panel4)
        layout4.setVerticalSpacing(2)
        layout4.addWidget(self.view_button_parallel, 1, 0, 1, 4)
        layout4.addWidget(self.view_button_grid, 1, 4, 1, 4)

        panel5 = QWidget(parent)
        layout5 = Layout(panel5)
        layout5.addWidget(label_axis, 0, 0, 1, 1)
        layout5.addWidget(self.view_combo_axis, 0, 1, 1, 3)
        layout5.addWidget(label_cell, 0, 4, 1, 1)
        layout5.addWidget(self.view_combo_cell, 0, 5, 1, 3)

        layout.addWidget(panel1, 0, 0, 1, 1)
        layout.addWidget(panel2, 1, 0, 1, 1)
        layout.addWidget(panel3, 2, 0, 1, 1)
        layout.addWidget(panel4, 3, 0, 1, 1)
        layout.addWidget(panel5, 4, 0, 1, 1)

        return panel

    # ==================================================
    def create_gui_buttons(self, parent):
        """
        Create button panel (other commands are in the menu bar).

        Args:
            parent (QWidget): parent.

        Returns:
            - (QWidget) -- button panel.

        :meta private:
        """
        panel = QWidget(parent)
        layout = Layout(panel)

        self.ds_button_edit = Button(parent, text="edit")
        self.misc_button_pref = Button(parent, text="preference")
        self.misc_button_about = Button(parent, text="about")
        if check_multipie():
            self.misc_button_multipie = Button(parent, text="MultiPie")

        panel1 = QWidget(parent)
        layout1 = Layout(panel1)
        layout1.addWidget(self.ds_button_edit, 0, 0, 1, 1)
        layout1.addWidget(self.misc_button_pref, 0, 1, 1, 1)
        layout1.addWidget(self.misc_button_about, 1, 0, 1, 1)
        if check_multipie():
            layout1.addWidget(self.misc_button_multipie, 1, 1, 1, 1)

        layout.addWidget(panel1, 0, 0, 1, 1)

        return panel

    # ==================================================
    def create_gui_debug(self, parent):
        """
        Create debug panel.

        Args:
            parent (QWidget): parent.

        Returns:
            - (QWidget) -- debug panel.

        :meta private:
        """
        panel = QWidget(parent)
        layout = Layout(panel)

        label_debug = Label(parent, text="Debug", bold=True)
        self.debug_button_camera = Button(parent, text="camera")
        self.debug_button_actor = Button(parent, text="actor")
        self.debug_button_data = Button(parent, text="data")
        self.debug_button_status = Button(parent, text="status")
        self.debug_button_preference = Button(parent, text="pref")

        panel1 = QWidget(parent)
        layout1 = Layout(panel1)
        layout1.addWidget(label_debug, 0, 0, 1, 1)
        layout1.addWidget(self.debug_button_camera, 0, 1, 1, 1)
        layout1.addWidget(self.debug_button_data, 1, 0, 1, 1)
        layout1.addWidget(self.debug_button_actor, 1, 1, 1, 1)
        layout1.addWidget(self.debug_button_status, 2, 0, 1, 1)
        layout1.addWidget(self.debug_button_preference, 2, 1, 1, 1)

        layout.addWidget(panel1, 0, 0, 1, 1)

        return panel

    # ==================================================
    def _document_state(self):
        """
        Current document state to detect unsaved changes.

        Returns:
            - (dict) -- objects, status saved in file, and MultiPie status.

        :meta private:
        """
        # status saved in file and changed by editing (view settings are not counted as modification).
        keys = ["origin", "cell", "crystal", "clip", "repeat", "lower", "upper"]
        widget = self.pyvista_widget
        status = {key: widget._status.get(key) for key in keys}
        multipie = widget._mp_data.status if widget._mp_data is not None else {}
        return copy.deepcopy({"data": widget.get_data_dict(), "status": status, "multipie": multipie})

    # ==================================================
    def is_modified(self):
        """
        Is document modified after it was opened or saved ?

        Returns:
            - (bool) -- modified ?
        """
        return self._document_state() != self._saved_state

    # ==================================================
    def _mark_saved(self):
        """
        Mark current document as saved.

        :meta private:
        """
        self._saved_state = self._document_state()
        self._update_title()

    # ==================================================
    def _create_modified_check(self):
        """
        Update "*" in window title shortly after objects are changed.

        :meta private:
        """
        self._modified_timer = QTimer(self)
        self._modified_timer.setSingleShot(True)
        self._modified_timer.setInterval(300)
        self._modified_timer.timeout.connect(self._settle)
        for model in self.pyvista_widget._data.values():
            model.dataModified.connect(self._document_changed)
            model.dataRemoved.connect(self._document_changed)
            model.checkChanged.connect(self._document_changed)
            model.modelReset.connect(self._document_changed)  # deferred group rename.
        self.pyvista_widget.document_changed.connect(self._document_changed)
        # status changed from panel (e.g. clip), which may not change objects.
        for button in self.findChildren(QAbstractButton):
            button.clicked.connect(self._document_changed)
        for combo in self.findChildren(QComboBox):
            combo.currentIndexChanged.connect(self._document_changed)
        for edit in self.findChildren(LineEdit):
            edit.returnPressed.connect(self._document_changed)

    # ==================================================
    def _document_changed(self, *args):
        """
        Start the timer to record the document after a change.

        :meta private:
        """
        if self._restoring:
            return
        self._modified_timer.start()
        self._update_undo_actions()

    # ==================================================
    def _settle(self):
        """
        Record the settled document for undo, and update the title.

        :meta private:
        """
        if self._restoring:
            return
        snapshot = self.pyvista_widget.document_snapshot()
        if self._history.current() is None:
            self._history.reset(snapshot)
        else:
            self._history.record(snapshot, same=same_snapshot)
        self._update_title()
        self._update_undo_actions()

    # ==================================================
    def _flush(self):
        """
        Record a pending change now (before undo, redo, load and save).

        :meta private:
        """
        self._commit_pending_input()
        for model in self.pyvista_widget._data.values():
            model.run_pending_renames()
        self._modified_timer.stop()
        self._settle()

    # ==================================================
    def _reset_history(self):
        """
        Start a new undo history with the current document.

        :meta private:
        """
        self._modified_timer.stop()
        self._history.reset(self.pyvista_widget.document_snapshot())
        self._update_undo_actions()

    # ==================================================
    def _update_undo_actions(self):
        """
        Enable undo and redo in Edit menu.

        :meta private:
        """
        if hasattr(self, "action_undo"):
            self.action_undo.setEnabled(self.can_undo())
            self.action_redo.setEnabled(self.can_redo())

    # ==================================================
    def _move_history(self, step):
        """
        Undo (step=-1) or redo (step=1).

        :meta private:
        """
        if self._restoring:
            return
        self._flush()
        target = self._history.peek_undo() if step < 0 else self._history.peek_redo()
        if target is None:
            return
        try:
            if self._restore(target):
                if step < 0:
                    self._history.commit_undo()
                else:
                    self._history.commit_redo()
        finally:
            self._update_title()
            self._update_undo_actions()

    # ==================================================
    def _restore(self, snapshot):
        """
        Restore a snapshot, or the current document again if it fails.

        Args:
            snapshot (dict): snapshot.

        Returns:
            - (bool) -- restored ? (an exception is raised if not)

        :meta private:
        """
        before = self.pyvista_widget.document_snapshot()
        self._restoring = True
        try:
            try:
                self.pyvista_widget.restore_document(snapshot)
                return True
            except Exception:
                try:
                    self.pyvista_widget.restore_document(before)
                except Exception:
                    self._history.clear()
                    try:
                        self._history.reset(self.pyvista_widget.document_snapshot())
                    except Exception:
                        pass  # history stays empty until the next successful snapshot.
                raise
        finally:
            try:
                self._after_restore()
            finally:
                self._restoring = False
                self._modified_timer.stop()  # changes made by the restore are not recorded.

    # ==================================================
    def _after_restore(self):
        """
        Update panel and MultiPie dialog after a restore.

        :meta private:
        """
        self._update_panel_quietly()
        if self.multipie_dialog is not None:
            if self.pyvista_widget._mp_data is None:
                self.multipie_dialog.close()
                self.multipie_dialog.deleteLater()  # by Qt at a safe point, not by the garbage collector later.
                self.multipie_dialog = None
                self.status.setText("MultiPie dialog closed: the restored document has no MultiPie group.")
            else:
                self.multipie_dialog.set_data(quiet=True)  # show the restored group, without changing it.

    # ==================================================
    def undo(self):
        """
        Undo the last change of the document (objects, unit cell, range and MultiPie).

        Note:
            - camera, view settings and preferences are not changed.
            - changes made in a row without running the event loop, e.g. in one Jupyter cell, are one step.
        """
        self._move_history(-1)

    # ==================================================
    def redo(self):
        """
        Redo the change undone last.

        Note:
            - changes made in a row without running the event loop, e.g. in one Jupyter cell, are one step.
        """
        self._move_history(1)

    # ==================================================
    def can_undo(self):
        """
        Undo possible ?

        Returns:
            - (bool) -- there is a change to undo ?
        """
        return self._history.can_undo() or self._modified_timer.isActive()

    # ==================================================
    def can_redo(self):
        """
        Redo possible ?

        Returns:
            - (bool) -- there is an undone change to redo ?
        """
        return not self._modified_timer.isActive() and self._history.can_redo()

    # ==================================================
    def _commit_pending_input(self):
        """
        Apply value typed in focused field but not confirmed by Enter.

        :meta private:
        """
        widget = QApplication.focusWidget()
        if isinstance(widget, LineEdit):
            widget.commit_pending()

    # ==================================================
    def _confirm_unsaved(self, action, always=False):
        """
        Ask to save unsaved changes.

        Args:
            action (str): action to be done, e.g. "closing".
            always (bool, optional): ask also without unsaved changes ?

        Returns:
            - (bool) -- go on with the action ?

        :meta private:
        """
        modified = self.is_modified()
        if not modified and not always:
            return True

        model = self.pyvista_widget._status["model"]
        text = f"Save changes to '{model}' before {action}?" if modified else f"Save '{model}' before {action}?"
        ret = QMessageBox.question(
            self,
            "",
            text,
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            QMessageBox.Save,
        )
        if ret == QMessageBox.Save:
            return self.save_file()  # not saved if save dialog was cancelled.
        return ret == QMessageBox.Discard

    # ==================================================
    def _update_panel(self):
        """
        Update widget in panel.

        :meta private:
        """
        self._update_application()
        self._update_title()
        self._update_unit_cell()
        self._update_view()

    # ==================================================
    def _update_application(self):
        """
        Update application sytle.

        :meta private:
        """
        self.app.setStyle("fusion")  # fixed, the same look on all platforms.
        font_type = self.pyvista_widget._preference["general"]["font"]
        size = self.pyvista_widget._preference["general"]["size"]
        self.app.setStyleSheet(font_style_sheet(font_type, size))

    # ==================================================
    def _update_title(self):
        """
        Update window title.

        :meta private:
        """
        title = self.pyvista_widget.window_title
        if self.is_modified():
            title += " *"
        data_title = title.replace("QtDraw", "Dataset")
        self.setWindowTitle(title)
        self.pyvista_widget._tab_group_view.setWindowTitle(data_title)
        if self.multipie_dialog is not None:
            self.multipie_dialog.set_title()

    # ==================================================
    def _update_unit_cell(self):
        """
        Update unit cell widget.

        :meta private:
        """
        crystal = self.pyvista_widget._status["crystal"]

        self.uc_combo_crystal.setCurrentText(f"{crystal}")

        if crystal == "monoclinic":
            ro = [False, False, False, True, False, True]
        elif crystal == "orthorhombic":
            ro = [False, False, False, True, True, True]
        elif crystal in ["tetragonal", "trigonal", "hexagonal"]:
            ro = [False, True, False, True, True, True]
        elif crystal == "cubic":
            ro = [False, True, True, True, True, True]
        else:  # ""/"triclinic
            ro = [False, False, False, False, False, False]

        self.uc_edit_a.set_read_only(ro[0])
        self.uc_edit_b.set_read_only(ro[1])
        self.uc_edit_c.set_read_only(ro[2])
        self.uc_edit_alpha.set_read_only(ro[3])
        self.uc_edit_beta.set_read_only(ro[4])
        self.uc_edit_gamma.set_read_only(ro[5])

        self.uc_edit_origin.setText(f"{self.pyvista_widget.origin}")

        status_a = self.pyvista_widget._status["cell"]["a"]
        self.uc_edit_a.setText(str(status_a))
        status_b = self.pyvista_widget._status["cell"]["b"]
        self.uc_edit_b.setText(str(status_b))
        status_c = self.pyvista_widget._status["cell"]["c"]
        self.uc_edit_c.setText(str(status_c))
        status_alpha = self.pyvista_widget._status["cell"]["alpha"]
        self.uc_edit_alpha.setText(str(status_alpha))
        status_beta = self.pyvista_widget._status["cell"]["beta"]
        self.uc_edit_beta.setText(str(status_beta))
        status_gamma = self.pyvista_widget._status["cell"]["gamma"]
        self.uc_edit_gamma.setText(str(status_gamma))

        self.uc_label_volume.setText(f"Volume {self.pyvista_widget.cell_volume:.04f}")

    # ==================================================
    def _update_view(self):
        """
        Update view.

        :meta private:
        """
        self.view_button_clip.setChecked(self.pyvista_widget._status["clip"])

        self.view_button_repeat.setChecked(self.pyvista_widget._status["repeat"])

        self.view_edit_lower.setText(str(self.pyvista_widget._status["lower"]))
        self.view_edit_upper.setText(str(self.pyvista_widget._status["upper"]))

        self.view_combo_a.blockSignals(True)
        self.view_combo_b.blockSignals(True)
        self.view_combo_c.blockSignals(True)
        self.view_combo_a.setCurrentText(str(self.pyvista_widget._status["view"][0]))
        self.view_combo_b.setCurrentText(str(self.pyvista_widget._status["view"][1]))
        self.view_combo_c.setCurrentText(str(self.pyvista_widget._status["view"][2]))
        self.view_combo_a.blockSignals(False)
        self.view_combo_b.blockSignals(False)
        self.view_combo_c.blockSignals(False)

        self.view_button_bar.setChecked(self.pyvista_widget._status["bar"])
        self.view_button_parallel.setChecked(self.pyvista_widget._status["parallel_projection"])
        self.view_button_grid.setChecked(self.pyvista_widget._status["grid"])

        self.view_combo_axis.setCurrentText(self.pyvista_widget._status["axis_type"])
        self.view_combo_cell.setCurrentText(self.pyvista_widget._status["cell_mode"])

    # ==================================================
    def _set_crystal(self, crystal=None):
        """
        Set crystal.

        Args:
            crystal (str, optional): crystal.

        :meta private:
        """
        self.pyvista_widget.set_crystal(crystal)

        self._update_unit_cell()

    # ==================================================
    def _set_origin(self):
        """
        Set origin.

        :meta private:
        """
        origin = self.uc_edit_origin.text()
        if origin == "":
            origin = None
        self.pyvista_widget.set_origin(origin)

        self._update_unit_cell()

    # ==================================================
    def _set_a(self):
        """
        Set lattice constant, a.

        :meta private:
        """
        a = self.uc_edit_a.text()
        cell = None if a == "" else {"a": a}
        self.pyvista_widget.set_unit_cell(cell)

        self._update_unit_cell()

    # ==================================================
    def _set_b(self):
        """
        Set lattice constant, b.

        :meta private:
        """
        b = self.uc_edit_b.text()
        cell = None if b == "" else {"b": b}
        self.pyvista_widget.set_unit_cell(cell)

        self._update_unit_cell()

    # ==================================================
    def _set_c(self):
        """
        Set lattice constant, c.

        :meta private:
        """
        c = self.uc_edit_c.text()
        cell = None if c == "" else {"c": c}
        self.pyvista_widget.set_unit_cell(cell)

        self._update_unit_cell()

    # ==================================================
    def _set_alpha(self):
        """
        Set lattice angle, alpha.

        :meta private:
        """
        alpha = self.uc_edit_alpha.text()
        cell = None if alpha == "" else {"alpha": alpha}
        self.pyvista_widget.set_unit_cell(cell)

        self._update_unit_cell()

    # ==================================================
    def _set_beta(self):
        """
        Set lattice angle, beta.

        :meta private:
        """
        beta = self.uc_edit_beta.text()
        cell = None if beta == "" else {"beta": beta}
        self.pyvista_widget.set_unit_cell(cell)

        self._update_unit_cell()

    # ==================================================
    def _set_gamma(self):
        """
        Set lattice angle, gamma.

        :meta private:
        """
        gamma = self.uc_edit_gamma.text()
        cell = None if gamma == "" else {"gamma": gamma}
        self.pyvista_widget.set_unit_cell(cell)

        self._update_unit_cell()

    # ==================================================
    def _set_clip(self, mode=None):
        """
        Set clip mode.

        Args:
            mode (bool): clip mode.

        Note:
            - if mode is None, default is used.

        :meta private:
        """
        self.pyvista_widget.set_clip(mode)

        self._update_view()

    # ==================================================
    def _set_repeat(self, mode=None):
        """
        Set repeat mode.

        Args:
            mode (bool): repeat mode.

        Note:
            - if mode is None, default is used.

        :meta private:
        """
        self.pyvista_widget.set_repeat(mode)

        self._update_view()

    # ==================================================
    def _set_bar(self, mode=None):
        """
        set bar.

        Args:
            mode (bool): scalar bar mode.

        Note:
            - if mode is None, default is used.

        :meta private:
        """
        self.pyvista_widget.set_bar(mode)

        self._update_view()

    # ==================================================
    def _set_lower(self):
        """
        Set lower bound.

        :meta private:
        """
        lower = self.view_edit_lower.text()
        if lower == "":
            lower = None
        self.pyvista_widget.set_range(lower, None)

        self._update_view()

    # ==================================================
    def _set_upper(self):
        """
        set upper bound.

        :meta private:
        """
        upper = self.view_edit_upper.text()
        if upper == "":
            upper = None
        self.pyvista_widget.set_range(None, upper)

        self._update_view()

    # ==================================================
    def _set_view_default(self):
        """
        set default.

        :meta private:
        """
        if self._is_view_updating:
            return

        self.pyvista_widget.set_view()
        # self._update_view()

    # ==================================================
    def _set_view(self, v, d):
        """
        set view direction.

        :meta private:
        """
        if self._is_view_updating:
            return

        view = [
            int(self.view_combo_a.currentText()),
            int(self.view_combo_b.currentText()),
            int(self.view_combo_c.currentText()),
        ]
        view[d] = int(v)
        self.pyvista_widget.set_view(view)

    # ==================================================
    def _set_parallel(self, mode=None):
        """
        set parallel projection mode.

        Args:
            mode (bool): parallel projection mode.

        Note:
            - if mode is None, default is used.

        :meta private:
        """
        self.pyvista_widget.set_parallel_projection(mode)

        self._update_view()

    # ==================================================
    def _set_grid(self, mode=None):
        """
        set grid mode.

        Args:
            mode (bool): grid mode.

        Note:
            - if mode is None, default is used.

        :meta private:
        """
        self.pyvista_widget.set_grid(mode)

        self._update_view()

    # ==================================================
    def _set_axis_type(self, mode=None):
        """
        set axis type.

        Args:
            mode (str): axis type.

        Note:
            - if mode is None, default is used.

        :meta private:
        """
        self.pyvista_widget.set_axis(mode)

        self._update_view()

    # ==================================================
    def _set_cell_mode(self, mode=None):
        """
        set cell mode.

        Args:
            mode (str): cell mode.

        Note:
            - if mode is None, default is used.

        :meta private:
        """
        self.pyvista_widget.set_cell(mode)

        self._update_view()

    # ==================================================
    def create_connection(self):
        """
        Create connections.

        :meta private:
        """
        # unit cell panel.
        self.uc_combo_crystal.currentTextChanged.connect(self._set_crystal)
        self.uc_edit_origin.returnPressed.connect(self._set_origin)
        self.uc_edit_a.returnPressed.connect(self._set_a)
        self.uc_edit_b.returnPressed.connect(self._set_b)
        self.uc_edit_c.returnPressed.connect(self._set_c)
        self.uc_edit_alpha.returnPressed.connect(self._set_alpha)
        self.uc_edit_beta.returnPressed.connect(self._set_beta)
        self.uc_edit_gamma.returnPressed.connect(self._set_gamma)

        # view panel.
        self.view_button_clip.toggled.connect(self._set_clip)
        self.view_button_repeat.toggled.connect(self._set_repeat)
        self.view_button_nonrepeat.clicked.connect(self._nonrepeat)
        self.view_edit_lower.returnPressed.connect(self._set_lower)
        self.view_edit_upper.returnPressed.connect(self._set_upper)
        self.view_button_bar.toggled.connect(self._set_bar)
        self.view_button_default.clicked.connect(self._set_view_default)
        self.view_button_x.clicked.connect(lambda: self.pyvista_widget.set_view([1, 0, 0]))
        self.view_button_y.clicked.connect(lambda: self.pyvista_widget.set_view([0, 1, 0]))
        self.view_button_z.clicked.connect(lambda: self.pyvista_widget.set_view([0, 0, 1]))
        self.view_button_xm.clicked.connect(lambda: self.pyvista_widget.set_view([-1, 0, 0]))
        self.view_button_ym.clicked.connect(lambda: self.pyvista_widget.set_view([0, -1, 0]))
        self.view_button_zm.clicked.connect(lambda: self.pyvista_widget.set_view([0, 0, -1]))
        self.view_combo_a.currentTextChanged.connect(lambda x: self._set_view(x, 0))
        self.view_combo_b.currentTextChanged.connect(lambda x: self._set_view(x, 1))
        self.view_combo_c.currentTextChanged.connect(lambda x: self._set_view(x, 2))
        self.view_button_parallel.toggled.connect(self._set_parallel)
        self.view_button_grid.toggled.connect(self._set_grid)
        self.view_combo_axis.currentTextChanged.connect(self._set_axis_type)
        self.view_combo_cell.currentTextChanged.connect(self._set_cell_mode)

        # button panel.
        self.ds_button_edit.released.connect(self.pyvista_widget.open_tab_group_view)
        self.misc_button_pref.released.connect(self._show_preference)
        self.misc_button_about.released.connect(self._show_about)
        if check_multipie():
            self.misc_button_multipie.released.connect(self._show_multipie)

        # debug panel.
        if self.debug:
            self.debug_button_camera.released.connect(self._show_camera_info)
            self.debug_button_data.released.connect(self._show_raw_data)
            self.debug_button_actor.released.connect(self._show_actor_list)
            self.debug_button_status.released.connect(self._show_status_data)
            self.debug_button_preference.released.connect(self._show_preference_data)

        # pyvista.
        self.pyvista_widget.message.connect(self.write_info)
        self.pyvista_widget.camera_view.connect(self.set_view_index)

    # ==================================================
    def set_view_index(self, index):
        if index is None or self._is_view_updating:
            return

        new_vals = [str(x) for x in index]
        if [self.view_combo_a.currentText(), self.view_combo_b.currentText(), self.view_combo_c.currentText()] == new_vals:
            return

        self._is_view_updating = True
        self.view_combo_a.blockSignals(True)
        self.view_combo_b.blockSignals(True)
        self.view_combo_c.blockSignals(True)
        try:
            self.view_combo_a.setCurrentText(new_vals[0])
            self.view_combo_b.setCurrentText(new_vals[1])
            self.view_combo_c.setCurrentText(new_vals[2])
        finally:
            self.view_combo_a.blockSignals(False)
            self.view_combo_b.blockSignals(False)
            self.view_combo_c.blockSignals(False)
            self._is_view_updating = False

    # ==================================================
    def _nonrepeat(self):
        """
        Transform data into non-repeat data.

        :meta private:
        """
        ret = QMessageBox.question(
            self,
            "non-repeat",
            "Convert repeated copies into independent objects?\nIt can be undone with Undo.",
            QMessageBox.Ok | QMessageBox.Cancel,
            QMessageBox.Cancel,
        )
        if ret != QMessageBox.Ok:
            return
        with busy_cursor():
            self.pyvista_widget.nonrepeat_data()

    # ==================================================
    def _show_preference(self):
        """
        Show preference panel.

        :meta private:
        """
        self.pyvista_widget.save_current()
        self.pref_dialog = PreferenceDialog(self.pyvista_widget, self)
        status = self.pref_dialog.exec()  # open as modal mode.

        if status != QDialog.Accepted:
            self.pyvista_widget.restore()

        self._update_application()

        if status == QDialog.Accepted:
            self.pyvista_widget.refresh()
            self.pyvista_widget.redraw()

        self._update_panel()

    # ==================================================
    def _show_about(self):
        """
        Show about panel.

        :meta private:
        """
        self.about_dialog = AboutDialog(self.pyvista_widget, self)
        self.about_dialog.exec()  # open as modal mode.

    # ==================================================
    def _show_multipie(self):
        """
        Show MultiPie panel.

        :meta private:
        """
        if check_multipie():
            from qtdraw.multipie.multipie_dialog import MultiPieDialog

            if self.multipie_dialog is None:
                self.multipie_dialog = MultiPieDialog(self)
                self.multipie_dialog.addActions([self.action_undo, self.action_redo])  # shortcuts in the dialog.
            else:
                self.multipie_dialog.show()

    # ==================================================
    def _show_status_data(self):
        """
        Show status data dialog.

        :meta private:
        """
        s = ""
        for key, val in self.pyvista_widget._status.items():
            if key != "plus" and key != "multipie":
                s += f"{key}: {val}\n"

        s += "\n=== multipie ===\n"
        if "version" in self.pyvista_widget._status["multipie"].keys():
            ver = self.pyvista_widget._status["multipie"]["version"]
            s += f"version: {ver}\n"
        for key, val in self.pyvista_widget._status["multipie"].items():
            if key != "plus":
                if key != "version":
                    s += f"--- {key} ---\n"
                    for k, v in val.items():
                        s += f"{k}: {v}\n"

        s += "\n=== plus ===\n"
        for key, val in self.pyvista_widget._status["plus"].items():
            s += f"{key}: {val}\n"

        s += "\n=== multipie.plus ===\n"
        for key, val in self.pyvista_widget._status["multipie"]["plus"].items():
            s += f"{key}: {val}\n"
        s = s[:-1]

        self.status_dialog = LogWidget("Status Data", None)
        self.status_dialog.set_text(s)
        self.status_dialog.show()

    # ==================================================
    def _show_preference_data(self):
        """
        Show preference data dialog.

        :meta private:
        """
        s = ""
        for key, val in self.pyvista_widget._preference.items():
            s += f"=== {key} ===\n"
            for name, v in val.items():
                s += f"{name}: {v}\n"
        s = s[:-1]
        self.pref_data_dialog = LogWidget("Preference Data", None)
        self.pref_data_dialog.set_text(s)
        self.pref_data_dialog.show()

    # ==================================================
    def _show_actor_list(self):
        """
        Show actor list dialog.

        :meta private:
        """
        s = ""
        for i in self.pyvista_widget.actor_list:
            s += i + "\n"
        s = s[:-1]
        self.actor_dialog = LogWidget("Actor Data", None)
        self.actor_dialog.set_text(s)
        self.actor_dialog.show()

    # ==================================================
    def _show_raw_data(self):
        """
        Show raw data dialog.

        :meta private:
        """
        s = ""
        for object_type, model in self.pyvista_widget._data.items():
            s += f"=== {object_type} ===\n"
            data = model.tolist()
            for row in data:
                s += str(row) + "\n"
        s = s[:-1]
        self.data_dialog = LogWidget("Raw Data", None)
        self.data_dialog.set_text(s)
        self.data_dialog.show()

    # ==================================================
    def _show_camera_info(self):
        """
        Show camera info. dialog.

        :meta private:
        """
        camera = self.pyvista_widget.get_camera_info()
        s = ""
        for key, val in camera.items():
            s += f"{key}: {val}\n"
        s = s[:-1]
        self.camera_dialog = LogWidget("Camera Info", None)
        self.camera_dialog.set_text(s)
        self.camera_dialog.show()

    # ==================================================
    def _clear_data(self):
        """
        Clear data (actor and data).

        :meta private:
        """
        self._commit_pending_input()
        if self.is_modified():
            if self._confirm_unsaved("clearing"):
                self.clear_data()
            return
        ret = QMessageBox.question(self, "", "Are you sure ?", QMessageBox.Cancel, QMessageBox.Ok)
        if ret == QMessageBox.Ok:
            self.clear_data()

    # ==================================================
    def clear_data(self):
        """
        Clear data (actor and data).
        """
        self.pyvista_widget.clear_data()
        self._update_panel()
        if self.multipie_dialog is not None:
            self.multipie_dialog.clear_data()

    # ==================================================
    def exec(self):
        """
        Execute QtDraw.

        :meta private:
        """
        self.app.exec()

    # ==================================================
    def closeEvent(self, event):
        """
        Close with dialog.

        Args:
            event (Event): event.

        :meta private:
        """
        self._commit_pending_input()
        ok = self._confirm_unsaved("closing", always=True)
        if not ok:
            event.ignore()
        else:
            dialogs = [self.multipie_dialog, self.logger, self.info_dialog]
            if self.debug:
                dialogs += [self.actor_dialog, self.data_dialog, self.status_dialog, self.pref_data_dialog, self.camera_dialog]
            dialogs = [dialog for dialog in dialogs if dialog is not None]

            # delete closed windows, otherwise they remain and slow down new windows.
            # scheduled first, so that a failing step below cannot skip it.
            for dialog in dialogs:
                dialog.deleteLater()
            self.deleteLater()
            # keep the VTK widget, as a closed standalone PyVistaWidget: deleting it together
            # with the window occasionally corrupts memory with Mesa on Linux.
            self.pyvista_widget.setParent(None)

            try:
                for dialog in dialogs:
                    dialog.close()
                self.pyvista_widget.close()
            finally:
                super().closeEvent(event)

    # ==================================================
    def update_status(self, key, value):
        """
        Update status.

        Args:
            key (str): status key.
            value (Any): value.

        :meta private:
        """
        self.pyvista_widget.update_status(key, value)
        self._update_panel()

    # ==================================================
    def update_preference(self, category, key, value):
        """
        Update preference.

        Args:
            category (str): category.
            key (str): status key.
            value (Any): value.

        :meta private:
        """
        self.pyvista_widget.update_preference(category, key, value)
        self._update_panel()

    # ==================================================
    def write_info(self, text):
        """
        Write text message into Info dialog.

        Args:
            text (str): message.

        :meta private:
        """
        self.info_dialog.append_text(text)

    # ==================================================
    def add_site(self, size=None, color=None, opacity=None, position=None, cell=None, name=None, label=None, margin=None):
        """
        Add site.

        Args:
            size (float, optional): site size. (default: 0.1)
            color (str, optional): site color. (default: darkseagreen)
            opacity (float, optional): opacity, [0,1]. (default: 1.0)
            position (str, optional): position in cell, [x,y,z]. (default: [0,0,0])
            cell (str, optional): cell, [nx,ny,nz]. (default: [0,0,0])
            name (str, optional): name of group. (default: untitled)
            label (str, optional): label. (default: label)
            margin (int, optional): label margin. (default: 3)

        Note:
            - if keyword is None, default value is used.
        """
        self.pyvista_widget.add_site(size, color, opacity, position, cell, name, label, margin)

    # ==================================================
    def add_bond(
        self,
        direction=None,
        width=None,
        color=None,
        color2=None,
        cartesian=None,
        opacity=None,
        position=None,
        cell=None,
        name=None,
        label=None,
        margin=None,
    ):
        """
        Add bond.

        Args:
            direction (str, optional): bond direction. (default: [0,0,1])
            width (float, optional): bond width. (default: 0.02)
            color (str, optional): bond color (tail side). (default: silver)
            color2 (str, optional): bond color (head side). (default: silver)
            cartesian (bool, optional): cartesian coordinate for direction ? (default: False)
            opacity (float, optional): opacity, [0,1]. (default: 1.0)
            position (str, optional): position in cell, [x,y,z]. (default: [0,0,0])
            cell (str, optional): cell, [nx,ny,nz]. (default: [0,0,0])
            name (str, optional): name of group. (default: untitled)
            label (str, optional): label. (default: label)
            margin (int, optional): label margin. (default: 3)

        Note:
            - if keyword is None, default value is used.
            - bond position is at center.
        """
        self.pyvista_widget.add_bond(direction, width, color, color2, cartesian, opacity, position, cell, name, label, margin)

    # ==================================================
    def add_vector(
        self,
        direction=None,
        length=None,
        width=None,
        offset=None,
        color=None,
        cartesian=None,
        shaft_R=None,
        tip_R=None,
        tip_length=None,
        opacity=None,
        position=None,
        cell=None,
        name=None,
        label=None,
        margin=None,
    ):
        """
        Add vector.

        Args:
            direction (str, optional): vector direction. (default: [0,0,1])
            length (float, optional): vector length. (default: 1.0)
            width (float, optional): vector width. (default: 0.02)
            offset (float, optional): vector offset. (default: -0.43)
            color (str, optional): vector color. (default: orange)
            cartesian (bool, optional): cartesian coordinate for direction ? (default: True)
            shaft_R (float, optional): shaft radius. (default: 1.0)
            tip_R (float, optional): tip radius. (default: 2.0)
            tip_length (float, optional): tip length. (default: 0.25)
            opacity (float, optional): opacity, [0,1]. (default: 1.0)
            position (str, optional): position in cell, [x,y,z]. (default: [0,0,0])
            cell (str, optional): cell, [nx,ny,nz]. (default: [0,0,0])
            name (str, optional): name of group. (default: untitled)
            label (str, optional): label. (default: label)
            margin (int, optional): label margin. (default: 3)

        Note:
            - if keyword is None, default value is used.
            - if length is negative, norm of direction multiplied by |length| is used.
        """
        self.pyvista_widget.add_vector(
            direction,
            length,
            width,
            offset,
            color,
            cartesian,
            shaft_R,
            tip_R,
            tip_length,
            opacity,
            position,
            cell,
            name,
            label,
            margin,
        )

    # ==================================================
    def add_orbital(
        self,
        shape=None,
        surface=None,
        size=None,
        range=None,
        color=None,
        opacity=None,
        position=None,
        cell=None,
        name=None,
        label=None,
        margin=None,
    ):
        """
        Add orbital.

        Args:
            shape (str, optional): orbital shape polynomial in terms of (x,y,z,r). (default: 3z**2-r**2)
            surface (str, optional): orbital colormap polynomial in terms of (x,y,z,r). (default: "")
            size (float, optional): orbital size. (default: 0.5)
            range (list, optional): plot range of [th,phi]. (default: [[0,180],[0,360]])
            color (str, optional): orbital color or colormap. (default: Wistia)
            opacity (float, optional): opacity, [0,1]. (default: 1.0)
            position (str, optional): position in cell, [x,y,z]. (default: [0,0,0])
            cell (str, optional): cell, [nx,ny,nz]. (default: [0,0,0])
            name (str, optional): name of group. (default: untitled)
            label (str, optional): label. (default: label)
            margin (int, optional): label margin. (default: 3)

        Note:
            - if keyword is None, default value is used.
            - if surface is "", the same one of shape is used.
            - if size is positive, max. value is equivalent to size.
            - if size is negative, abs. value is scaled by size.
        """
        self.pyvista_widget.add_orbital(shape, surface, size, range, color, opacity, position, cell, name, label, margin)

    # ==================================================
    def add_stream(
        self,
        shape=None,
        vector=None,
        size=None,
        range=None,
        division=None,
        length=None,
        width=None,
        offset=None,
        abs_scale=None,
        color=None,
        component=None,
        shaft_R=None,
        tip_R=None,
        tip_length=None,
        opacity=None,
        position=None,
        cell=None,
        name=None,
        label=None,
        margin=None,
    ):
        """
        Add stream.

        Args:
            shape (str, optional): shape polynomial on which stream put. (default: 1)
            vector (str, optional): stream polynomials for [x,y,z] components. (default: [x,y,z])
            size (float, optional): shape size. (default: 0.5)
            range (list, optional): plot range of [th,phi]. (default: [[0,180],[0,360]])
            division (list, optional): division of stream of [th,phi]. (default: [9,18])
            length (float, optional): stream arrow size. (default: 0.1)
            width (float, optional): stream arrow width. (default: 0.01)
            offset (float, optional): stream arrow offset. (default: -0.43)
            abs_scale (bool, optional): stream arrow scaled ? (default: False)
            color (str, optional): stream arrow color or colormap. (default: coolwarm)
            component (str, optional): use component or abs, "x/y/z/abs". (default: abs)
            shaft_R (float, optional): shaft radius. (default: 1.0)
            tip_R (float, optional): tip radius. (default: 2.0)
            tip_length (float, optional): tip length. (default: 0.25)
            opacity (float, optional): opacity, [0,1]. (default: 1.0)
            position (str, optional): position in cell, [x,y,z]. (default: [0,0,0])
            cell (str, optional): cell, [nx,ny,nz]. (default: [0,0,0])
            name (str, optional): name of group. (default: untitled)
            label (str, optional): label. (default: label)
            margin (int, optional): label margin. (default: 3)

        Note:
            - if keyword is None, default value is used.
            - if size is negative, shape is normalized.
        """
        self.pyvista_widget.add_stream(
            shape,
            vector,
            size,
            range,
            division,
            length,
            width,
            offset,
            abs_scale,
            color,
            component,
            shaft_R,
            tip_R,
            tip_length,
            opacity,
            position,
            cell,
            name,
            label,
            margin,
        )

    # ==================================================
    def add_line(
        self,
        direction=None,
        width=None,
        arrow1=None,
        arrow2=None,
        tip_R=None,
        tip_length=None,
        color=None,
        cartesian=None,
        opacity=None,
        position=None,
        cell=None,
        name=None,
        label=None,
        margin=None,
    ):
        """
        Add line.

        Args:
            direction (str, optional): line direction. (default: [0,0,1])
            width (float, optional): line width. (default: 0.02)
            arrow1 (bool, optional): arrow (tail side) ? (default: False)
            arrow2 (bool, optional): arrow (head side) ? (default: False)
            tip_R (float, optional): arrow tip radius. (default: 2.0)
            tip_length (float, optional): arrow tip length. (default: 0.1)
            color (str, optional): line color. (default: strawberry)
            cartesian (bool, optional): cartesian coordinate for direction ? (default: False)
            opacity (float, optional): opacity, [0,1]. (default: 1.0)
            position (str, optional): position in cell, [x,y,z]. (default: [0,0,0])
            cell (str, optional): cell, [nx,ny,nz]. (default: [0,0,0])
            name (str, optional): name of group. (default: untitled)
            label (str, optional): label. (default: label)
            margin (int, optional): label margin. (default: 3)

        Note:
            - if keyword is None, default value is used.
        """
        self.pyvista_widget.add_line(
            direction, width, arrow1, arrow2, tip_R, tip_length, color, cartesian, opacity, position, cell, name, label, margin
        )

    # ==================================================
    def add_plane(
        self,
        normal=None,
        x_size=None,
        y_size=None,
        color=None,
        width=None,
        grid=None,
        grid_color=None,
        cartesian=None,
        opacity=None,
        position=None,
        cell=None,
        name=None,
        label=None,
        margin=None,
    ):
        """
        Add plane.

        Args:
            normal (str, optional): plane normal vector. (default: [0,0,1])
            x_size (float, optional): plane x size. (default: 1.0)
            y_size (float, optional): plane y size. (default: 1.0)
            color (str, optional): plane color. (default: sky)
            width (float, optional): plane grid width. (default: 2.0)
            grid (bool, optional): grid ? (default: False)
            grid_color (str, optional): grid color. (default: black)
            cartesian (bool, optional): cartesian coordinate for normal ? (default: True)
            opacity (float, optional): opacity, [0,1]. (default: 1.0)
            position (str, optional): position in cell, [x,y,z]. (default: [0,0,0])
            cell (str, optional): cell, [nx,ny,nz]. (default: [0,0,0])
            name (str, optional): name of group. (default: untitled)
            label (str, optional): label. (default: label)
            margin (int, optional): label margin. (default: 3)

        Note:
            - if keyword is None, default value is used.
        """
        self.pyvista_widget.add_plane(
            normal, x_size, y_size, color, width, grid, grid_color, cartesian, opacity, position, cell, name, label, margin
        )

    # ==================================================
    def add_circle(
        self,
        normal=None,
        size=None,
        color=None,
        width=None,
        edge=None,
        edge_color=None,
        cartesian=None,
        opacity=None,
        position=None,
        cell=None,
        name=None,
        label=None,
        margin=None,
    ):
        """
        Add circle.

        Args:
            normal (str, optional): circle normal vector. (default: [0,0,1])
            size (float, optional): circle size. (default: 0.5)
            color (str, optional): circle color. (default: salmon)
            width (float, optional): edge width. (default: 2.0)
            edge (bool, optional): edge ? (default: True)
            edge_color (str, optional): edge color. (default: black)
            cartesian (bool, optional): cartesian coordinate for normal ? (default: True)
            opacity (float, optional): opacity, [0,1]. (default: 1.0)
            position (str, optional): position in cell, [x,y,z]. (default: [0,0,0])
            cell (str, optional): cell, [nx,ny,nz]. (default: [0,0,0])
            name (str, optional): name of group. (default: untitled)
            label (str, optional): label. (default: label)
            margin (int, optional): label margin. (default: 3)

        Note:
            - if keyword is None, default value is used.
        """
        self.pyvista_widget.add_circle(
            normal, size, color, width, edge, edge_color, cartesian, opacity, position, cell, name, label, margin
        )

    # ==================================================
    def add_torus(
        self,
        normal=None,
        size=None,
        width=None,
        color=None,
        cartesian=None,
        opacity=None,
        position=None,
        cell=None,
        name=None,
        label=None,
        margin=None,
    ):
        """
        Add torus.

        Args:
            normal (str, optional): torus normal vector. (default: [0,0,1])
            size (float, optional): torus size. (default: 0.5)
            width (float, optional): torus width. (default: 0.15)
            color (str, optional): torus color. (default: cantaloupe)
            cartesian (bool, optional): cartesian coordinate for normal ? (default: True)
            opacity (float, optional): opacity, [0,1]. (default: 1.0)
            position (str, optional): position in cell, [x,y,z]. (default: [0,0,0])
            cell (str, optional): cell, [nx,ny,nz]. (default: [0,0,0])
            name (str, optional): name of group. (default: untitled)
            label (str, optional): label. (default: label)
            margin (int, optional): label margin. (default: 3)

        Note:
            - if keyword is None, default value is used.
        """
        self.pyvista_widget.add_torus(normal, size, width, color, cartesian, opacity, position, cell, name, label, margin)

    # ==================================================
    def add_ellipsoid(
        self,
        normal=None,
        x_size=None,
        y_size=None,
        z_size=None,
        color=None,
        cartesian=None,
        opacity=None,
        position=None,
        cell=None,
        name=None,
        label=None,
        margin=None,
    ):
        """
        Add ellipsoid.

        Args:
            normal (str, optional): ellipsoid normal vector. (default: [0,0,1])
            x_size (float, optional): ellipsoid x size. (default: 0.5)
            y_size (float, optional): ellipsoid y size. (default: 0.4)
            z_size (float, optional): ellipsoid z size. (default: 0.3)
            color (str, optional): ellipsoid color. (default: cornflowerblue)
            cartesian (bool, optional): cartesian coordinate for normal ? (default: True)
            opacity (float, optional): opacity, [0,1]. (default: 1.0)
            position (str, optional): position in cell, [x,y,z]. (default: [0,0,0])
            cell (str, optional): cell, [nx,ny,nz]. (default: [0,0,0])
            name (str, optional): name of group. (default: untitled)
            label (str, optional): label. (default: label)
            margin (int, optional): label margin. (default: 3)

        Note:
            - if keyword is None, default value is used.
        """
        self.pyvista_widget.add_ellipsoid(
            normal, x_size, y_size, z_size, color, cartesian, opacity, position, cell, name, label, margin
        )

    # ==================================================
    def add_toroid(
        self,
        normal=None,
        size=None,
        width=None,
        x_scale=None,
        y_scale=None,
        z_scale=None,
        ring_shape=None,
        tube_shape=None,
        color=None,
        cartesian=None,
        opacity=None,
        position=None,
        cell=None,
        name=None,
        label=None,
        margin=None,
    ):
        """
        Add toroid.

        Args:
            normal (str, optional): toroid normal vector. (default: [0,0,1])
            size (float, optional): toroid size. (default: 0.5)
            width (float, optional): toroid width. (default: 0.15)
            x_scale (float, optional): toroid x scale. (default: 1.0)
            y_scale (float, optional): toroid y scale. (default: 1.0)
            z_scale (float, optional): toroid z scale. (default: 1.0)
            ring_shape (float, optional): toroid ring shape. (default: 0.3)
            tube_shape (float, optional): toroid tube shape. (default: 0.3)
            color (str, optional): toroid color. (default: tan)
            cartesian (bool, optional): cartesian coordinate for normal ? (default: True)
            opacity (float, optional): opacity, [0,1]. (default: 1.0)
            position (str, optional): position in cell, [x,y,z]. (default: [0,0,0])
            cell (str, optional): cell, [nx,ny,nz]. (default: [0,0,0])
            name (str, optional): name of group. (default: untitled)
            label (str, optional): label. (default: label)
            margin (int, optional): label margin. (default: 3)

        Note:
            - if keyword is None, default value is used.
        """
        self.pyvista_widget.add_toroid(
            normal,
            size,
            width,
            x_scale,
            y_scale,
            z_scale,
            ring_shape,
            tube_shape,
            color,
            cartesian,
            opacity,
            position,
            cell,
            name,
            label,
            margin,
        )

    # ==================================================
    def add_box(
        self,
        a1=None,
        a2=None,
        a3=None,
        width=None,
        edge=None,
        edge_color=None,
        wireframe=None,
        color=None,
        cartesian=None,
        opacity=None,
        position=None,
        cell=None,
        name=None,
        label=None,
        margin=None,
    ):
        """
        Add box.

        Args:
            a1 (str, optional): box a1 vector. (default: [1,0,0])
            a2 (str, optional): box a2 vector. (default: [0,1,0])
            a3 (str, optional): box a3 vector. (default: [0,0,1])
            width (float, optional): edge width. (default: 2.0)
            edge (bool, optional): edge ? (default: True)
            edge_color (str, optional): edge color. (default: black)
            wireframe (bool, optional): wireframe ? (default: False)
            color (str, optional): box color. (default: yellowgreen)
            cartesian (bool, optional): cartesian coordinate for shape ? (default: False)
            opacity (float, optional): opacity, [0,1]. (default: 1.0)
            position (str, optional): position in cell, [x,y,z]. (default: [0,0,0])
            cell (str, optional): cell, [nx,ny,nz]. (default: [0,0,0])
            name (str, optional): name of group. (default: untitled)
            label (str, optional): label. (default: label)
            margin (int, optional): label margin. (default: 3)

        Note:
            - if keyword is None, default value is used.
        """
        self.pyvista_widget.add_box(
            a1, a2, a3, width, edge, edge_color, wireframe, color, cartesian, opacity, position, cell, name, label, margin
        )

    # ==================================================
    def add_polygon(
        self,
        point=None,
        connectivity=None,
        width=None,
        edge=None,
        edge_color=None,
        wireframe=None,
        color=None,
        cartesian=None,
        opacity=None,
        position=None,
        cell=None,
        name=None,
        label=None,
        margin=None,
    ):
        """
        Add polygon.

        Args:
            point (str, optional): polygon vertex points. (default: [[0,0,0],[0.8,0,0],[0,0.6,0],[0,0,0.4],[0.6,0.6,0]])
            connectivity (str, optional): connectivity. (default: [[0,1,4,2],[0,1,3],[1,4,3],[2,0,3],[2,3,4]])
            width (float, optional): edge width. (default: 2.0)
            edge (bool, optional): edge ? (default: True)
            edge_color (str, optional): edge color. (default: black)
            wireframe (bool, optional): wireframe ? (default: False)
            color (str, optional): polygon color. (default: aluminum)
            cartesian (bool, optional): cartesian coordinate for shape ? (default: False)
            opacity (float, optional): opacity, [0,1]. (default: 1.0)
            position (str, optional): position in cell, [x,y,z]. (default: [0,0,0])
            cell (str, optional): cell, [nx,ny,nz]. (default: [0,0,0])
            name (str, optional): name of group. (default: untitled)
            label (str, optional): label. (default: label)
            margin (int, optional): label margin. (default: 3)

        Note:
            - if keyword is None, default value is used.
        """
        self.pyvista_widget.add_polygon(
            point,
            connectivity,
            width,
            edge,
            edge_color,
            wireframe,
            color,
            cartesian,
            opacity,
            position,
            cell,
            name,
            label,
            margin,
        )

    # ==================================================
    def add_spline(
        self,
        point=None,
        width=None,
        n_interp=None,
        closed=None,
        natural=None,
        arrow1=None,
        arrow2=None,
        tip_R=None,
        tip_length=None,
        color=None,
        cartesian=None,
        opacity=None,
        position=None,
        cell=None,
        name=None,
        label=None,
        margin=None,
    ):
        """
        Add spline.

        Args:
            point (str, optional): spline vertex points. (default: [[0,0,0],[1,0,1],[0,1,2]])
            width (float, optional): spline width. (default: 0.01)
            n_interp (int, optional): spline interpolation points. (default: 500)
            closed (bool, optional): closed curve ? (default: False)
            natural (bool, optional): natural edge ? (default: True)
            arrow1 (bool, optional): arrow (tail side) ? (default: False)
            arrow2 (bool, optional): arrow (head side) ? (default: False)
            tip_R (float, optional): arrow tip radius. (default: 2.0)
            tip_length (float, optional): arrow tip length. (default: 0.1)
            color (str, optional): spline color. (default: banana)
            cartesian (bool, optional): cartesian coordinate for point ? (default: True)
            opacity (float, optional): opacity, [0,1]. (default: 1.0)
            position (str, optional): position in cell, [x,y,z]. (default: [0,0,0])
            cell (str, optional): cell, [nx,ny,nz]. (default: [0,0,0])
            name (str, optional): name of group. (default: untitled)
            label (str, optional): label. (default: label)
            margin (int, optional): label margin. (default: 3)

        Note:
            - if keyword is None, default value is used.
        """
        self.pyvista_widget.add_spline(
            point,
            width,
            n_interp,
            closed,
            natural,
            arrow1,
            arrow2,
            tip_R,
            tip_length,
            color,
            cartesian,
            opacity,
            position,
            cell,
            name,
            label,
            margin,
        )

    # ==================================================
    def add_spline_t(
        self,
        point=None,
        t_range=None,
        width=None,
        n_interp=None,
        closed=None,
        natural=None,
        arrow1=None,
        arrow2=None,
        tip_R=None,
        tip_length=None,
        color=None,
        cartesian=None,
        opacity=None,
        position=None,
        cell=None,
        name=None,
        label=None,
        margin=None,
    ):
        """
        Add spline (parametric).

        Args:
            point (str, optional): spline function vector in terms of t. (default: [cos(2 pi t), sin(2 pi t), t/2])
            t_range (str, optional): spline t range [t0,t1,dt]. (default: [0,1,0.05])
            width (float, optional): spline width. (default: 0.01)
            n_interp (int, optional): spline interpolation points. (default: 500)
            closed (bool, optional): closed curve ? (default: False)
            natural (bool, optional): natural edge ? (default: True)
            arrow1 (bool, optional): arrow (tail side) ? (default: False)
            arrow2 (bool, optional): arrow (head side) ? (default: False)
            tip_R (float, optional): arrow tip radius. (default: 2.0)
            tip_length (float, optional): arrow tip length. (default: 0.1)
            color (str, optional): splline color. (default: crimson)
            cartesian (bool, optional): cartesian coordinate for point ? (default: True)
            opacity (float, optional): opacity, [0,1]. (default: 1.0)
            position (str, optional): position in cell, [x,y,z]. (default: [0,0,0])
            cell (str, optional): cell, [nx,ny,nz]. (default: [0,0,0])
            name (str, optional): name of group. (default: untitled)
            label (str, optional): label. (default: label)
            margin (int, optional): label margin. (default: 3)

        Note:
            - if keyword is None, default value is used.
        """
        self.pyvista_widget.add_spline_t(
            point,
            t_range,
            width,
            n_interp,
            closed,
            natural,
            arrow1,
            arrow2,
            tip_R,
            tip_length,
            color,
            cartesian,
            opacity,
            position,
            cell,
            name,
            label,
            margin,
        )

    # ==================================================
    def add_text3d(
        self,
        text=None,
        size=None,
        view=None,
        depth=None,
        offset=None,
        color=None,
        opacity=None,
        position=None,
        cell=None,
        name=None,
        label=None,
        margin=None,
    ):
        """
        Add text 3d.

        Args:
            text (str, optional): text. (default: text)
            size (float, optional): text size. (default: 0.3)
            view (str, optional): text viewpoint. (default: [0,0,1])
            depth (float, optional): text depth. (default: 0.2)
            offset (str, optional): text offset. (default: [0,0,0])
            color (str, optional): text color. (default: iron)
            opacity (float, optional): opacity, [0,1]. (default: 1.0)
            position (str, optional): position in cell, [x,y,z]. (default: [0,0,0])
            cell (str, optional): cell, [nx,ny,nz]. (default: [0,0,0])
            name (str, optional): name of group. (default: untitled)
            label (str, optional): label. (default: label)
            margin (int, optional): label margin. (default: 3)

        Note:
            - if keyword is None, default value is used.
        """
        self.pyvista_widget.add_text3d(text, size, view, depth, offset, color, opacity, position, cell, name, label, margin)

    # ==================================================
    def add_isosurface(
        self,
        data=None,
        value=None,
        surface=None,
        color=None,
        color_range=None,
        opacity=None,
        position=None,
        cell=None,
        name=None,
        label=None,
        margin=None,
    ):
        """
        Add isosurface.

        Args:
            data (str, optional): data (file) name for grid data. (default: "")
            value (str, optional): isosurface values. (default: [0.5])
            surface (str, optional): surface value name. (default: "")
            color (str, optional): text color. (default: white)
            color_range (str, optional): color range. (default: [0,1])
            opacity (float, optional): opacity, [0,1]. (default: 0.8)
            position (str, optional): position in cell, [x,y,z]. (default: [0,0,0])
            cell (str, optional): cell, [nx,ny,nz]. (default: [0,0,0])
            name (str, optional): name of group. (default: untitled)
            label (str, optional): label. (default: label)
            margin (int, optional): label margin. (default: 3)

        Note:
            - if keyword is None, default value is used.
            - if filename is tuple, (name, dict), use dict data as name.
        """
        self.pyvista_widget.add_isosurface(data, value, surface, color, color_range, opacity, position, cell, name, label, margin)

    # ==================================================
    def add_caption(self, caption=None, size=None, bold=None, color=None, position=None, cell=None, name=None, margin=None):
        """
        Add caption.

        Args:
            caption (str, optional): caption list. (default: [A,B,C])
            size (int, optional): caption size. (default: 18)
            bold (bool, optional): bold ? (default: True)
            color (str, optional): caption color. (default: black)
            position (str, optional): position of each caption. (default: [[0,0,0],[1,0,0],[1,1,0]])
            cell (str, optional): cell. (default: [0,0,0])
            name (str, optional): name of group. (default: untitled)
            margin (int, optional): label margin. (default: 3)

        Note:
            - if keyword is None, default value is used.
        """
        self.pyvista_widget.add_caption(caption, size, bold, color, position, cell, name, margin)

    # ==================================================
    def add_text2d(self, caption=None, size=None, color=None, font=None, position=None, name=None):
        """
        Add text 2d.

        Args:
            caption (str, optional): caption. (default: text)
            size (int, optional): caption size. (default: 8)
            color (str, optional): caption color. (default: black)
            font (str, optional): caption font. (default: arial)
            position (str, optional): position in cell, [x,y,z]. (default: [0,0,0])
            name (str, optional): name of group. (default: untitled)

        Note:
            - if keyword is None, default value is used.
        """
        self.pyvista_widget.add_text2d(caption, size, color, font, position, name)

    # ==================================================
    def plot_orbital_from_data(
        self,
        name,
        shape,
        surface=None,
        size=1.0,
        point_size=0.03,
        spherical_plot=False,
        color="coolwarm",
        opacity=1.0,
        position=None,
    ):
        """
        Plot orbital from data.

        Args:
            name (str): plot name.
            shape (ndarray): (x,y,z) orbital shape.
            surface (ndarray, optional): (x,y,z) orbital colormap.
            size (float, optional): orbital size.
            point_size(float, optional): point size.
            spherical_plot (bool, optional): spherical-like plot ?
            color (str, optional): orbital color or colormap.
            opacity (float, optional): opacity, [0,1].
            position (ndarray): position (transformed).

        Note:
            - if surface is None, the same one of shape is used.
            - if size is positive, max. value is equivalent to size.
            - if size is negative, abs. value is scaled by size.
            - if point_size is None, no point is shown.
            - to remove object, use remove_actor(name).
        """
        self.pyvista_widget.plot_orbital_from_data(
            name, shape, surface, size, point_size, spherical_plot, color, opacity, position
        )

    # ==================================================
    def plot_stream_from_data(
        self,
        name,
        vector,
        shape,
        surface=None,
        size=1.0,
        length=0.2,
        width=0.01,
        offset=-0.43,
        abs_scale=False,
        color="coolwarm",
        component="abs",
        spherical_plot=False,
        shaft_R=1.0,
        tip_R=2.0,
        tip_length=0.25,
        opacity=1.0,
        position=None,
    ):
        """
        Plot stream from data (vectors in cartesian coordinate).

        Args:
            name (str): object name.
            vector (ndarray): stream vector [vx(x,y,z),vy(x,y,z),vz(x,y,z)] (cartesina).
            shape (ndarray): f(x,y,z) shape on which stream put (cartesian).
            surface (ndarray, optional): (x,y,z) orbital colormap.
            size (float, optional): shape size.
            length (float, optional): stream arrow size.
            width (float, optional): stream arrow width.
            offset (float, optional): stream arrow offest.
            abs_scale (bool, optional): stream arrow scaled ?
            color (str, optional): stream arrow color or colormap.
            component (str, optional): use component or abs, "x/y/z/abs".
            spherical_plot (bool, optional): spherical-like plot ?
            shaft_R (float, optional) :shaft radius.
            tip_R (float, optional): tip radius.
            tip_length (float, optional): tip length.
            opacity (float, optional): opacity, [0,1].
            position (ndarray): position (transformed).

        Note:
            - if size is negative, shape is normalized.
            - to remove object, use remove_actor(name).
        """
        self.pyvista_widget.plot_stream_from_data(
            name,
            vector,
            shape,
            surface,
            size,
            length,
            width,
            offset,
            abs_scale,
            color,
            component,
            spherical_plot,
            shaft_R,
            tip_R,
            tip_length,
            opacity,
            position,
        )

    # ==================================================
    def set_model(self, name=None):
        """
        Set model name.

        Args:
            name (str, optional): model name.

        Note:
            - if name is None, default is used.
        """
        self.pyvista_widget.set_model(name)
        self._update_title()

    # ==================================================
    def set_unit_cell(self, cell=None):
        """
        Set unit cell.

        Args:
            cell (dict, optional): unit cell, {a, b, c, alpha, beta, gamma}.

        Note:
            - if cell is None, default is used.
            - set cell.
        """
        view = self.pyvista_widget._status["view"]
        self.pyvista_widget.set_unit_cell(cell)
        self._update_unit_cell()
        self._update_view()
        self.set_view(view)

    # ==================================================
    def set_crystal(self, crystal=None):
        """
        Set crystal.

        Args:
            crystal (str, optional): crystal, "triclinic/monoclinic/orthorhombic/tetragonal/trigonal/hexagonal/cubic".

        Note:
            - if crystal is None, default is used.
            - set unit cell.
        """
        view = self.pyvista_widget._status["view"]
        self.pyvista_widget.set_crystal(crystal)
        self._update_view()
        self.set_view(view)

    # ==================================================
    def set_origin(self, origin=None):
        """
        Set origin.

        Args:
            origin (list or str, optional): origin.

        Note:
            - if origin is None, default is used.
            - set cell.
        """
        view = self.pyvista_widget._status["view"]
        self.pyvista_widget.set_origin(origin)
        self._update_view()
        self.set_view(view)

    # ==================================================
    def set_clip(self, mode=None):
        """
        Set clip mode.

        Args:
            mode (bool, optional): clip object ?

        Note:
            - if mode is None, default is used.
        """
        self._set_clip(mode)

    # ==================================================
    def set_repeat(self, mode=None):
        """
        Set repeat mode.

        Args:
            mode (bool, optional): repeat mode.

        Note:
            - if mode is None, default is used.
            - repeat data.
        """
        self._set_repeat(mode)

    # ==================================================
    def set_nonrepeat(self):
        """
        Transform data to non-repeat data.
        """
        self.pyvista_widget.nonrepeat_data()

    # ==================================================
    def set_range(self, lower=None, upper=None):
        """
        Set cell range.

        Args:
            lower (list or str, optional): lower bound, [float].
            upper (list or str, optional): upper bound, [float].

        Note:
            - if lower/upper is None, default is used.
            - set cell.
        """
        view = self.pyvista_widget._status["view"]
        self.pyvista_widget.set_range(lower, upper)
        self._update_view()
        self.set_view(view)

    # ==================================================
    def set_view(self, view=None):
        """
        Set view point.

        Args:
            view (list or str, optional): view indices of [a1,a2,a3], [int].

        Note:
            - if view is None, default is used.
        """
        if view is None:
            self._set_view_default()
            return

        if type(view) == str:
            view = view.strip("[]").split(",")
        self.pyvista_widget.set_view(view)

    # ==================================================
    def set_parallel_projection(self, mode=None):
        """
        Set parallel projection mode.

        Args:
            mode (bool, optional): use parallel projection ?

        Note:
            - if mode is None, default is used.
        """
        view = self.pyvista_widget._status["view"]
        self._set_parallel(mode)
        self.set_view(view)

    # ==================================================
    def set_grid(self, mode=None):
        """
        Set grid mode.

        Args:
            mode (bool, optional): use grid ?

        Note:
            - if mode is None, default is used.
        """
        self._set_grid(mode)

    # ==================================================
    def set_bar(self, mode=None):
        """
        Set scalar bar mode.

        Args:
            mode (bool, optional): show scalar bar ?

        Note:
            - if mode is None, default is used.
        """
        self._set_bar(mode)

    # ==================================================
    def set_axis(self, axis_type=None):
        """
        Set axis widget.

        Args:
            axis_type (str, optional): axis type, "on/axis/full/off".

        Note:
            - if axis_type is None, default is used.
        """
        self._set_axis_type(axis_type)

    # ==================================================
    def set_cell(self, mode=None):
        """
        Set unit cell.

        Args:
            mode (str, optional): mode "single/all/off.

        Note:
            - if mode is None, default is used.
        """
        self._set_cell_mode(mode)

    # ==================================================
    def add_mesh(
        self,
        mesh,
        color=None,
        style=None,
        scalars=None,
        clim=None,
        show_edges=None,
        edge_color=None,
        point_size=None,
        line_width=None,
        opacity=None,
        flip_scalars=False,
        lighting=None,
        n_colors=256,
        interpolate_before_map=None,
        cmap=None,
        label=None,
        reset_camera=None,
        scalar_bar_args=None,
        show_scalar_bar=None,
        multi_colors=False,
        name=None,
        texture=None,
        render_points_as_spheres=None,
        render_lines_as_tubes=None,
        smooth_shading=None,
        split_sharp_edges=None,
        ambient=None,
        diffuse=None,
        specular=None,
        specular_power=None,
        nan_color=None,
        nan_opacity=1.0,
        culling=None,
        rgb=None,
        categories=False,
        silhouette=None,
        use_transparency=False,
        below_color=None,
        above_color=None,
        annotations=None,
        pickable=True,
        preference="point",
        log_scale=False,
        pbr=None,
        metallic=None,
        roughness=None,
        render=True,
        user_matrix=None,
        component=None,
        emissive=None,
        copy_mesh=False,
        backface_params=None,
        show_vertices=None,
        edge_opacity=None,
        **kwargs,
    ):
        """
        Add any PyVista/VTK mesh or dataset that PyVista can wrap to the scene.

        See PyVista manual.
        """
        self.pyvista_widget.add_mesh(
            mesh,
            color,
            style,
            scalars,
            clim,
            show_edges,
            edge_color,
            point_size,
            line_width,
            opacity,
            flip_scalars,
            lighting,
            n_colors,
            interpolate_before_map,
            cmap,
            label,
            reset_camera,
            scalar_bar_args,
            show_scalar_bar,
            multi_colors,
            name,
            texture,
            render_points_as_spheres,
            render_lines_as_tubes,
            smooth_shading,
            split_sharp_edges,
            ambient,
            diffuse,
            specular,
            specular_power,
            nan_color,
            nan_opacity,
            culling,
            rgb,
            categories,
            silhouette,
            use_transparency,
            below_color,
            above_color,
            annotations,
            pickable,
            preference,
            log_scale,
            pbr,
            metallic,
            roughness,
            render,
            user_matrix,
            component,
            emissive,
            copy_mesh,
            backface_params,
            show_vertices,
            edge_opacity,
            **kwargs,
        )

    # ==================================================
    def remove_actor(self, actor, reset_camera=False, render=True):
        """
        Remove actor.

        Args:
            actor (str, vtk.vtkActor, list or tuple): actor name.
            reset_camera (bool, optional): reset camera to show all actors ?
            render (bool, optional): render upon actor removal.

        Returns:
            - (bool) -- True if actor is removed.

        :meta private:
        """
        return self.pyvista_widget.remove_actor(actor, reset_camera, render)

    # ==================================================
    def load(self, filename):
        """
        Load all info.

        Args:
            filename (str): full file name.
        """
        self._flush()
        self.pyvista_widget.load(filename)
        self._mark_saved()
        self._reset_history()

    # ==================================================
    def save(self, filename):
        """
        save all info.

        Args:
            filename (str): full file name.
        """
        self._save(filename)
        self._mark_saved()

    # ==================================================
    def _save(self, filename):
        """
        Save the document, and keep the history valid in the new directory.

        Args:
            filename (str): full file name.

        Note:
            - saving changes the current directory to that of the file, and makes the data file names of isosurfaces relative to it.

        :meta private:
        """
        self._flush()
        old_dir = Path.cwd()
        try:
            self.pyvista_widget.save(filename)
        finally:  # also when writing fails after the directory was changed.
            new_dir = Path.cwd()
            if old_dir != new_dir:
                self._history.map(lambda s: self.pyvista_widget.rebase_snapshot(s, old_dir, new_dir))

    # ==================================================
    # MultiPie interface
    # ==================================================
    def _check_multipie(self):
        if not check_multipie():
            raise Exception("MultiPie is not installed.")
        if self.multipie_dialog is None:
            QMessageBox.question(self, "", "Call 'mp_set_group(tag)' at first.", QMessageBox.Ok)
            return True
        return False

    # ==================================================
    def mp_set_group(self, group):
        """
        MultiPie: Set group.

        Args:
            group (str): group tag [default: C1].
        """
        if self.multipie_dialog is not None:
            self.multipie_dialog.close()
            self.multipie_dialog = None

        self.pyvista_widget.mp_set_group(group=group)
        self.misc_button_multipie.released.emit()

    # ==================================================
    def mp_add_site(self, site, size=None, color=None, opacity=None):
        """
        MultiPie: Add equivalent sites.

        Args:
            site (str): representative site.
            size (float, optional): size.
            color (str, optional): color.
            opacity (float, optional): opacity.
        """
        if self._check_multipie():
            return

        self.pyvista_widget.mp_add_site(site, size, color, opacity)
        self.multipie_dialog._object_panel.edit_site.setText(site)

    # ==================================================
    def mp_add_bond(self, bond, width=None, color=None, color2=None, opacity=None):
        """
        MultiPie: Add equivalent bonds.

        Args:
            bond (str): representative bond.
            width (float, optional): width.
            color (str, optional): color.
            color2 (str, optional): color2.
            opacity (float, optional): opacity.
        """
        if self._check_multipie():
            return

        self.pyvista_widget.mp_add_bond(bond, width, color, color2, opacity)
        self.multipie_dialog._object_panel.edit_bond.setText(bond)

    # ==================================================
    def mp_add_vector(
        self, vector_sb, type="Q", cartesian=True, average=False, length=None, width=None, color=None, opacity=None
    ):
        """
        MultiPie: Add transformed vectors at equivalent sites or bonds.

        Args:
            vector_sb (str): vector, "v # site_bond".
            type (str, optional): type of vector, Q/G/T/M.
            cartesian (bool, optional): cartesian vector ?
            average (bool, optional): average ?
            length (float, optional): length.
            width (float, optional): width.
            color (str, optional): color.
            opacity (float, optional): opacity.
        """
        if self._check_multipie():
            return

        self.pyvista_widget.mp_add_vector(vector_sb, type, cartesian, average, length, width, color, opacity)
        self.multipie_dialog._object_panel.combo_vector_type.setCurrentText(type)
        self.multipie_dialog._object_panel.edit_vector.setText(vector_sb)
        self.multipie_dialog._object_panel.check_vector_cart.setChecked(cartesian)
        self.multipie_dialog._object_panel.check_vector_av.setChecked(average)

    # ==================================================
    def mp_add_orbital(self, orbital_sb, type="Q", average=False, size=None, color=None, opacity=None):
        """
        MultiPie: Add transformed orbitals at equivalent sites or bonds.

        Args:
            orbital_sb (str): orbital, "f(r) # site_bond".
            type (str, optional): type of orbital, Q/G/T/M.
            average (bool, optional): average ?
            size (float, optional): size.
            color (str, optional): color.
            opacity (float, optional): opacity.
        """
        if self._check_multipie():
            return

        self.pyvista_widget.mp_add_orbital(orbital_sb, type, average, size, color, opacity)
        self.multipie_dialog._object_panel.combo_orbital_type.setCurrentText(type)
        self.multipie_dialog._object_panel.edit_orbital.setText(orbital_sb)
        self.multipie_dialog._object_panel.check_orbital_av.setChecked(average)

    # ==================================================
    def mp_add_bond_definition(self, bond, length=None, width=None, color=None, opacity=None):
        """
        MultiPie: Create bond definition.

        Args:
            bond (str): representative bond.
            length (float, optional): length.
            width (float, optional): width.
            color (str, optional): color.
            opacity (float, optional): opacity.
        """
        if self._check_multipie():
            return

        self.pyvista_widget.mp_add_bond_definition(bond, length, width, color, opacity)
        self.multipie_dialog._basis_panel.edit_def_bond.setText(bond)

    # ==================================================
    def mp_site_samb_list(self, site):
        """
        MultiPie: Create site SAMB list.

        Args:
            site (str): representative site.

        Returns:
            - (list) -- list of site SAMB, [str].
        """
        if self._check_multipie():
            return

        self.multipie_dialog._basis_panel.edit_site.setText(site)
        return self.pyvista_widget.mp_site_samb_list(site)

    # ==================================================
    def mp_add_site_samb(self, tag, size=None, p_color=None, n_color=None, z_color=None, z_size=None):
        """
        MultiPie: Add site SAMB.

        Args:
            tag (str): site SAMB, obtained by mp_site_samb_list.
            size (float, optional): relative size.
            p_color (str, optional): positive SAMB color.
            n_color (str, optional): negative SAMB color.
            z_color (str, optional): zero SAMB color.
            z_size (float, optional): zero SAMB size.
        """
        self.pyvista_widget.mp_add_site_samb(tag, size, p_color, n_color, z_color, z_size)
        self.multipie_dialog._basis_panel.combo_site_samb.setCurrentText(tag)

    # ==================================================
    def mp_bond_samb_list(self, bond):
        """
        MultiPie: Create bond SAMB list.

        Args:
            bond (str): representative bond.

        Returns:
            - (list) -- list of bond SAMB, [str].
        """
        if self._check_multipie():
            return

        self.multipie_dialog._basis_panel.edit_bond.setText(bond)
        return self.pyvista_widget.mp_bond_samb_list(bond)

    # ==================================================
    def mp_add_bond_samb(self, tag, width=None, p_color=None, n_color=None, z_color=None, z_width=None, a_size=None):
        """
        MultiPie: Add bond SAMB.

        Args:
            tag (str): bond SAMB, obtained by mp_bond_samb_list.
            width (float, optional): relative width.
            p_color (str, optional): positive SAMB color.
            n_color (str, optional): negative SAMB color.
            z_color (str, optional): zero SAMB color.
            z_width (float, optional): zero SAMB width.
            a_size (float, optional): relative arrow size.
        """
        self.pyvista_widget.mp_add_bond_samb(tag, width, p_color, n_color, z_color, z_width, a_size)
        self.multipie_dialog._basis_panel.combo_bond_samb.setCurrentText(tag)

    # ==================================================
    def mp_vector_samb_list(self, site_bond, type="Q"):
        """
        MultiPie: Create vector SAMB list.

        Args:
            site_bond (str): representative site or bond.
            type (str, optional): type of vector, Q/G/T/M.

        Returns:
            - (dict) -- list of vector SAMB, Dict[samb_type, [str] ].
        """
        if self._check_multipie():
            return

        self.multipie_dialog._basis_panel.combo_vector_type.setCurrentText(type)
        self.multipie_dialog._basis_panel.edit_vector.setText(site_bond)
        return self.pyvista_widget.mp_vector_samb_list(site_bond, type)

    # ==================================================
    def mp_add_vector_samb(self, lc, length=None, width=None, color=None, opacity=None):
        """
        MultiPie: Add vector SAMB.

        Args:
            lc (str): linear combination of vector SAMBs, obtained by mp_vector_samb_list.
            length (float, optional): relative length.
            width (float, optional): relative width.
            color (str, optional): color.
            opacity (float, optional): opacity.
        """
        self.pyvista_widget.mp_add_vector_samb(lc, length, width, color, opacity)
        self.multipie_dialog._basis_panel.edit_vector_lc.setText(lc)

    # ==================================================
    def mp_add_vector_samb_modulation(self, modulation_range, length=None, width=None, color=None, opacity=None):
        """
        MultiPie: Add vector SAMB with modulation.

        Args:
            modulation_range (str): modulation and range, "[[tag, coeff, k_vector, cos/sin]] : [r1, r2, r3]".
            length (float, optional): relative length.
            width (float, optional): relative width.
            color (str, optional): color.
            opacity (float, optional): opacity.
        """
        self.pyvista_widget.mp_add_vector_samb_modulation(modulation_range, length, width, color, opacity)
        self.multipie_dialog._basis_panel.edit_vector_modulation.setText(modulation_range)

    # ==================================================
    def mp_orbital_samb_list(self, site_bond, type="Q", rank=0):
        """
        MultiPie: Create orbital SAMB.

        Args:
            site_bond (str): representative site or bond.
            type (str, optional): type of orbital, Q/G/T/M.
            rank (int or str, optional): rank.

        Returns:
            - (dict) -- list of orbital SAMB, Dict[samb_type, [str] ].
        """
        if self._check_multipie():
            return

        self.multipie_dialog._basis_panel.combo_orbital_type.setCurrentText(type)
        self.multipie_dialog._basis_panel.combo_orbital_rank.setCurrentText(str(rank))
        self.multipie_dialog._basis_panel.edit_orbital.setText(site_bond)
        return self.pyvista_widget.mp_orbital_samb_list(site_bond, type, rank)

    # ==================================================
    def mp_add_orbital_samb(self, lc, size=None, color=None, opacity=None):
        """
        MultiPie: Add orbital SAMB.

        Args:
            lc (str): linear combination of orbital SAMBs, obtained by mp_orbital_samb_list.
            size (float, optional): relative size.
            color (str, optional): color.
            opacity (float, optional): opacity.
        """
        self.pyvista_widget.mp_add_orbital_samb(lc, size, color, opacity)
        self.multipie_dialog._basis_panel.edit_orbital_lc.setText(lc)

    # ==================================================
    def mp_add_orbital_samb_modulation(self, modulation_range, size=None, color=None, opacity=None):
        """
        MultiPie: Add orbital SAMB with modulation.

        Args:
            modulation_range (str): modulation and range, "[[tag, coeff, k_vector, cos/sin]] : [r1, r2, r3]".
            size (float, optional): relative size.
            color (str, optional): color.
            opacity (float, optional): opacity.
        """
        self.pyvista_widget.mp_add_orbital_samb_modulation(modulation_range, size, color, opacity)
        self.multipie_dialog._basis_panel.edit_orbital_modulation.setText(modulation_range)
