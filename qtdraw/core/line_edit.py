from qtpy.QtWidgets import QLineEdit, QWidget, QLabel, QDialog, QGridLayout
from qtpy.QtCore import Qt, Signal
from qtpy.QtGui import QValidator
from gcoreutils.convert_util import is_valid_sympy, text_to_list
from gcoreutils.basic_util import apply
from gcoreutils.string_util import remove_space
from qtdraw.core.validator import validator_map, create_validator


# ==================================================
class LineEdit(QLineEdit):
    """
    customized line editor.
    """

    closeEdit = Signal()
    _valid_style = "padding-left: 3px; background: none;"
    _invalid_style = "padding-left: 3px; background: pink;"
    _read_only_style = "padding-left: 3px; background: lightgray;"
    _validator_list = list(validator_map.keys())

    # ==================================================
    def __init__(self, init="", validator=None, decimal=4, check_var=None, parent=None):
        """
        initialize the class.

        Args:
            init (str, optional): initial text.
            validator (str, optional): validator. see, validator_list.
            decimal (int, optional): precision for real number.
            check_var (list, optional): acceptable variable strings. if None, do not check.
            parent (QWidget, optional): parent object.
        """
        super().__init__(parent)

        self.set_validator(validator, decimal, check_var)
        self.setText(init)
        self._backtup = self.text()

    # ==================================================
    def set_validator(self, validator=None, decimal=4, check_var=None):
        """
        set validator.

        Args:
            validator (str, optional): validator. see, validator_list.
            decimal (int, optional): precision for real number.
            check_var (list, optional): acceptable variable strings. if None, do not check.
        """
        if validator not in self.validator_list:
            validator = None

        self._formatter = lambda text: text

        self._str_validator = False
        if validator is None:
            self._validator = None
        else:
            self._validator = create_validator(validator)
            if validator == "real_unit":
                self._validator.setDecimals(decimal)
            if validator[0] == "i":
                self._formatter = lambda text: str(apply(lambda t: "{ts: d}".format(ts=int(t)), text_to_list(text))).replace(
                    "'", ""
                )
            elif validator[0] == "r":
                self._formatter = lambda text: str(
                    apply(lambda t: "{ts: .{decimal}f}".format(ts=float(t), decimal=decimal), text_to_list(text))
                ).replace("'", "")
            elif validator[0] in ["s", "l"]:
                self._str_validator = True

        self.check_var = check_var

    # ==================================================
    def focusOutEvent(self, event):
        """
        :meta private:
        """
        self.setStyleSheet(self._valid_style)
        self.closeEdit.emit()
        super().focusOutEvent(event)

    # ==================================================
    def keyPressEvent(self, event):
        """
        :meta private:
        """
        k = event.key()
        if k == Qt.Key_Escape:
            self.setStyleSheet(self._valid_style)
            self.closeEdit.emit()
        elif k == Qt.Key_Return:
            status = self.setText(self.text())
            if status:
                self.returnPressed.emit()
        else:
            super().keyPressEvent(event)

    # ==================================================
    def setText(self, text):
        """
        set text.

        Args:
            text (str): text.

        Returns:
            bool: return True if text is valid.
        """
        if self._validator is not None and not self._str_validator:
            text = remove_space(text)
        status = True
        if self._validator is not None:
            status, text, pos = self._validator.validate(text, 0)
            status = status == QValidator.Acceptable
        if self.check_var is not None:
            status = status and is_valid_sympy(text, self.check_var)

        if status:
            text = self._formatter(text)
            self.setStyleSheet(self._valid_style)
            super().setText(text)
            self._backtup = text
        else:
            self.setStyleSheet(self._invalid_style)

        if self.isReadOnly():
            self.setStyleSheet(self._read_only_style)

        return status

    # ==================================================
    def clear(self):
        """
        clear editor.
        """
        self.setText("")
        self.setStyleSheet(self._valid_style)
        super().clear()

    # ==================================================
    @property
    def validator_list(self):
        """
        available validator list.

        Returns:
            list: validator list.
        """
        return self._validator_list


# ==================================================
class LineEditor(QDialog):
    """
    customized line editor widget.
    """

    closeEdit = Signal()
    acceptEdit = Signal()

    # ==================================================
    def __init__(self, label="", init="", validator=None, decimal=4, check_var=None, callback=None, parent=None):
        """
        initialize the class.

        Args:
            label (str, optional): label of the editor.
            init (str, optional): initial text.
            validator (str, optional): validator. see, validator_list.
            decimal (int, optional): precision for real number.
            check_var (list, optional): acceptable variable strings. if None, do not check.
            parent (QWidget, optional): parent object.
        """
        super().__init__(parent)

        if callback is None:
            self.callback = self.default_callback
        else:
            self.callback = callback

        self.label = QLabel(label, self)
        self.label.setIndent(0)

        self.editor = LineEdit(init, validator, decimal, check_var, self)
        self.editor.closeEdit.connect(self.close_edit)
        self.editor.returnPressed.connect(self.accept_edit)

        self.layout = QGridLayout()
        self.layout.setContentsMargins(0, 1, 0, 1)
        self.layout.setSpacing(3)
        if label != "":
            self.layout.addWidget(self.label, 0, 0)
            self.layout.addWidget(self.editor, 0, 1)
        else:
            self.layout.addWidget(self.editor, 0, 0)

        self.setLayout(self.layout)

    # ==================================================
    def close_edit(self):
        """
        :meta private:
        """
        self.editor.setText(self.editor._backtup)
        self.closeEdit.emit()

    # ==================================================
    def accept_edit(self):
        """
        :meta private:
        """
        text = self.editor.text()
        self.callback(text)
        self.acceptEdit.emit()

    # ==================================================
    def setText(self, text):
        """
        set text.

        Args:
            text (str): text.
        """
        self.editor.setText(text)

    # ==================================================
    def text(self):
        """
        current text.

        Returns:
            str: text.
        """
        return self.editor.text()

    # ==================================================
    def default_callback(self, text):
        """
        :meta private:
        """
        print(text)

    # ==================================================
    def set_validator(self, validator=None, decimal=4, check_var=None):
        """
        set validator.

        Args:
            validator (str, optional): validator. see, validator_list.
            decimal (int, optional): precision for real number.
            check_var (list, optional): acceptable variable strings. if None, do not check.
        """
        self.editor.set_validator(validator, decimal, check_var)

    # ==================================================
    def clear(self):
        """
        clear editor.
        """
        self.editor.clear()

    # ==================================================
    @property
    def validator_list(self):
        """
        available validator list.

        Returns:
            list: validator list.
        """
        return self.editor.validator_list


# ==================================================
class Label(QWidget):
    """
    label widget with the same size as editor.
    """

    # ==================================================
    def __init__(self, label="", parent=None):
        """
        initialize the class.

        Args:
            label (str, optional): label.
            parent (QWidget, optional): parent object.
        """
        super().__init__(parent)

        self.label = QLabel(label, self)
        self.label.setIndent(0)

        layout = QGridLayout()
        layout.setContentsMargins(0, 1, 0, 1)
        layout.setSpacing(3)
        layout.addWidget(self.label, 0, 0)

        self.setLayout(layout)

    # ==================================================
    def setText(self, text):
        self.label.setText(text)

    # ==================================================
    def setPixmap(self, pixmap):
        self.label.setPixmap(pixmap)

    # ==================================================
    def setAlignment(self, align):
        if align is None:
            return
        d = {"left": Qt.AlignLeft, "center": Qt.AlignCenter, "right": Qt.AlignRight}
        self.label.setAlignment(d[align] | Qt.AlignVCenter)
