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
    def updateEditorGeometry(self, editor, option, index):
        rect = option.rect
        size = editor.sizeHint()

        width = size.width()
        height = size.height()

        max_width = rect.width() - 2 * self.padding
        max_height = rect.height() - 2 * self.padding
        width = min(width, max_width)
        height = min(height, max_height)

        x = rect.x() + (rect.width() - width) // 2
        y = rect.y() + (rect.height() - height) // 2

        editor.setGeometry(QRect(x, y, width, height))

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
    def sizeHint(self, option, index):
        sz = super().sizeHint(option, index)
        w, h = 6 * self.padding, self.padding
        return QSize(sz.width() + w, sz.height() + h)


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
    def sizeHint(self, option, index):
        sz = super().sizeHint(option, index)
        w, h = 6 * self.padding, self.padding
        return QSize(sz.width() + w, sz.height() + h)


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
        editor.returnPressed.connect(lambda data: model.setData(index, data))
        return editor

    # ==================================================
    def sizeHint(self, option, index):
        sz = super().sizeHint(option, index)
        w, h = 2 * self.padding, 4 * self.padding
        return QSize(sz.width() + w, sz.height() + h)
