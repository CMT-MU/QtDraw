"""
Delegate for GroupModel and GroupView.

This module provides delegate for color selector, combo, and editor.
"""

from PySide6.QtWidgets import QStyledItemDelegate, QStyle
from PySide6.QtCore import Qt

from qtdraw.widget.custom_widget import Combo, Editor, ColorSelector


# ==================================================
class Delegate(QStyledItemDelegate):
    # ==================================================
    def __init__(self, parent):
        super().__init__(parent)

    # ==================================================
    def setEditorData(self, editor, index):
        value = index.data(Qt.EditRole)
        editor.setCurrentText(value)

    # ==================================================
    def setModelData(self, editor, model, index):
        return

    # ==================================================
    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect.adjusted(5, 7, -5, 0))

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
class EditorDelegate(Delegate):
    # ==================================================
    def __init__(self, parent, default, option, t, color, size):
        super().__init__(parent)
        self.default = default
        self.option = option
        self.type = t
        self.color = color
        self.size = size

    # ==================================================
    def createEditor(self, parent, option, index):
        model = index.model()
        editor = Editor(parent, self.default, (self.type, self.option), color=self.color, size=self.size)
        editor.returnPressed.connect(lambda data: model.setData(index, data))
        return editor

    # ==================================================
    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect.adjusted(5, 0, -5, 0))
