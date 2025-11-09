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
from PySide6.QtGui import QFont, Qt, QPixmap, QColor, QIcon
from PySide6.QtCore import Signal
from gcoreutils.color_palette import all_colors
from qtdraw.util.color_selector_util import _color2pixmap
from qtdraw.widget.validator import (
    validator_int,
    validator_float,
    validator_sympy_float,
    validator_sympy,
    validator_ilist,
    validator_list,
    validator_site,
    validator_bond,
    validator_site_bond,
    validator_vector_site_bond,
    validator_orbital_site_bond,
)
from qtdraw.util.latex_to_png import latex_to_png
from qtdraw.util.color_selector_util import color2pixmap


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
class Color(QColor):
    # ==================================================
    def __init__(self, color):
        """
        Color

        Args:
            color (str): color name.
        """
        super().__init__(all_colors[color][0])


# ==================================================
class Label(QLabel):
    # ==================================================
    def __init__(self, parent=None, text="", bold=False, color="black", size=10, math=False, dpi=120):
        """
        Label widget.

        Args:
            parent (QWidget, optional): parent.
            text (str, optional): text.
            bold (bool, optional): bold font ?
            color (str, optional): font color.
            size (int, optional): font size.
            math (bool, optional): for math ?
            dpi (int, optional): DPI for math.

        Note:
            - in math mode, text is given in LaTeX code without $.
        """
        super().__init__(parent=parent)
        policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.setSizePolicy(policy)
        self.setContentsMargins(0, 0, 0, 0)
        font = QFont()
        font.setBold(bold)
        self.setFont(font)
        self.setFocusPolicy(Qt.NoFocus)
        self.setIndent(6)

        if math:
            self.to_png = lambda text: latex_to_png(text, True, color, size, dpi)
        else:
            self.to_png = None

        self.setText(text)

    # ==================================================
    def setText(self, text):
        """
        Set text.

        Args:
            text (xtr): text.
        """
        if self.to_png is None:
            super().setText(text)
        else:
            s = self.to_png(text)
            if s is None:
                return
            else:
                pixmap = QPixmap()
                pixmap.setDevicePixelRatio(1.0)
                pixmap.loadFromData(s)
                super().setPixmap(pixmap)


# ==================================================
class ColorLabel(Panel):
    # ==================================================
    def __init__(self, parent=None, color="", bold=False):
        """
        Color label widget.

        Args:
            parent (QWidget, optional): parent.
            color (str, optional): color/colormap name.
            bold (bool, optional): bold font ?
        """
        super().__init__(parent)

        label = Label(self, color, bold)
        size = label.font().pointSize()

        colorbox = _color2pixmap(color, "color_both", size)
        icon = Label(self)
        icon.setPixmap(colorbox)
        icon.setFrameStyle(QFrame.Box)
        icon.setFixedSize(colorbox.size())

        self.layout.addWidget(icon, 0, 0)
        self.layout.addWidget(label, 0, 1)


# ==================================================
class LineEdit(QLineEdit):
    _valid_style = "padding-left: 3px; background: none;"
    _invalid_style = "padding-left: 3px; background: pink;"
    _read_only_style = "padding-left: 3px; background: lightgray;"

    focusOut = Signal()

    # ==================================================
    def __init__(self, parent=None, text="", validator=None):
        """
        Line editor.

        Args:
            parent (QWidget, optional): parent.
            text (str, optional): text.
            validator (tuple, optional): (validator_type, option).
        """
        super().__init__(text, parent)
        policy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.setSizePolicy(policy)
        self.setContentsMargins(0, 0, 0, 0)

        self.set_validator(validator)
        self.set_read_only(False)
        self._raw = text
        self._backup = text
        self._valid = True

        self.setText(text)

    # ==================================================
    @property
    def validator(self):
        """
        Validator type.

        Returns:
            - (str) -- validator type.
        """
        return self._validator_type

    # ==================================================
    @property
    def read_only(self):
        """
        Read only ?

        Returns:
            - (bool) -- read only ?
        """
        return self._read_only

    # ==================================================
    def close_edit(self):
        """
        Close editor.
        """
        if self._valid:
            self.returnPressed.emit()
            self.clearFocus()

    # ==================================================
    def raw_text(self):
        """
        Raw text.

        Returns:
            - (str) -- raw text.
        """
        return self._raw

    # ==================================================
    def setText(self, text):
        """
        Set text.

        Args:
            text (str): text.
        """
        if self._validator is None:
            s = text
        else:
            s = self._validator(text)

        if s is None:
            self.setStyleSheet(self._invalid_style)
            self._valid = False
        else:
            if self.read_only:
                super().setText(s)
                return
            self.setStyleSheet(self._valid_style)
            self._backup = text
            self._raw = text
            self._valid = True
            super().setText(s)

    # ==================================================
    def set_validator(self, validator):
        """
        Set validator.

        Args:
            validator (tuple): (validator_type, option).
        """
        validator_dict = {
            "int": validator_int,
            "float": validator_float,
            "sympy_float": validator_sympy_float,
            "sympy": validator_sympy,
            "ilist": validator_ilist,
            "list": validator_list,
            "site": validator_site,
            "bond": validator_bond,
            "site_bond": validator_site_bond,
            "vector_site_bond": validator_vector_site_bond,
            "orbital_site_bond": validator_orbital_site_bond,
        }
        if validator is None:
            self._validator = None
        else:
            self._validator_type, option = validator
            self._validator = lambda text: validator_dict[self._validator_type](text, option)

    # ==================================================
    def set_read_only(self, flag):
        """
        Set read only.

        Args:
            flag (bool): read only ?
        """
        self._read_only = flag
        if flag:
            self.setStyleSheet(self._read_only_style)
        else:
            self.setStyleSheet(self._valid_style)

    # ==================================================
    def focusInEvent(self, event):
        """
        Focus-out event.
        """
        super().setText(self._raw)
        super().focusInEvent(event)
        self.selectAll()

    # ==================================================
    def focusOutEvent(self, event):
        """
        Focus-out event.
        """
        self.clearFocus()
        super().focusOutEvent(event)
        self.focusOut.emit()

    # ==================================================
    def clearFocus(self):
        """
        Clear focus.
        """
        if not self.read_only:
            if not self._valid:
                self.setStyleSheet(self._valid_style)
            self.setText(self._backup)
        super().clearFocus()

    # ==================================================
    def keyPressEvent(self, event):
        """
        Key event.

        Args:
            event (str): event.
        """
        k = event.key()
        if k == Qt.Key_Escape:
            self.clearFocus()
            self.setFocus()
        elif k == Qt.Key_Return:
            self.setText(self.text())
            self.close_edit()
        else:
            super().keyPressEvent(event)


# ==================================================
class HBar(QFrame):
    # ==================================================
    def __init__(self, parent=None):
        """
        Horizontal bar item.

        Args:
            parent (QWidget, optional): parent.
        """
        super().__init__(parent)
        self.setMinimumSize(0, 10)
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)
        self.setContentsMargins(0, 0, 0, 0)
        self.setFocusPolicy(Qt.NoFocus)


# ==================================================
class Button(QPushButton):
    # ==================================================
    def __init__(self, parent=None, text="", toggle=False):
        """
        Button widget.

        Args:
            parent (QWidget, optional): parent.
            text (str, optional): text.
            toggle (bool, optional): toggle button ?
        """
        super().__init__(text, parent)
        self.setCheckable(toggle)
        self.setContentsMargins(0, 0, 0, 0)
        self.setFocusPolicy(Qt.NoFocus)


# ==================================================
class Combo(QComboBox):
    # ==================================================
    def __init__(self, parent=None, item=[], init=None):
        """
        Combo widget.

        Args:
            parent (QWidget, optional): parent.
            item (list, optional): list of items, [str].
            init (str, optional): initial value.
        """
        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        self.setFocusPolicy(Qt.NoFocus)
        self.set_item(item)
        if init is not None:
            self.setCurrentText(init)

        total_height = self.font().pointSize() * 1.6
        self.setFixedHeight(total_height)

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
        index = [idx for idx, s in enumerate(item) if key in s]
        return index


# ==================================================
class Spin(QSpinBox):
    # ==================================================
    def __init__(self, parent=None, min=0, max=1):
        """
        Spin widget.

        Args:
            parent (QWidget, optional): parent.
            min (int, optional): minimum value.
            max (int, optional): maximum value.
        """
        super().__init__(parent)
        self.setMinimum(min)
        self.setMaximum(max)
        self.setContentsMargins(0, 0, 0, 0)
        self.setFocusPolicy(Qt.NoFocus)


# ==================================================
class DSpin(QDoubleSpinBox):
    # ==================================================
    def __init__(self, parent=None, min=0.0, max=1.0, step=0.1):
        """
        Spin widget.

        Args:
            parent (QWidget, optional): parent.
            min (float, optional): minimum value.
            max (float, optioanl): maximum value.
            step (float, optional): step value.
        """
        super().__init__(parent)
        self.setMinimum(min)
        self.setMaximum(max)
        self.setSingleStep(step)
        self.setContentsMargins(0, 0, 0, 0)
        self.setFocusPolicy(Qt.NoFocus)


# ==================================================
class Check(QCheckBox):
    # ==================================================
    def __init__(self, parent=None, text=""):
        """
        Check widget.

        Args:
            parent (QWidget, optional): parent.
            text (str, optional): text.
        """
        super().__init__(text, parent)
        self.setContentsMargins(0, 0, 0, 0)
        self.setFocusPolicy(Qt.NoFocus)

    # ==================================================
    def is_checked(self):
        """
        Is checked ?

        Returns:
            - (bool) -- checked ?
        """
        return self.checkState() == Qt.Checked


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
class Editor(Panel):
    returnPressed = Signal(str)

    # ==================================================
    def __init__(self, parent=None, text="", validator=None, color="black", size=10, dpi=120):
        """
        Math equation label widget.

        Args:
            parent (QWidget, optional): parent.
            text (str, optional): text.
            validator (tuple, optional): (validator_type, option).
            color (str, optioanl): color name.
            size (int, optional): font size.
            dpi (int, optional): DPI.

        Note:
            - following validators can be used.
                - int: (min, max).
                - float: (min, max, digit).
                - sympy_float: (digit).
                - sympy: (variable list).
                - ilist: (shape).
                - list: (shape, variable list, digit).
                - site: (use variable?).
                - bond: (use variable?).
                - site_bond: (use variable?).
                - vector_site_bond: (use variable?).
                - orbital_site_bond: (use variable?).
        """
        super().__init__(parent)

        math = False
        if validator is not None and validator[0] == "sympy":
            math = True

        self._editor = LineEdit(None, text, validator)
        self._display = Label(None, self._editor.text(), color=color, size=size, math=math, dpi=dpi)

        self.layout.addWidget(self._display, 0, 0)
        self.layout.addWidget(self._editor, 0, 0)

        self._editor.hide()
        self._in_edit = False

        self._editor.returnPressed.connect(self.close_editor)
        self._editor.focusOut.connect(self.clearFocus)

    # ==================================================
    def close_editor(self):
        """
        Close editor.
        """
        self.clearFocus()
        if self._editor._valid:
            self.returnPressed.emit(self._editor.raw_text())

    # ==================================================
    def clearFocus(self):
        """
        Clear focus.
        """
        if self._editor._valid:
            self._display.setText(self._editor.text())
        self._editor.clearFocus()
        self._editor.hide()
        self._display.show()
        self._in_edit = False

    # ==================================================
    def mouseDoubleClickEvent(self, event):
        """
        Mouse double-click event.
        """
        if not self._in_edit and not self._editor.read_only:
            self._in_edit = True
            self._display.hide()
            self._editor.show()
            self._editor.setFocus()

    # ==================================================
    def mousePressEvent(self, event):
        """
        Mouse click event.
        """
        current = QApplication.focusWidget()
        if current:
            current.clearFocus()
        super().mousePressEvent(event)

    # ==================================================
    def text(self):
        """
        Text.

        Returns:
            - (str) -- text.
        """
        if self._editor._validator_type == "sympy":
            return self._editor.raw_text()
        else:
            return self._display.text()

    # ==================================================
    def setText(self, text):
        """
        Set text.

        Args:
            text (str): text.
        """
        self._editor.setText(text)
        if self._editor._valid:
            self._display.setText(self._editor.text())

    # ==================================================
    def raw_text(self):
        """
        Raw text.

        Returns:
            - (str) -- raw text.
        """
        return self._editor.raw_text()

    # ==================================================
    def setCurrentText(self, text):
        """
        Set current text.

        Args:
            text (str): text.
        """
        self._editor.setText(text)
        if self._editor._valid:
            self._display.setText(self._editor.text())

    # ==================================================
    def currentText(self):
        """
        Get current text.

        Returns:
            - (str) -- current text.
        """
        return self._editor.raw_text()


# ==================================================
class ColorSelector(QComboBox):
    # ==================================================
    def __init__(self, parent=None, current="", color_type="color"):
        """
        Color selector widget.

        Args:
            parent (QWidget, optional): parent.
            current (str, optional): default color.
            color_type (str, optional): color/colormap/color_both

        Notes:
            - connect currentTextChanged.
        """
        super().__init__(parent=parent)
        self.setFocusPolicy(Qt.NoFocus)
        self.setContentsMargins(0, 0, 0, 0)

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
        self.setCurrentIndex(current_index)

        icon_size = next(iter(color_pixmap.values())).size()
        self.setIconSize(icon_size)

        total_height = icon_size.height() * 1.8
        self.setFixedHeight(total_height)

        for i in separator:
            self.insertSeparator(i)
