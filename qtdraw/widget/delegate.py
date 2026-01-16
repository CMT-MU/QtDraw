"""
Delegate for GroupModel and GroupView.

This module provides delegate for color selector, combo, and editor.
"""

from PySide6.QtWidgets import QStyledItemDelegate, QStyle
from PySide6.QtCore import Qt, QSize, QRect

from qtdraw.widget.custom_widget import Combo, Editor, ColorSelector


# ==================================================
class Delegate(QStyledItemDelegate):
    # ==================================================
    def __init__(self, parent):
        super().__init__(parent)
        self.padding = 5

    # ==================================================
    def setEditorData(self, editor, index):
        value = index.data(Qt.EditRole)
        editor.setCurrentText(value)

    # ==================================================
    def setModelData(self, editor, model, index):
        return

    # ==================================================
    def paint(self, painter, option, index):
        if index.isValid():
            value = index.model().data(index, Qt.DisplayRole)
            if value:
                option.displayAlignment = Qt.AlignHCenter | Qt.AlignVCenter
                self.parent().style().drawControl(QStyle.CE_ItemViewItem, option, painter, self.parent())


# ==================================================
class ComboDelegate(Delegate):
    # ==================================================
    def __init__(self, parent, default, option):
        super().__init__(parent)
        self.default = default
        self.option = option

    # ==================================================
    def createEditor(self, parent, option, index):
        model = index.model()
        editor = Combo(parent, self.option, self.default)
        editor.currentTextChanged.connect(lambda data: model.setData(index, data))
        return editor

    # ==================================================
    def updateEditorGeometry(self, editor, option, index):
        rect = option.rect
        size = editor.sizeHint()

        width = size.width() + self.padding
        height = size.height() - self.padding

        x = rect.x() + (rect.width() - width) // 2
        y = rect.y() + (rect.height() - height) // 2

        editor.setGeometry(QRect(x, y, width, height))

    # ==================================================
    def sizeHint(self, option, index):
        sz = super().sizeHint(option, index)
        w, h = sz.width() + 6 * self.padding, sz.height() + 2 * self.padding
        return QSize(w, h)


# ==================================================
class ColorDelegate(Delegate):
    # ==================================================
    def __init__(self, parent, default, option):
        super().__init__(parent)
        self.default = default
        self.option = option

    # ==================================================
    def createEditor(self, parent, option, index):
        model = index.model()
        editor = ColorSelector(parent, self.default, self.option)
        editor.currentTextChanged.connect(lambda data: model.setData(index, data))
        return editor

    # ==================================================
    def updateEditorGeometry(self, editor, option, index):
        rect = option.rect
        size = editor.sizeHint()

        width = size.width() - 2 * self.padding
        height = size.height() - self.padding

        x = rect.x() + (rect.width() - width) // 2
        y = rect.y() + (rect.height() - height) // 2

        editor.setGeometry(QRect(x, y, width, height))

    # ==================================================
    def sizeHint(self, option, index):
        sz = super().sizeHint(option, index)
        w, h = sz.width() + 6 * self.padding, sz.height() + 2 * self.padding
        return QSize(w, h)


# ==================================================
class EditorDelegate(Delegate):
    # ==================================================
    def __init__(self, parent, default, option, t, color, size, mathjax):
        super().__init__(parent)
        self.default = default
        self.option = option
        self.type = t
        self.color = color
        self.size = size
        self.mathjax = mathjax

    # ==================================================
    def createEditor(self, parent, option, index):
        model = index.model()
        editor = Editor(parent, self.default, (self.type, self.option), color=self.color, size=self.size, mathjax=self.mathjax)
        editor.returnPressed.connect(lambda data: self._set_data_size(editor, model, index, data))
        return editor

    # ==================================================
    def _set_data_size(self, editor, model, index, data):
        model.setData(index, data)
        h = editor.sizeHint().height() + 2 * self.padding
        editor.setFixedHeight(h)
        view = self.parent()
        view.set_row_height_hint(index.row(), h)

    # ==================================================
    def updateEditorGeometry(self, editor, option, index):
        rect = option.rect
        size = editor.sizeHint()

        width = size.width()
        height = size.height() + 2 * self.padding

        x = rect.x() + (rect.width() - width) // 2
        y = rect.y() + (rect.height() - height) // 2

        editor.setGeometry(QRect(x, y, width, height))

    # ==================================================
    def sizeHint(self, option, index):
        view = self.parent()
        h = view.row_height_hint(index.row())
        if h is not None:
            w = super().sizeHint(option, index).width() + 2 * self.padding
            return QSize(w, h)
        return super().sizeHint(option, index)
