"""
Custom widget.

This module provides customuized widgets.
"""

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QGridLayout,
    QSizePolicy,
    QLineEdit,
    QFrame,
    QPushButton,
    QComboBox,
    QSpinBox,
    QDoubleSpinBox,
    QCheckBox,
    QSpacerItem,
    QApplication,
)
from PySide6.QtGui import QPainter, QFont, QIcon
from PySide6.QtCore import Signal, QSize, Qt
from PySide6.QtSvg import QSvgRenderer
from xml.etree import ElementTree as ET

from qtdraw.sandbox.color_selector_util import color2pixmap, color_palette
from qtdraw.sandbox.validator import (
    validator_int,
    validator_float,
    validator_sympy_int,
    validator_sympy_float,
    validator_sympy_latex,
    validator_site,
    validator_bond,
    validator_site_bond,
    validator_vector_site_bond,
    validator_orbital_site_bond,
)
from qtdraw.mathjax.latex_to_svg import latex_to_svg_string


# ==================================================
class Layout(QGridLayout):
    # ==================================================
    def __init__(self, parent=None):
        """
        Layout widget.

        Args:
            parent (QWidget, optional): parent.
        """
        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        self.setHorizontalSpacing(2)
        self.setVerticalSpacing(5)


# ==================================================
class Panel(QWidget):
    # ==================================================
    def __init__(self, parent=None):
        """
        Panel widget.

        Args:
            parent (QWidget, optional): parent.
        """
        super().__init__(parent)
        self.layout = Layout(self)


# ==================================================
class Label(QLabel):
    # ==================================================
    def __init__(self, parent=None, text="", color="black", size=None, bold=False):
        """
        Label widget.

        Args:
            parent (QWidget, optional): parent.
            text (str, optional): text.
            color (str, optional): font color.
            size (int, optional): font size (pt).
            bold (bool, optional): bold font ?
        """
        super().__init__(parent)

        self.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed))
        self.setContentsMargins(0, 0, 0, 0)

        font = QFont()
        if size is not None:
            font.setPointSize(size)
        font.setBold(bold)
        self.setFont(font)
        self.setPalette(color_palette(color))

        self.setText(text)
        self.setIndent(6)

    # ==================================================
    def sizeHint(self):
        sz = super().sizeHint()
        extra = 10
        return QSize(sz.width() + extra, sz.height())


# ==================================================
class MathWidget(QWidget):
    # ==================================================
    def __init__(self, parent=None, text="", color="black", size=None):
        super().__init__(parent)

        if size is None:
            size = self.font().pointSize()

        self.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed))
        self.setContentsMargins(0, 0, 0, 0)

        self._size = size + 5
        self._color = color
        self._text = ""
        self._renderer = None
        self._wsize = (0, 0)

        self.setText(text)

    # ==================================================
    def setText(self, text):
        self._text = text
        text = "$$" + text + "$$"
        s = latex_to_svg_string(text, self._color)

        root = ET.fromstring(s)
        x, y, w, h = map(float, root.attrib["viewBox"].split())
        scale = self._size / 1000.0
        root.set("width", str(w * scale))
        root.set("height", str(h * scale))
        svg_bytes = ET.tostring(root, encoding="utf-8")
        self._renderer = QSvgRenderer(svg_bytes)
        self._wsize = (int(w * scale), int(h * scale))
        self.setFixedSize(*self._wsize)
        self.update()

    # ==================================================
    def text(self):
        return self._text

    # ==================================================
    def paintEvent(self, event):
        if not self._renderer:
            return
        painter = QPainter(self)
        self._renderer.render(painter)

    # ==================================================
    def sizeHint(self):
        return QSize(*self._wsize)


# ==================================================
class HBar(QFrame):
    # ==================================================
    def __init__(self, parent=None):
        """
        Horizontal bar widget.

        Args:
            parent (QWidget, optional): parent.
        """
        super().__init__(parent)
        self.setMinimumSize(0, 10)
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


# ==================================================
class VSpacer(QSpacerItem):
    # ==================================================
    def __init__(self):
        """
        Vertical spacer.
        """
        super().__init__(1, 1, QSizePolicy.Minimum, QSizePolicy.Expanding)


# ==================================================
class HSpacer(QSpacerItem):
    # ==================================================
    def __init__(self):
        """
        Horizontal spacer.
        """
        super().__init__(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)


# ==================================================
class ColorSelector(QComboBox):
    # ==================================================
    def __init__(self, parent=None, current="", color_type="color", size=None, bold=False):
        """
        Color selector widget.

        Args:
            parent (QWidget, optional): parent.
            current (str, optional): default color.
            color_type (str, optional): color/colormap/color_both
            size (int, optional): font size.
            bold (bool, optional): bold face ?

        Notes:
            - connect currentTextChanged.
        """
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed))

        font = QFont()
        if size is not None:
            font.setPointSize(size)
        font.setBold(bold)
        self.setFont(font)

        color_pixmap, separator = color2pixmap(color_type, self.font().pointSize())
        names = list(color_pixmap.keys())

        if current == "":
            current_index = 0
        else:
            try:
                current_index = names.index(current)
            except ValueError:
                current_index = 0

        self.blockSignals(True)
        for color, pixmap in color_pixmap.items():
            self.addItem(QIcon(pixmap), color)
        self.blockSignals(False)

        icon_size = next(iter(color_pixmap.values())).size()
        self.setIconSize(icon_size)
        self.setFixedHeight(int(icon_size.height() * 1.8))

        for i in separator:
            self.insertSeparator(i)

        self.setCurrentIndex(current_index)
        # self.setSizeAdjustPolicy(QComboBox.AdjustToContents)

    # ==================================================
    def sizeHint(self):
        sz = super().sizeHint()
        extra = 10
        return QSize(sz.width() + extra, sz.height())


# ==================================================
class Button(QPushButton):
    # ==================================================
    def __init__(self, parent=None, text="", toggle=False, size=None, bold=False):
        """
        Button widget.

        Args:
            parent (QWidget, optional): parent.
            text (str, optional): text.
            toggle (bool, optional): toggle button ?
            size (int, optional): font size.
            bold (bool, optional): bold face ?
        """
        super().__init__(text, parent)
        self.setCheckable(toggle)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed))

        font = QFont()
        if size is not None:
            font.setPointSize(size)
        font.setBold(bold)
        self.setFont(font)


# ==================================================
class Combo(QComboBox):
    # ==================================================
    def __init__(self, parent=None, item=None, init=None, size=None, bold=False):
        """
        Combo widget.

        Args:
            parent (QWidget, optional): parent.
            item (list, optional): list of items, [str].
            init (str, optional): initial value.
            size (int, optional): font size.
            bold (bool, optional): bold face ?
        """
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed))

        font = QFont()
        if size is not None:
            font.setPointSize(size)
        font.setBold(bold)
        self.setFont(font)

        if item is None:
            item = []

        self.set_item(item)

        if init is not None:
            self.setCurrentText(init)

        total_height = self.font().pointSize() * 1.6
        self.setFixedHeight(total_height)
        # self.setSizeAdjustPolicy(QComboBox.AdjustToContents)

    # ==================================================
    def get_item(self):
        """
        Get item.

        Returns:
            - (list) -- item list.
        """
        lst = [self.itemText(i) for i in range(self.count())]
        return lst

    # ==================================================
    def set_item(self, item):
        """
        Set item.

        Args:
            item (list): item list.
        """
        self.blockSignals(True)
        self.clear()
        self.addItems(item)
        self.blockSignals(False)

    # ==================================================
    def find_index(self, key):
        """
        Find index.

        Args:
            key (str): item key.

        Returns:
            - (int) -- index.
        """
        item = self.get_item()
        index = [idx for idx, s in enumerate(item) if key == s]
        return index

    # ==================================================
    def sizeHint(self):
        sz = super().sizeHint()
        extra = 10
        return QSize(sz.width() + extra, sz.height())


# ==================================================
class Spin(QSpinBox):
    # ==================================================
    def __init__(self, parent=None, minimum=0, maximum=1, size=None, bold=False):
        """
        Spin widget.

        Args:
            parent (QWidget, optional): parent.
            minimum (int, optional): minimum value.
            maximum (int, optional): maximum value.
            size (int, optional): font size.
            bold (bool, optional): bold face ?
        """
        super().__init__(parent)
        self.setMinimum(minimum)
        self.setMaximum(maximum)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed))

        font = QFont()
        if size is not None:
            font.setPointSize(size)
        font.setBold(bold)
        self.setFont(font)


# ==================================================
class DSpin(QDoubleSpinBox):
    # ==================================================
    def __init__(self, parent=None, minimum=0.0, maximum=1.0, step=0.1, size=None, bold=False):
        """
        Spin widget.

        Args:
            parent (QWidget, optional): parent.
            minimum (float, optional): minimum value.
            maximum (float, optional): maximum value.
            step (float, optional): step value.
            size (int, optional): font size.
            bold (bool, optional): bold face ?
        """
        super().__init__(parent)
        self.setMinimum(minimum)
        self.setMaximum(maximum)
        self.setSingleStep(step)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed))

        font = QFont()
        if size is not None:
            font.setPointSize(size)
        font.setBold(bold)
        self.setFont(font)


# ==================================================
class Check(QCheckBox):
    # ==================================================
    def __init__(self, parent=None, text="", size=None, bold=False):
        """
        Check widget.

        Args:
            parent (QWidget, optional): parent.
            text (str, optional): text.
            size (int, optional): font size.
            bold (bool, optional): bold face ?
        """
        super().__init__(text, parent)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed))

        font = QFont()
        if size is not None:
            font.setPointSize(size)
        font.setBold(bold)
        self.setFont(font)

    # ==================================================
    def is_checked(self):
        """
        Is checked ?

        Returns:
            - (bool) -- checked ?
        """
        return self.checkState() == Qt.Checked


# ==================================================
class LineEdit(QLineEdit):
    focusOut = Signal()

    def __init__(self, parent=None, text="", validator=None, size=None, bold=False):
        super().__init__("", parent)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.setContentsMargins(0, 0, 0, 0)

        font = QFont()
        if size is not None:
            font.setPointSize(size)
        font.setBold(bold)
        self.setFont(font)

        self._validator_func = None
        self._read_only = False
        self._valid = True
        self._raw = ""
        self._validated = ""

        if validator:
            self.set_validator(validator)

        self.setText(text)

    # ==================================================
    def set_validator(self, validator):
        vtype, option = validator
        VALIDATORS = {
            "int": validator_int,
            "float": validator_float,
            "list_float": validator_sympy_float,
            "list_int": validator_sympy_int,
            "math": validator_sympy_latex,
            "site": validator_site,
            "bond": validator_bond,
            "site_bond": validator_site_bond,
            "vector_site_bond": validator_vector_site_bond,
            "orbital_site_bond": validator_orbital_site_bond,
        }
        self._validator_func = lambda t: VALIDATORS[vtype](t, **option)

    # ==================================================
    def setText(self, text):
        validated = self._validate(text)

        if validated is None:
            self._valid = False
            super().setText(text)
        else:
            self._raw = text
            self._valid = True
            self._validated = validated
            super().setText(validated)

        self._update_style()

    # ==================================================
    def _validate(self, text):
        return self._validator_func(text) if self._validator_func else text

    # ==================================================
    def _update_style(self):
        base_style = """
            QLineEdit {{
                padding-left: 3px;
                padding-right: 3px;
                background: {bg_color};
            }}
            QLineEdit:focus {{
                border: 2px solid "#90B8EF";
            }}
        """
        if self._read_only:
            bg_color = "lightgray"
        elif self._valid:
            bg_color = "white"
        else:
            bg_color = "pink"

        self.setStyleSheet(base_style.format(bg_color=bg_color))

    # ==================================================
    def raw_text(self):
        return self._raw

    # ==================================================
    def set_read_only(self, flag):
        self._read_only = flag
        self.setReadOnly(flag)

        if flag:
            self.setFocusPolicy(Qt.NoFocus)
        else:
            self.setFocusPolicy(Qt.StrongFocus)

        self._update_style()

    # ==================================================
    def keyPressEvent(self, event):
        k = event.key()
        if k == Qt.Key_Escape:
            super().setText(self._validated)
            self._valid = True
            self._update_style()
            return

        if k in (Qt.Key_Return, Qt.Key_Enter):
            self.setText(self.text())
            if self._valid:
                self.returnPressed.emit()
            return

        super().keyPressEvent(event)

    # ==================================================
    def focusOutEvent(self, event):
        super().setText(self._validated)
        self._valid = True
        self._update_style()

        super().focusOutEvent(event)
        self.focusOut.emit()

    # ==================================================
    def focusInEvent(self, event):
        super().setText(self._raw)
        self._update_style()
        super().focusInEvent(event)


# ==================================================
class Editor(Panel):
    returnPressed = Signal(str)

    # ==================================================
    def __init__(self, parent=None, text="", validator=None, color="black", size=None, bold=False):
        """
        Editor widget with math/text display.

        Args:
            parent (QWidget, optional): parent.
            text (str, optional): text.
            validator (tuple, optional): (validator_type, option).
            color (str, optional): color name.
            size (int, optional): font size.
            bold (bool, optional): bold face ?
        """
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed))

        self._math_mode = validator is not None and validator[0] == "math"

        self._editor = LineEdit(parent=parent, text=text, validator=validator, bold=bold, size=size)

        validated = self._editor._validated or text

        self._display = (
            MathWidget(parent=parent, text=validated, color=color, size=size)
            if self._math_mode
            else Label(parent=parent, text=validated, color=color, bold=bold, size=size)
        )

        self.layout.addWidget(self._display, 0, 0)
        self.layout.addWidget(self._editor, 0, 0)
        self._editor.hide()

        self._in_edit = False

        # Signals
        self._editor.returnPressed.connect(self._on_return)
        self._editor.focusOut.connect(self._on_focus_out)

    # ==================================================
    def _on_return(self):
        """
        Called when Enter is pressed in editor.
        """
        self.clearFocus()
        if self._editor._valid:
            self.returnPressed.emit(self._editor.raw_text())

    # ==================================================
    def _on_focus_out(self):
        """
        Handle focus-out safely.
        """
        if self._in_edit:
            self.clearFocus()

    # ==================================================
    def clearFocus(self):
        """
        Exit edit mode, safely restoring display.
        """
        if not self._in_edit:
            return

        self._in_edit = False

        if self._editor._valid:
            self._display.setText(self._editor._validated)

        self._editor.hide()
        self._display.show()

        # Avoid recursion
        if self._editor.hasFocus():
            self._editor.blockSignals(True)
            self._editor.clearFocus()
            self._editor.blockSignals(False)

    # ==================================================
    def mouseDoubleClickEvent(self, _):
        """
        Switch to edit mode on double click.
        """
        if not self._in_edit and not self._editor._read_only:
            self._in_edit = True
            self._display.hide()
            self._editor.show()
            self._editor.setFocus(Qt.TabFocusReason)

    # ==================================================
    def mousePressEvent(self, event):
        """
        Handle focus changes safely.
        """
        focused = QApplication.focusWidget()
        if focused and focused not in (self, self._editor):
            focused.clearFocus()
        super().mousePressEvent(event)

    # ==================================================
    def text(self):
        """
        Return current text.

        - During editing: return raw_text() from LineEdit.
        - Otherwise: return display text.
        """
        if self._in_edit:
            return self._editor.raw_text()
        return self._display.text()

    # ==================================================
    def setText(self, text):
        """
        Set editor and display text.
        """
        self._editor.setText(text)
        if self._editor._valid:
            self._display.setText(self._editor.text())

    # ==================================================
    def setCurrentText(self, text):
        self.setText(text)

    # ==================================================
    def sizeHint(self):
        return self._display.sizeHint()
