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
        """
        Set model data.

        Args:
            editor (QWidget): editor.
            model (QAbstractItemModel) model.
            index (QModelIndex): index.
        """
        model.blockSignals(True)
        model.setData(index, editor.currentText(), Qt.EditRole)
        model.blockSignals(False)

    # ==================================================
    def updateEditorGeometry(self, editor, option, index):
        """
        Update editor geometry.

        Args:
            editor (QWidget): editor.
            option (QStyleOptionViewItem) option.
            index (QModelIndex): index.
        """
        editor.setGeometry(option.rect)

    # ==================================================
    def paint(self, painter, option, index):
        """
        Paint cell.

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
    def __init__(self, parent):
        """
        Create delegate for Combo.

        Args:
            parent (QWidget): parent.
        """
        super().__init__(parent)

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
        c = index.column()
        dd = index.model().column_default[c]
        opt = index.model().column_option[c]
        combo = Combo(parent, opt, dd)
        combo.setStyleSheet("margin: 5px 10px 5px 10px; padding: 0px 5px 0px 5px;")
        combo.currentTextChanged.connect(lambda data: index.model().setData(index, data))
        return combo


# ==================================================
class ColorDelegate(Delegate):
    # ==================================================
    def __init__(self, parent):
        """
        Create delegate for ColorSelector.

        Args:
            parent (QWidget): parent.
        """
        super().__init__(parent)

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
        c = index.column()
        dd = index.model().column_default[c]
        tp = index.model().column_type[c]
        color_selector = ColorSelector(parent, dd, tp)
        color_selector.setStyleSheet("margin: 5px 10px 5px 10px; padding: 0px 5px 0px 5px;")
        color_selector.currentTextChanged.connect(lambda data: index.model().setData(index, data))

        return color_selector


# ==================================================
class EditorDelegate(Delegate):
    # ==================================================
    def __init__(self, parent):
        """
        Create delegate for Editor.

        Args:
            parent (QWidget): parent.
        """
        super().__init__(parent)

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
        model = index.model()
        c = index.column()
        dd = model.column_default[c]
        opt = model.column_option[c]
        tp = model.column_type[c]
        color = model.parent()._preference["latex"]["color"]
        size = model.parent()._preference["latex"]["size"]
        dpi = model.parent()._preference["latex"]["dpi"]
        editor = Editor(parent, dd, (tp, opt), color, size, dpi)

        editor.returnPressed.connect(lambda data: index.model().setData(index, data))
        return editor
