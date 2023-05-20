from qtpy.QtWidgets import (
    QDialog,
    QTabWidget,
    QWidget,
    QSpacerItem,
    QSizePolicy,
    QComboBox,
    QCheckBox,
    QSpinBox,
    QDoubleSpinBox,
    QLabel,
    QGridLayout,
    QDialogButtonBox,
)
from qtpy.QtCore import Qt
from qtdraw.core.editable_widget import QtColorSelector


# ==================================================
class DialogPreference(QDialog):
    # ==================================================
    def __init__(self, preference, setting, apply_callback, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle("Preferences")

        self.preference = preference
        self.setting = setting
        self.callback = apply_callback
        self.pref = preference.copy()
        self.sett = setting.copy()
        self.default = preference.copy()
        self.default_set = setting.copy()

        self.resize(350, 200)

        # tab contents.
        self.tab = QTabWidget(self)
        self.create_tab_label()
        self.create_tab_vector()
        self.create_tab_axis()
        self.create_tab_cell()
        self.create_tab_light()
        self.create_tab_spotlight()

        # buttons.
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.buttonBox.clicked.connect(self.apply)

        # main layout
        self.layout = QGridLayout(self)
        self.layout.addWidget(self.tab, 0, 0, 1, 2)
        self.layout.addWidget(self.buttonBox, 1, 0, 2, 1)

    # ==================================================
    def create_tab_label(self):
        self.tab_label = QWidget()
        self.tab.addTab(self.tab_label, "label")

        self.lbl_size = QLabel("font size", self)
        self.spin_size = QSpinBox(self)
        self.spin_size.setMinimum(4)
        self.spin_size.setMaximum(48)
        self.spin_size.setProperty("value", self.pref["label.size"])
        self.lbl_bold = QLabel("bold", self)
        self.check_bold = QCheckBox(self)
        self.check_bold.setChecked(self.pref["label.bold"])
        self.lbl_italic = QLabel("italic", self)
        self.check_italic = QCheckBox(self)
        self.check_italic.setChecked(self.pref["label.italic"])
        self.lbl_color = QLabel("color", self)
        self.combo_color = QtColorSelector(
            self.pref["label.color"],
            color_type="color",
            callback=lambda v: self.pref.update({"label.color": v}),
            parent=self,
        )
        self.combo_color.layout.setContentsMargins(0, 0, 0, 0)
        self.lbl_family = QLabel("font family", self)
        self.combo_font = QComboBox(self)
        self.combo_font.addItems(["arial", "courier", "times"])
        self.combo_font.setCurrentText(self.pref["label.font"])

        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        spacerItem1 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_4 = QGridLayout(self.tab_label)
        self.gridLayout_4.addWidget(self.lbl_size, 0, 0, 1, 1)
        self.gridLayout_4.addWidget(self.spin_size, 0, 1, 1, 1)
        self.gridLayout_4.addItem(spacerItem, 0, 2, 1, 1)
        self.gridLayout_4.addWidget(self.lbl_bold, 1, 0, 1, 1)
        self.gridLayout_4.addWidget(self.check_bold, 1, 1, 1, 1)
        self.gridLayout_4.addWidget(self.lbl_italic, 2, 0, 1, 1)
        self.gridLayout_4.addWidget(self.check_italic, 2, 1, 1, 1)
        self.gridLayout_4.addWidget(self.lbl_color, 3, 0, 1, 1)
        self.gridLayout_4.addWidget(self.combo_color, 3, 1, 1, 1)
        self.gridLayout_4.addWidget(self.lbl_family, 4, 0, 1, 1)
        self.gridLayout_4.addWidget(self.combo_font, 4, 1, 1, 1)
        self.gridLayout_4.addItem(spacerItem1, 5, 0, 1, 1)

        self.spin_size.valueChanged.connect(lambda v: self.pref.update({"label.size": v}))
        self.check_bold.toggled.connect(lambda flag: self.pref.update({"label.bold": flag}))
        self.check_italic.toggled.connect(lambda flag: self.pref.update({"label.italic": flag}))
        self.combo_font.currentTextChanged.connect(lambda v: self.pref.update({"label.font": v}))

    # ==================================================
    def create_tab_vector(self):
        self.tab_vector = QWidget()
        self.tab.addTab(self.tab_vector, "vector")

        self.lbl_tip_l = QLabel("tip length", self)
        self.spin_tip_l = QDoubleSpinBox(self)
        self.spin_tip_l.setMaximum(1.0)
        self.spin_tip_l.setSingleStep(0.05)
        self.spin_tip_l.setProperty("value", self.pref["vector.tip.length"])
        self.spin_tip_l.setFocusPolicy(Qt.NoFocus)
        self.lbl_tip_r = QLabel("tip radius", self)
        self.spin_tip_r = QDoubleSpinBox(self)
        self.spin_tip_r.setMaximum(0.5)
        self.spin_tip_r.setSingleStep(0.01)
        self.spin_tip_r.setProperty("value", self.pref["vector.tip.radius"])
        self.spin_tip_r.setFocusPolicy(Qt.NoFocus)
        self.lbl_shaft_r = QLabel("shaft radius", self)
        self.spin_shaft_r = QDoubleSpinBox(self)
        self.spin_shaft_r.setMaximum(0.5)
        self.spin_shaft_r.setSingleStep(0.01)
        self.spin_shaft_r.setProperty("value", self.pref["vector.shaft.radius"])
        self.spin_shaft_r.setFocusPolicy(Qt.NoFocus)

        spacerItem2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        spacerItem3 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_5 = QGridLayout(self.tab_vector)
        self.gridLayout_5.addWidget(self.lbl_tip_l, 0, 0, 1, 1)
        self.gridLayout_5.addWidget(self.spin_tip_l, 0, 1, 1, 1)
        self.gridLayout_5.addItem(spacerItem2, 0, 2, 1, 1)
        self.gridLayout_5.addWidget(self.lbl_tip_r, 1, 0, 1, 1)
        self.gridLayout_5.addWidget(self.spin_tip_r, 1, 1, 1, 1)
        self.gridLayout_5.addWidget(self.lbl_shaft_r, 2, 0, 1, 1)
        self.gridLayout_5.addWidget(self.spin_shaft_r, 2, 1, 1, 1)
        self.gridLayout_5.addItem(spacerItem3, 3, 0, 1, 1)

        self.spin_tip_l.valueChanged.connect(lambda v: self.pref.update({"vector.tip.length": round(v, 4)}))
        self.spin_tip_r.valueChanged.connect(lambda v: self.pref.update({"vector.tip.radius": round(v, 4)}))
        self.spin_shaft_r.valueChanged.connect(lambda v: self.pref.update({"vector.shaft.radius": round(v, 4)}))

    # ==================================================
    def create_tab_axis(self):
        self.tab_axis = QWidget()
        self.tab.addTab(self.tab_axis, "axis")

        self.lbl_atype = QLabel("type", self)
        self.combo_atype = QComboBox(self)
        self.combo_atype.addItems(["xyz", "abc", "abc*"])
        self.combo_atype.setCurrentText(self.pref["axis.type"])
        self.lbl_asize = QLabel("size", self)
        self.spin_asize = QSpinBox(self)
        self.spin_asize.setMinimum(10)
        self.spin_asize.setMaximum(24)
        self.spin_asize.setProperty("value", self.pref["axis.size"])
        self.lbl_abold = QLabel("bold", self)
        self.check_abold = QCheckBox(self)
        self.check_abold.setChecked(self.pref["axis.bold"])
        self.lbl_aitalic = QLabel("italic", self)
        self.check_aitalic = QCheckBox(self)
        self.check_aitalic.setChecked(self.pref["axis.italic"])
        self.lbl_aposition = QLabel("position", self)
        self.spin_aposition = QDoubleSpinBox(self)
        self.spin_aposition.setMinimum(0.8)
        self.spin_aposition.setMaximum(1.2)
        self.spin_aposition.setSingleStep(0.1)
        self.spin_aposition.setProperty("value", self.pref["axis.position"])
        self.lbl_ctype = QLabel("crystal", self)
        self.combo_ctype = QComboBox(self)
        self.combo_ctype.addItems(["", "triclinic", "monoclinic", "orthorhombic", "tetragonal", "trigonal", "hexagonal", "cubic"])
        self.combo_ctype.setCurrentText(self.sett["crystal"])

        spacerItema1 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        spacerItema2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_a = QGridLayout(self.tab_axis)
        self.gridLayout_a.addWidget(self.lbl_atype, 0, 0, 1, 1)
        self.gridLayout_a.addWidget(self.combo_atype, 0, 1, 1, 1)
        self.gridLayout_a.addItem(spacerItema1, 0, 2, 1, 1)
        self.gridLayout_a.addWidget(self.lbl_ctype, 1, 0, 1, 1)
        self.gridLayout_a.addWidget(self.combo_ctype, 1, 1, 1, 1)
        self.gridLayout_a.addWidget(self.lbl_asize, 2, 0, 1, 1)
        self.gridLayout_a.addWidget(self.spin_asize, 2, 1, 1, 1)
        self.gridLayout_a.addWidget(self.lbl_abold, 3, 0, 1, 1)
        self.gridLayout_a.addWidget(self.check_abold, 3, 1, 1, 1)
        self.gridLayout_a.addWidget(self.lbl_aitalic, 4, 0, 1, 1)
        self.gridLayout_a.addWidget(self.check_aitalic, 4, 1, 1, 1)
        self.gridLayout_a.addWidget(self.lbl_aposition, 5, 0, 1, 1)
        self.gridLayout_a.addWidget(self.spin_aposition, 5, 1, 1, 1)
        self.gridLayout_a.addItem(spacerItema2, 6, 0, 1, 1)

        self.combo_atype.currentTextChanged.connect(lambda v: self.pref.update({"axis.type": v}))
        self.spin_asize.valueChanged.connect(lambda v: self.pref.update({"axis.size": v}))
        self.check_abold.toggled.connect(lambda flag: self.pref.update({"axis.bold": flag}))
        self.check_aitalic.toggled.connect(lambda flag: self.pref.update({"axis.italic": flag}))
        self.spin_aposition.valueChanged.connect(lambda v: self.pref.update({"axis.position": round(v, 4)}))
        self.combo_ctype.currentTextChanged.connect(lambda v: self.sett.update({"crystal": v}))

    # ==================================================
    def create_tab_cell(self):
        self.tab_cell = QWidget()
        self.tab.addTab(self.tab_cell, "cell")

        self.gridLayout_2 = QGridLayout(self.tab_cell)
        self.lbl_width = QLabel("width", self)
        self.spin_width = QDoubleSpinBox(self)
        self.spin_width.setMaximum(5.0)
        self.spin_width.setSingleStep(0.1)
        self.spin_width.setProperty("value", self.pref["cell.width"])
        self.spin_width.setFocusPolicy(Qt.NoFocus)
        self.lbl_color_2 = QLabel("color", self)
        self.combo_color_2 = QtColorSelector(
            self.pref["cell.color"],
            color_type="color",
            callback=lambda v: self.pref.update({"cell.color": v}),
            parent=self,
        )
        self.combo_color_2.layout.setContentsMargins(0, 0, 0, 0)
        self.lbl_opacity = QLabel("opacity", self)
        self.spin_opacity = QDoubleSpinBox(self)
        self.spin_opacity.setMaximum(1.0)
        self.spin_opacity.setSingleStep(0.1)
        self.spin_opacity.setProperty("value", self.pref["cell.opacity"])
        self.spin_opacity.setFocusPolicy(Qt.NoFocus)

        spacerItem4 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        spacerItem5 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_2.addWidget(self.lbl_width, 0, 0, 1, 1)
        self.gridLayout_2.addWidget(self.spin_width, 0, 1, 1, 1)
        self.gridLayout_2.addItem(spacerItem4, 0, 2, 1, 1)
        self.gridLayout_2.addWidget(self.lbl_color_2, 1, 0, 1, 1)
        self.gridLayout_2.addWidget(self.combo_color_2, 1, 1, 1, 1)
        self.gridLayout_2.addWidget(self.lbl_opacity, 2, 0, 1, 1)
        self.gridLayout_2.addWidget(self.spin_opacity, 2, 1, 1, 1)
        self.gridLayout_2.addItem(spacerItem5, 3, 0, 1, 1)

        self.spin_width.valueChanged.connect(lambda v: self.pref.update({"cell.width": round(v, 4)}))
        self.spin_opacity.valueChanged.connect(lambda v: self.pref.update({"cell.opacity": round(v, 4)}))

    # ==================================================
    def create_tab_light(self):
        self.tab_light = QWidget()
        self.tab.addTab(self.tab_light, "light")

        self.gridLayout = QGridLayout(self.tab_light)
        self.lbl_intensity = QLabel("intensity", self)
        self.spin_intensity = QDoubleSpinBox(self)
        self.spin_intensity.setMaximum(1.0)
        self.spin_intensity.setSingleStep(0.1)
        self.spin_intensity.setProperty("value", self.pref["light.intensity"])
        self.lbl_prb = QLabel("physics based rendering", self)
        self.check_pbr = QCheckBox(self)
        self.check_pbr.setChecked(self.pref["light.pbr"])
        self.lbl_metallic = QLabel("metallic", self)
        self.spin_metallic = QDoubleSpinBox(self)
        self.spin_metallic.setMaximum(1.0)
        self.spin_metallic.setSingleStep(0.1)
        self.spin_metallic.setProperty("value", self.pref["light.metallic"])
        self.lbl_roughness = QLabel("roughness", self)
        self.spin_roughness = QDoubleSpinBox(self)
        self.spin_roughness.setMaximum(1.0)
        self.spin_roughness.setSingleStep(0.1)
        self.spin_roughness.setProperty("value", self.pref["light.roughness"])
        self.lbl_eye_light = QLabel("eye dome lighting", self)
        self.check_eye_dome_light = QCheckBox(self)
        self.check_eye_dome_light.setChecked(self.pref["light.eye_dome_lighting"])

        spacerItem6 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        spacerItem7 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout.addWidget(self.lbl_intensity, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.spin_intensity, 0, 1, 1, 1)
        self.gridLayout.addItem(spacerItem6, 0, 2, 1, 1)
        self.gridLayout.addWidget(self.lbl_prb, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.check_pbr, 1, 1, 1, 1)
        self.gridLayout.addWidget(self.lbl_metallic, 1, 2, 1, 1)
        self.gridLayout.addWidget(self.spin_metallic, 1, 3, 1, 1)
        self.gridLayout.addWidget(self.lbl_roughness, 2, 2, 1, 1)
        self.gridLayout.addWidget(self.spin_roughness, 2, 3, 1, 1)
        self.gridLayout.addWidget(self.lbl_eye_light, 3, 0, 1, 1)
        self.gridLayout.addWidget(self.check_eye_dome_light, 3, 1, 1, 1)
        self.gridLayout.addItem(spacerItem7, 4, 0, 1, 1)

        self.spin_intensity.valueChanged.connect(lambda v: self.pref.update({"light.intensity": round(v, 4)}))
        self.check_pbr.toggled.connect(lambda flag: self.pref.update({"light.pbr": flag}))
        self.spin_metallic.valueChanged.connect(lambda v: self.pref.update({"light.metallic": round(v, 4)}))
        self.spin_roughness.valueChanged.connect(lambda v: self.pref.update({"light.roughness": round(v, 4)}))
        self.check_eye_dome_light.toggled.connect(lambda flag: self.pref.update({"light.eye_dome_lighting": flag}))

    # ==================================================
    def create_tab_spotlight(self):
        self.tab_spotlight = QWidget()
        self.tab.addTab(self.tab_spotlight, "spotlight")

        self.gridLayout_3 = QGridLayout(self.tab_spotlight)
        self.lbl_radius = QLabel("radius", self)
        self.spin_radius = QDoubleSpinBox(self)
        self.spin_radius.setMaximum(5.0)
        self.spin_radius.setSingleStep(0.05)
        self.spin_radius.setProperty("value", self.pref["spotlight.size"])
        self.lbl_color_3 = QLabel("color", self)
        self.combo_color_3 = QtColorSelector(
            self.pref["spotlight.color"],
            color_type="color",
            callback=lambda v: self.pref.update({"spotlight.color": v}),
            parent=self,
        )
        self.combo_color_3.layout.setContentsMargins(0, 0, 0, 0)
        self.lbl_opacity_2 = QLabel("opacity", self)
        self.spin_opacity_2 = QDoubleSpinBox(self)
        self.spin_opacity_2.setMaximum(1.0)
        self.spin_opacity_2.setSingleStep(0.1)
        self.spin_opacity_2.setProperty("value", self.pref["spotlight.opacity"])

        spacerItem8 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        spacerItem9 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_3.addWidget(self.lbl_radius, 0, 0, 1, 1)
        self.gridLayout_3.addWidget(self.spin_radius, 0, 1, 1, 1)
        self.gridLayout_3.addItem(spacerItem8, 0, 2, 1, 1)
        self.gridLayout_3.addWidget(self.lbl_color_3, 1, 0, 1, 1)
        self.gridLayout_3.addWidget(self.combo_color_3, 1, 1, 1, 1)
        self.gridLayout_3.addWidget(self.lbl_opacity_2, 2, 0, 1, 1)
        self.gridLayout_3.addWidget(self.spin_opacity_2, 2, 1, 1, 1)
        self.gridLayout_3.addItem(spacerItem9, 3, 0, 1, 1)

        self.spin_radius.valueChanged.connect(lambda v: self.pref.update({"spotlight.size": round(v, 4)}))
        self.spin_opacity_2.valueChanged.connect(lambda v: self.pref.update({"spotlight.opacity": round(v, 4)}))

    # ==================================================
    def accept(self):
        self.preference.update(self.pref)
        self.setting.update(self.sett)
        self.callback()
        super().accept()

    # ==================================================
    def reject(self):
        self.preference.update(self.default)
        self.setting.update(self.default_set)
        self.callback()
        super().reject()

    # ==================================================
    def apply(self, button):
        if self.buttonBox.standardButton(button) == QDialogButtonBox.Apply:
            self.preference.update(self.pref)
            self.setting.update(self.sett)
            self.callback()
