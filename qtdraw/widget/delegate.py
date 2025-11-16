"""
Delegate for GroupModel and GroupView.

This module provides delegate for color selector, combo, and editor.
"""

from PySide6.QtWidgets import QStyle, QStyledItemDelegate
from PySide6.QtCore import Qt
from qtdraw.widget.custom_widget import Combo, Editor, ColorSelector


# ==================================================
class Delegate(QStyledItemDelegate):
    # ==================================================
    def __init__(self, parent):
        """
        Base delegate.

        Args:
            parent (QWidget): parent.
        """
        super().__init__(parent)

    # ==================================================
    def setEditorData(self, editor, index):
        """
        Set editor data.

        Args:
            editor (QWidget): editor.
            index (QModelIndex): index.
        """
        value = index.model().data(index, Qt.EditRole)
        editor.setCurrentText(value)

    # ==================================================
    def setModelData(self, editor, model, index):
        return  # set model data by using signal.

    # ==================================================
    def updateEditorGeometry(self, editor, option, index):
        """
        Update editor geometry.

        Args:
            editor (QWidget): editor.
            option (QStyleOptionViewItem) option.
            index (QModelIndex): index.
        """
        editor.setGeometry(option.rect.adjusted(5, 7, -5, 0))

    # ==================================================
    def paint(self, painter, option, index):
        """
        Paint cell (need to highlight selection).

        Args:
            painter (QPainter): painter.
            option (QStyleOptionViewItem) option.
            index (QModelIndex): index.
        """
        if index.isValid():
            value = index.model().data(index, Qt.DisplayRole)
            if value:
                option.displayAlignment = Qt.AlignHCenter | Qt.AlignVCenter
                self.parent().style().drawControl(QStyle.CE_ItemViewItem, option, painter, self.parent())


# ==================================================
class ComboDelegate(Delegate):
    # ==================================================
    def __init__(self, parent, default, option):
        """
        Create delegate for Combo.

        Args:
            parent (QWidget): parent.
            default (str): Combo default.
            option (tuple): Cobo option.
        """
        super().__init__(parent)
        self.default = default
        self.option = option

    # ==================================================
    def createEditor(self, parent, option, index):
        """
        Create combobox.

        Args:
            parent (QWidget): parent.
            option (QStyleOptionViewItem): option.
            index (QModelIndex): index.

        Returns:
            - (Combo) -- combo widget.
        """
        combo = Combo(parent, self.option, self.default)
        combo.currentTextChanged.connect(lambda data: index.model().setData(index, data))
        return combo


# ==================================================
class ColorDelegate(Delegate):
    # ==================================================
    def __init__(self, parent, default, option):
        """
        Create delegate for ColorSelector.

        Args:
            parent (QWidget): parent.
            default (str): ColorSelector default.
            option (tuple): ColorSelector option.
        """
        super().__init__(parent)
        self.default = default
        self.option = option

    # ==================================================
    def createEditor(self, parent, option, index):
        """
        Create color selector.

        Args:
            parent (QWidget): parent.
            option (QStyleOptionViewItem): option.
            index (QModelIndex): index.

        Returns:
            - (ColorSelector) -- color selector widget.
        """
        color_selector = ColorSelector(parent, self.default, self.option)
        color_selector.currentTextChanged.connect(lambda data: index.model().setData(index, data))

        return color_selector


# ==================================================
class EditorDelegate(Delegate):
    # ==================================================
    def __init__(self, parent, default, option, t, color, size, dpi):
        """
        Create delegate for Editor.

        Args:
            parent (QWidget): parent.
            default (str): Editor default.
            option (tuple): Editor option.
            t (str): Editor type.
            color (str): Editor color.
            size (int): Editor size.
            dpi (int): Editor dpi.
        """
        super().__init__(parent)
        self.default = default
        self.option = option
        self.type = t
        self.color = color
        self.size = size
        self.dpi = dpi

    # ==================================================
    def createEditor(self, parent, option, index):
        """
        Create editor.

        Args:
            parent (QWidget): parent.
            option (QStyleOptionViewItem): option.
            index (QModelIndex): index.

        Returns:
            - (Editor) -- editor widget.
        """
        editor = Editor(parent, self.default, (self.type, self.option), self.color, self.size, self.dpi)

        editor.returnPressed.connect(lambda data: index.model().setData(index, data))
        return editor

    # ==================================================
    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect.adjusted(5, 0, -5, 0))
