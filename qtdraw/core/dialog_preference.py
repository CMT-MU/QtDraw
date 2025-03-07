"""
Preference dialog.

This module provides preference dialog for PyVistaWidget.
"""

from PySide6.QtWidgets import QDialog, QTabWidget, QWidget, QDialogButtonBox
from PySide6.QtCore import Qt
from qtdraw.widget.custom_widget import Layout, Label, Combo, Spin, DSpin, Check, VSpacer, HSpacer, ColorSelector
from qtdraw.util.util import create_style_sheet


# ==================================================
class PreferenceDialog(QDialog):
    # ==================================================
    def __init__(self, widget, parent=None):
        """
        Preference dialog.

        Args:
            widget (PyVistaWidget): widget.
            parent (QWidget, optional): parent.
        """
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        self.resize(400, 300)

        self.widget = widget
        self.preference = widget._preference

        panel_label = self.create_label_panel(self)
        panel_axis = self.create_axis_panel(self)
        panel_cell = self.create_cell_panel(self)
        panel_light = self.create_light_panel(self)
        panel_latex = self.create_latex_panel(self)
        panel_general = self.create_general_panel(self)

        # tab content.
        tab = QTabWidget(self)
        tab.addTab(panel_label, "Label")
        tab.addTab(panel_axis, "Axis")
        tab.addTab(panel_cell, "Cell")
        tab.addTab(panel_light, "Light")
        tab.addTab(panel_latex, "LaTeX")
        tab.addTab(panel_general, "General")

        # button.
        button = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply)
        button.accepted.connect(self.accept)
        button.rejected.connect(self.reject)
        button.button(QDialogButtonBox.Apply).clicked.connect(self.apply)

        # main layout.
        layout = Layout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.addWidget(tab, 0, 0, 1, 2)
        layout.addWidget(button, 1, 0, 2, 1)

    # ==================================================
    def create_label_panel(self, parent):
        """
        Create label panel.
        """
        panel = QWidget(parent)
        layout = Layout(panel)
        layout.setContentsMargins(10, 5, 10, 5)

        preference = self.preference["label"]

        # widgets.
        label_font = Label(parent, "font")
        combo_font = Combo(parent, ["arial", "courier", "times"])
        label_size = Label(parent, "size")
        spin_size = Spin(parent, 4, 48)
        label_color = Label(parent, "color")
        combo_color = ColorSelector(parent, preference["color"], color_type="color")
        check_bold = Check(parent, "bold")
        check_italic = Check(parent, "italic")
        check_default = Check(parent, "default check")

        # set layout.
        layout.addWidget(label_font, 0, 0, 1, 1, Qt.AlignRight)
        layout.addWidget(combo_font, 0, 1, 1, 1)
        layout.addWidget(label_size, 0, 2, 1, 1, Qt.AlignRight)
        layout.addWidget(spin_size, 0, 3, 1, 1)
        layout.addWidget(check_bold, 1, 1, 1, 1)
        layout.addWidget(check_italic, 1, 3, 1, 1)
        layout.addWidget(label_color, 2, 0, 1, 1, Qt.AlignRight)
        layout.addWidget(combo_color, 2, 1, 1, 1)
        layout.addWidget(check_default, 3, 1, 1, 1)
        layout.addItem(HSpacer(), 0, 4, 1, 1)
        layout.addItem(VSpacer(), 4, 0, 1, 1)

        # initial values.
        combo_font.setCurrentText(preference["font"])
        spin_size.setProperty("value", preference["size"])
        check_bold.setChecked(preference["bold"])
        check_italic.setChecked(preference["italic"])
        check_default.setChecked(preference["default_check"])

        # connections.
        combo_font.currentTextChanged.connect(lambda v: preference.update({"font": v}))
        spin_size.valueChanged.connect(lambda v: preference.update({"size": v}))
        combo_color.currentTextChanged.connect(lambda v: preference.update({"color": v}))
        check_bold.toggled.connect(lambda flag: preference.update({"bold": flag}))
        check_italic.toggled.connect(lambda flag: preference.update({"italic": flag}))
        check_default.toggled.connect(lambda flag: preference.update({"default_check": flag}))

        return panel

    # ==================================================
    def create_axis_panel(self, parent):
        """
        Create axis panel.
        """
        panel = QWidget(parent)
        layout = Layout(panel)
        layout.setContentsMargins(10, 5, 10, 5)

        preference = self.preference["axis"]
        axis_type = {
            "xyz": "[x,y,z]",
            "abc": "[a,b,c]",
            "abc*": "[a*,b*,c*]",
            "[x,y,z]": "xyz",
            "[a,b,c]": "abc",
            "[a*,b*,c*]": "abc*",
        }

        # widgets.
        label_type = Label(parent, "type")
        combo_type = Combo(parent, ["xyz", "abc", "abc*"])
        label_size = Label(parent, "size")
        spin_size = Spin(parent, 12, 36)
        check_bold = Check(parent, "bold")
        check_italic = Check(parent, "italic")

        # set layout.
        layout.addWidget(label_type, 0, 0, 1, 1, Qt.AlignRight)
        layout.addWidget(combo_type, 0, 1, 1, 1)
        layout.addWidget(label_size, 0, 2, 1, 1, Qt.AlignRight)
        layout.addWidget(spin_size, 0, 3, 1, 1)
        layout.addWidget(check_bold, 1, 1, 1, 1)
        layout.addWidget(check_italic, 1, 3, 1, 1)
        layout.addItem(HSpacer(), 0, 4, 1, 1)
        layout.addItem(VSpacer(), 2, 0, 1, 1)

        # initial values.
        combo_type.setCurrentText(axis_type[preference["label"]])
        spin_size.setProperty("value", preference["size"])
        check_bold.setChecked(preference["bold"])
        check_italic.setChecked(preference["italic"])

        # connections.
        combo_type.currentTextChanged.connect(lambda v: preference.update({"label": axis_type[v]}))
        spin_size.valueChanged.connect(lambda v: preference.update({"size": v}))
        check_bold.toggled.connect(lambda flag: preference.update({"bold": flag}))
        check_italic.toggled.connect(lambda flag: preference.update({"italic": flag}))

        return panel

    # ==================================================
    def create_cell_panel(self, parent):
        """
        Create cell panel.
        """
        panel = QWidget(parent)
        layout = Layout(panel)
        layout.setContentsMargins(10, 5, 10, 5)

        preference = self.preference["cell"]

        # widgets.
        label_width = Label(parent, "width")
        spin_width = DSpin(parent, 0.0, 5.0, 0.1)
        label_color = Label(parent, "color")
        combo_color = ColorSelector(parent, preference["color"], color_type="color")
        label_opacity = Label(parent, "opacity")
        spin_opacity = DSpin(parent, 0.0, 1.0, 0.1)

        # set layout.
        layout.addWidget(label_width, 0, 0, 1, 1, Qt.AlignRight)
        layout.addWidget(spin_width, 0, 1, 1, 1)
        layout.addWidget(label_opacity, 1, 0, 1, 1, Qt.AlignRight)
        layout.addWidget(spin_opacity, 1, 1, 1, 1)
        layout.addWidget(label_color, 2, 0, 1, 1, Qt.AlignRight)
        layout.addWidget(combo_color, 2, 1, 1, 2)
        layout.addItem(HSpacer(), 2, 3, 1, 1)
        layout.addItem(VSpacer(), 3, 0, 1, 1)

        # initial values.
        spin_width.setProperty("value", preference["line_width"])
        spin_opacity.setProperty("value", preference["opacity"])

        # connections.
        spin_width.valueChanged.connect(lambda v: preference.update({"line_width": round(v, 4)}))
        combo_color.currentTextChanged.connect(lambda v: preference.update({"color": v}))
        spin_opacity.valueChanged.connect(lambda v: preference.update({"opacity": round(v, 4)}))

        return panel

    # ==================================================
    def create_light_panel(self, parent):
        """
        Create light panel.
        """
        panel = QWidget(parent)
        layout = Layout(panel)
        layout.setContentsMargins(10, 5, 10, 5)

        preference = self.preference["light"]

        # widgets.
        label_intensity = Label(parent, "intensity")
        spin_intensity = DSpin(parent, 0.0, 1.0, 0.05)
        check_pbr = Check(parent, "physics based rendering")
        label_metallic = Label(parent, "metallic")
        spin_metallic = DSpin(parent, 0.0, 1.0, 0.1)
        label_roughness = Label(parent, "roughness")
        spin_roughness = DSpin(parent, 0.0, 1.0, 0.1)
        label_color = Label(parent, "color")
        combo_color = ColorSelector(parent, preference["color"], color_type="color")
        label_type = Label(parent, "type")
        combo_type = Combo(parent, ["lightkit", "3 lights", "ver1"])

        # set layout.
        layout.addWidget(label_type, 0, 0, 1, 1, Qt.AlignRight)
        layout.addWidget(combo_type, 0, 1, 1, 1)
        layout.addWidget(label_intensity, 1, 0, 1, 1, Qt.AlignRight)
        layout.addWidget(spin_intensity, 1, 1, 1, 1)
        layout.addWidget(label_color, 1, 2, 1, 1, Qt.AlignRight)
        layout.addWidget(combo_color, 1, 3, 1, 1)
        layout.addWidget(check_pbr, 2, 0, 1, 3)
        layout.addWidget(label_metallic, 3, 1, 1, 1, Qt.AlignRight)
        layout.addWidget(spin_metallic, 3, 2, 1, 1)
        layout.addWidget(label_roughness, 4, 1, 1, 1, Qt.AlignRight)
        layout.addWidget(spin_roughness, 4, 2, 1, 1)
        layout.addItem(HSpacer(), 0, 4, 1, 1)
        layout.addItem(VSpacer(), 5, 0, 1, 1)

        # initial values.
        spin_intensity.setProperty("value", preference["intensity"])
        check_pbr.setChecked(preference["pbr"])
        spin_metallic.setProperty("value", preference["metallic"])
        spin_roughness.setProperty("value", preference["roughness"])
        combo_type.setCurrentText(preference["type"])

        # connections.
        spin_intensity.valueChanged.connect(lambda v: preference.update({"intensity": round(v, 4)}))
        check_pbr.toggled.connect(lambda flag: preference.update({"pbr": flag}))
        spin_metallic.valueChanged.connect(lambda v: preference.update({"metallic": round(v, 4)}))
        spin_roughness.valueChanged.connect(lambda v: preference.update({"roughness": round(v, 4)}))
        combo_color.currentTextChanged.connect(lambda v: preference.update({"color": v}))
        combo_type.currentTextChanged.connect(lambda v: preference.update({"type": v}))

        return panel

    # ==================================================
    def create_latex_panel(self, parent):
        """
        Create LaTeX panel.
        """
        panel = QWidget(parent)
        layout = Layout(panel)
        layout.setContentsMargins(10, 5, 10, 5)

        preference = self.preference["latex"]

        # widgets.
        label_color = Label(parent, "color")
        combo_color = ColorSelector(parent, preference["color"], color_type="color")
        label_size = Label(parent, "size")
        spin_size = Spin(parent, 8, 24)
        label_dpi = Label(parent, "DPI")
        combo_dpi = Combo(parent, ["120", "240", "300"])

        # set layout.
        layout.addWidget(label_color, 0, 0, 1, 1, Qt.AlignRight)
        layout.addWidget(combo_color, 0, 1, 1, 2)
        layout.addWidget(label_size, 1, 0, 1, 1, Qt.AlignRight)
        layout.addWidget(spin_size, 1, 1, 1, 2)
        layout.addWidget(label_dpi, 2, 0, 1, 1, Qt.AlignRight)
        layout.addWidget(combo_dpi, 2, 1, 1, 2)
        layout.addItem(HSpacer(), 0, 3, 1, 1)
        layout.addItem(VSpacer(), 3, 0, 1, 1)

        # initial values.
        spin_size.setProperty("value", preference["size"])
        combo_dpi.setCurrentText(str(preference["dpi"]))

        # connections.
        combo_color.currentTextChanged.connect(lambda v: preference.update({"color": v}))
        spin_size.valueChanged.connect(lambda v: preference.update({"size": v}))
        combo_dpi.currentTextChanged.connect(lambda v: preference.update({"dpi": int(v)}))

        return panel

    # ==================================================
    def create_general_panel(self, parent):
        """
        Create general panel.
        """
        panel = QWidget(parent)
        layout = Layout(panel)
        layout.setContentsMargins(10, 5, 10, 5)

        preference = self.preference["general"]

        # widgets.
        label_style = Label(parent, "style")
        combo_style = Combo(parent, ["fusion", "macos", "windows"])
        label_font = Label(parent, "font")
        combo_font = Combo(parent, ["Osaka", "Monaco", "Arial", "Times New Roman", "Helvetica Neue"])
        label_color = Label(parent, "scheme")
        combo_color = Combo(parent, ["Jmol", "VESTA"])
        label_size = Label(parent, "size")
        spin_size = Spin(parent, 9, 14)

        # set layout.
        layout.addWidget(label_style, 0, 0, 1, 1, Qt.AlignRight)
        layout.addWidget(combo_style, 0, 1, 1, 1)
        layout.addWidget(label_font, 1, 0, 1, 1, Qt.AlignRight)
        layout.addWidget(combo_font, 1, 1, 1, 1)
        layout.addWidget(label_size, 1, 2, 1, 1, Qt.AlignRight)
        layout.addWidget(spin_size, 1, 3, 1, 1)
        layout.addWidget(label_color, 2, 0, 1, 1, Qt.AlignRight)
        layout.addWidget(combo_color, 2, 1, 1, 1)
        layout.addItem(HSpacer(), 1, 4, 1, 1)
        layout.addItem(VSpacer(), 3, 0, 1, 1)

        # initial values.
        combo_style.setCurrentText(preference["style"])
        combo_font.setCurrentText(preference["font"])
        combo_color.setCurrentText(preference["color_scheme"])
        spin_size.setProperty("value", preference["size"])

        # connections.
        combo_style.currentTextChanged.connect(lambda v: preference.update({"style": v}))
        combo_font.currentTextChanged.connect(lambda v: preference.update({"font": v}))
        combo_color.currentTextChanged.connect(lambda v: preference.update({"color_scheme": v}))
        spin_size.valueChanged.connect(lambda v: preference.update({"size": v}))

        return panel

    # ==================================================
    def apply(self, button):
        """
        Apply change.

        Args:
            button (QAbstractButton): button status.

        :meta private:
        """
        self.parent().app.setStyleSheet(create_style_sheet(self.preference["general"]["size"]))
        self.widget.refresh()
        self.widget.redraw()
        self.parent()._update_panel()
