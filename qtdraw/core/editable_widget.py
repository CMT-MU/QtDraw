from qtpy.QtGui import QPixmap, QIcon
from qtpy.QtWidgets import (
    QWidget,
    QLabel,
    QCheckBox,
    QHBoxLayout,
    QBoxLayout,
    QButtonGroup,
    QRadioButton,
    QComboBox,
    QFrame,
    QSizePolicy,
)
from gcoreutils.convert_util import text_to_list, text_to_sympy, sympy_to_latex
from gcoreutils.nsarray import NSArray
from qtdraw.core.color_palette import color2pixmap, _color2pixmap
from qtdraw.core.pixmap_converter import latex2pixmap
from qtdraw.core.line_edit import LineEditor, Label


# ==================================================
class EditableWidget(QWidget):
    def __init__(self, label=None, callback=None, parent=None):
        super().__init__(parent)
        if callback is None:
            callback = self.default_callback

        self.editor = None
        self.inedit = False
        self.callback = callback

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(15, 3, 15, 3)
        self.layout.setSpacing(3)

        if label is not None:
            self.label = Label(parent=self)
            self.setLabel(label)
            self.layout.addWidget(self.label)

        self.setLayout(self.layout)

    # ==================================================
    def set_editor(self, label="", init="", validator=None, decimal=4, check_var=None, callback=None):
        if label is None:
            self.editor = None
        else:
            self.editor = LineEditor(label, init, validator, decimal, check_var, callback, self)
            self.editor.setWindowTitle("Input Panel")
            self.editor.layout.setContentsMargins(3, 3, 3, 3)
            self.editor.resize(600, 2 * self.label.height())
            self.editor.hide()
            self.editor.closeEdit.connect(self.close_edit)
            self.editor.acceptEdit.connect(self.accept_edit)

    # ==================================================
    def setLabel(self, label):
        self.label.setText(label)

    # ==================================================
    def mouseDoubleClickEvent(self, event):
        if self.editor is not None and not self.inedit:
            self.inedit = True
            self.label.hide()
            self.editor.show()
            self.editor.editor.setFocus()

    # ==================================================
    def close_edit(self):
        self.editor.hide()
        self.label.show()
        self.inedit = False

    # ==================================================
    def accept_edit(self):
        self.setLabel(self.editor.text())
        self.close_edit()

    # ==================================================
    def default_callback(self, text):
        print(text)
        return True

    # ==================================================
    def __str__(self):
        return "Widget: " + self.label.text()


# ==================================================
class QtColorSelector(EditableWidget):
    """
    color selector widget.
    """

    # ==================================================
    def __init__(self, current="", color_type="color", callback=None, parent=None):
        """
        initialize the class.

        Args:
            current (str, optional): default color.
            color_type (str, optional): color/colormap/color_both
            callback (function, optional): callback function to get color name, f(name).
            parent (QWidget, optional): parent.

        Notes:
            - callback is f(colorname).
        """
        super().__init__(callback=callback, parent=parent)

        size = self.font().pointSize()

        color_pixmap, separator = color2pixmap(color_type, size)
        names = list(color_pixmap.keys())

        if current == "" or current is None:
            current = names[0]

        try:
            current = names.index(current)
        except ValueError:
            current = 0

        combo = QComboBox(self)
        combo.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        for s, c in color_pixmap.items():
            combo.addItem(QIcon(c), s, self)
        combo.setCurrentIndex(current)

        combo.setIconSize(next(iter(color_pixmap.values())).size())

        for i in separator:
            combo.insertSeparator(i)

        self.layout.addWidget(combo)

        def _callback(txt):
            self.callback(txt)
            return True

        combo.currentTextChanged.connect(_callback)


# ==================================================
class QtCheckBox(EditableWidget):
    """
    check box widget.
    """

    # ==================================================
    def __init__(self, label=None, current=True, callback_check=None, callback_label=None, read_only=False, parent=None):
        """
        initialize the class.

        Args:
            label (str, optional): label for check box.
            current (bool, optional): default status.
            callback_check (function, optional): callback function to get check status.
            callback_label (function, optional): callback function to get label.
            read_only (bool, optional): read only ?
            parent (QWidget, optional): parent.

        Notes:
            - callback is f(flag). If label makes editable, two callbacks f1(flag) and f2(text) are passed.
        """
        if callback_check is None:
            callback_check = self.default_check

        super().__init__(label, parent=parent)
        if callback_label is not None and label is not None and not read_only:
            self.set_editor(init=label, validator="latex", callback=callback_label)
            self.editor.setContentsMargins(3, 1, 0, 1)

        chkbox = QCheckBox("", self)
        sizePolicy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        chkbox.setSizePolicy(sizePolicy)

        if current:
            chkbox.setChecked(True)
        else:
            chkbox.setChecked(False)

        if label is None:
            self.layout.addWidget(chkbox)
        else:
            self.layout.insertWidget(0, chkbox)
            self.label.setContentsMargins(13, 1, 0, 1)

        chkbox.toggled.connect(callback_check)

    # ==================================================
    def default_check(self, flag):
        print(flag)


# ==================================================
class QtRadioGroup(EditableWidget):
    """
    radio group widget.
    """

    # ==================================================
    def __init__(self, lst, current=0, vertical=False, callback=None, parent=None):
        """
        initialize the class.

        Args:
            lst (list): radio group text.
            current (int, optional): default index.
            vertical (bool, optional): align vertically ?
            callback (function, optional): callback function to get selected text, f(text).
            parent (QWidget, optional): parent.

        Notes:
            - callback is f(lst_index).
        """
        self.lst = lst

        super().__init__(callback=callback, parent=parent)

        if vertical:
            self.layout.setDirection(QBoxLayout.TopToBottom)

        self.select = QButtonGroup(self)
        for no, i in enumerate(lst):
            btn = QRadioButton(i, self)
            self.select.addButton(btn)
            if no == current:
                btn.setChecked(True)
            self.layout.addWidget(btn)

        def _callback(btn):
            no = self.lst.index(btn.text())
            self.callback(no)
            return True

        self.select.buttonClicked.connect(_callback)


# ==================================================
class QtComboBox(EditableWidget):
    """
    combo box widget.
    """

    # ==================================================
    def __init__(self, lst, current=0, callback=None, parent=None):
        """
        initialize the class.

        Args:
            lst (list): combo box text.
            current (int, optional): default index.
            callback (function, optional): callback function to get selected text, f(text).
            parent (QWidget, optional): parent.

        Notes:
            - callback is f(lst_index).
        """
        self.lst = lst

        super().__init__(callback=callback, parent=parent)

        combo = QComboBox(self)
        for s in lst:
            combo.addItem(s, self)
        combo.setCurrentIndex(current)

        self.layout.addWidget(combo)

        def _callback(txt):
            no = self.lst.index(txt)
            self.callback(no)
            return True

        combo.currentTextChanged.connect(_callback)


# ==================================================
class QtImage(EditableWidget):
    """
    image widget.
    """

    # ==================================================
    def __init__(self, label, width=100, callback=None, read_only=False, parent=None):
        """
        initialize the class.

        Args:
            label (str): file name of image.
            width (int, optional): width.
            callback (function, optional): callback when editable=True.
            read_only (bool, optional): read only ?
            parent (QWidget, optional): parent.

        Notes:
            - callback is f(filename).
        """
        self.w = width
        super().__init__(label, callback=callback, parent=parent)
        if not read_only:
            self.set_editor(init=label)

    # ==================================================
    def setLabel(self, label):
        # file existing check for label.
        pix = QPixmap(label)
        pix = pix.scaledToWidth(self.w)

        self.label.setPixmap(pix)


# ==================================================
class QtColorLabel(EditableWidget):
    """
    color label widget.
    """

    # ==================================================
    def __init__(self, label, parent=None):
        """
        initialize the class.

        Args:
            label (str): color or colormap name.
            parent (QWidget, optional): parent.
        """
        if label == "" or label is None:
            return

        super().__init__(label, parent=parent)

        size = self.font().pointSize()

        colorbox = _color2pixmap(label, "color_both", size)

        icon = QLabel(self)
        icon.setPixmap(colorbox)
        icon.setFrameStyle(QFrame.Box)
        icon.setFixedSize(colorbox.size())

        self.layout.insertWidget(0, icon)
        self.label.setContentsMargins(3, 1, 0, 1)


# ==================================================
class QtText(EditableWidget):
    """
    text widget.
    """

    # ==================================================
    def __init__(self, label, callback=None, validator=None, decimal=4, check_var=None, read_only=False, align=None, parent=None):
        """
        initialize the class.

        Args:
            label (str): text.
            callback (function, optional): callback function to get input, f(input).
            validator (str, optional): validator.
            decimal (int, optional): digit for floating number.
            check_var (list, optional): acceptable variables.
            read_only (bool, optional): read only ?
            align (str, optional): alignment, "left/center/right".
            parent (QWidget, optional): parent.
        """
        if align is None:
            align = "left"
        label = str(label).replace("'", "")
        self.validator = validator
        super().__init__(label, parent=parent)

        if callback is not None and not read_only:
            self.set_editor(init=label, validator=validator, decimal=decimal, check_var=check_var, callback=callback)
            self.setLabel(self.editor.text(), align)
        else:
            self.setLabel(label, align)

    # ==================================================
    def setLabel(self, label, align=None):
        if self.validator in [
            "s_row",
            "s_vector",
            "i_row",
            "i_pos_row",
            "i_vector",
            "i_pos_vector",
            "r_row",
            "r_pos_row",
            "r_vector",
            "r_pos_vector",
        ]:
            text = text_to_list(label)
            text = "[" + ", ".join(map(lambda i: str(i).strip(" "), text)) + "]"
        elif self.validator in [
            "s_column",
            "i_column",
            "i_pos_column",
            "r_column",
            "r_pos_column",
            "s_column_vector",
            "i_column_vector",
            "i_pos_column_vector",
            "r_column_vector",
            "r_pos_column_vector",
        ]:
            text = text_to_list(label)
            text = "\n".join(map(lambda i: str(i).strip(" "), text))
        elif self.validator in [
            "s_matrix",
            "s_vector_list",
            "i_matrix",
            "i_pos_matrix",
            "i_vector_list",
            "i_pos_vector_list",
            "r_matrix",
            "r_pos_matrix",
            "r_vector_list",
            "r_pos_vector_list",
        ]:
            text = text_to_list(label)
            text = "\n".join(["[" + ", ".join(map(lambda j: str(j).strip(" "), i)) + "]" for i in text])
        else:
            text = label

        self.label.setText(text)
        self.label.setAlignment(align)


# ==================================================
class QtMath(EditableWidget):
    """
    math widget.

    References:
        - Render TeX to SVG in Python using matplotlib and display with PyQt
        - https://gist.github.com/gmarull/dcc8218385014559c1ca46047457c364
    """

    # ==================================================
    def __init__(
        self,
        label,
        callback=None,
        validator=None,
        check_var=None,
        color="black",
        style="svg",
        dpi=300,
        read_only=False,
        align=None,
        parent=None,
    ):
        """
        initialize the class.

        Args:
            label (str or list): that can be conveted to sympy.
            callback (function, optional): callback function to get input, f(input).
            validator (str, optional): scalar/row/column/matrix.
            check_var (list, optional): acceptable variables.
            color (str, optional): color name.
            style (str, optional): pixmap style, "svg/png/jpg".
            dpi (int, optional): DPI of image.
            read_only (bool, optional): read only ?
            align (str, optional): alignment, "left/center/right".
            parent (QWidget, optional): parent.
        """
        if align is None:
            align = "left"
        if label is None:
            return
        if validator not in [None, "s_scalar", "s_row", "s_column", "s_matrix", "s_vector", "s_column_vector", "s_vector_list"]:
            return

        self.validator = validator
        self.color = color
        self.style = style
        self.dpi = dpi

        super().__init__(label, parent=parent)

        if callback is not None and not read_only:
            self.set_editor(init=label, validator=validator, check_var=check_var, callback=callback)
            self.setLabel(self.editor.text(), align)
        else:
            self.setLabel(label, align)

    # ==================================================
    def setLabel(self, label, align=None):
        if label == "":
            return
        if self.validator is not None:
            # latex = sympy_to_latex(text_to_sympy(label))
            latex = sympy_to_latex(NSArray(label).semi_evalf().tolist())
        else:
            latex = label

        size = self.font().pointSize()
        sp = r"\,\,\," if self.style == "svg" else ""

        if self.validator in ["s_row", "s_vector"]:
            latex = r"\begin{pmatrix}" + (r"&" + sp).join(latex) + r"\end{pmatrix}"
        elif self.validator in ["s_column", "s_column_vector"]:
            latex = (r"\begin{pmatrix}" + r"&".join(latex) + r"\end{pmatrix}").replace(r"&", r"\\")
        elif self.validator == "s_matrix":
            latex = r"\begin{pmatrix}" + r"\\".join([(r"&" + sp).join(i) for i in latex]) + r"\end{pmatrix}"
        elif self.validator == "s_vector_list":
            latex = (
                r"\begin{matrix}"
                + r"\\".join([r"\begin{pmatrix}" + (r"&" + sp).join(i) + r"\end{pmatrix}" for i in latex])
                + r"\end{matrix}"
            )

        pixmap = latex2pixmap(latex, size, self.color, self.dpi, self.style)
        if pixmap:
            self.label.setPixmap(pixmap)
            self.label.setAlignment(align)
