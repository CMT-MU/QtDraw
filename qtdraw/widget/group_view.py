"""
View panel for GroupModel.

This module provides a view class to show object data.
By clicking right button of mouse, the context menu appears.
"""

from PySide6.QtWidgets import QMenu, QTreeView, QHeaderView
from PySide6.QtCore import Qt, Signal, QPoint, QModelIndex, QItemSelection, QItemSelectionModel, QObject, QEvent
from qtdraw.core.pyvista_widget_setting import COLOR_WIDGET, COMBO_WIDGET, EDITOR_WIDGET, HIDE_TYPE
from qtdraw.widget.delegate import ColorDelegate, ComboDelegate, EditorDelegate


# ==================================================
class GroupView(QTreeView):
    selectionChanged = Signal(str, list, list)  # name, deselect, select.

    # ==================================================
    def __init__(self, model, parent=None, use_delegate=True):
        """
        Group view.

        Args:
            model (GroupModel): group model.
            parent (QWidget, optional): parent.
        """
        super().__init__(parent)

        # for debug.
        self._debug = {"delegate": use_delegate, "hide": True, "raw_data": False}

        # set model.
        self.setModel(model)

        # set delegate.
        if self._debug["delegate"]:
            for c, t in enumerate(self.model().column_type):
                if t in COLOR_WIDGET:
                    default = self.model().column_default[c]
                    option = t
                    self.setItemDelegateForColumn(c, ColorDelegate(self, default, option))
                elif t in COMBO_WIDGET:
                    default = self.model().column_default[c]
                    option = self.model().column_option[c]
                    self.setItemDelegateForColumn(c, ComboDelegate(self, default, option))
                elif t in EDITOR_WIDGET:
                    default = self.model().column_default[c]
                    option = self.model().column_option[c]
                    if hasattr(model.parent(), "_preference"):
                        color = model.parent()._preference["latex"]["color"]
                        size = model.parent()._preference["latex"]["size"]
                        dpi = model.parent()._preference["latex"]["dpi"]
                    else:
                        color, size, dpi = "black", 11, 120
                    self.setItemDelegateForColumn(c, EditorDelegate(self, default, option, t, color, size, dpi))

        # set properties.
        self.setAlternatingRowColors(True)
        self.header().setSectionsMovable(False)
        for column in range(self.model().columnCount()):
            self.header().setSectionResizeMode(column, QHeaderView.ResizeToContents)
        self.header().setDefaultAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        # hide columns.
        if self._debug["hide"]:
            for column, role in enumerate(self.model().column_type):
                if role in HIDE_TYPE:
                    self.header().setSectionHidden(column, True)

        # context menu.
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.context_menu)

        # connection to update widget.
        if self._debug["delegate"]:
            self.model().updateWidget.connect(self.update_widget)
            self.update_widget(force=True)

        self.selectionModel().selectionChanged.connect(self.selection_changed)

        self.clear_selection()

    # ==================================================
    def clear_selection(self):
        """
        Clear selection.
        """
        self.clearFocus()
        self.clearSelection()
        self.setCurrentIndex(QModelIndex())
        self.setFocus()

    # ==================================================
    def mousePressEvent(self, event):
        """
        Mouse press event for focus or clear selection.
        """
        self.setFocus()
        # in order to deselect when click point has no item.
        position = event.position()
        point = QPoint(int(position.x()), int(position.y()))
        index = self.indexAt(point)
        if not index.isValid():
            self.clear_selection()
        super().mousePressEvent(event)

    # ==================================================
    def keyPressEvent(self, event):
        """
        Key press event for ESC and up and down keys.
        """
        # in order to deselect by ESC key.
        if event.key() == Qt.Key_Escape:
            self.clear_selection()
        # in order to deselect when arrow key selection goes outside.
        elif event.key() in [Qt.Key_Up, Qt.Key_Down]:
            current_indexes = self.selectionModel().selectedIndexes()

            if len(current_indexes) == 0:
                super().keyPressEvent(event)
                return

            first_index = current_indexes[0]
            last_index = current_indexes[-1]

            if event.key() == Qt.Key_Up:
                next_index = self.indexAbove(first_index)
            elif event.key() == Qt.Key_Down:
                next_index = self.indexBelow(last_index)
            else:
                next_index = QModelIndex()

            if not next_index.isValid():
                self.clear_selection()
            else:  # for within range.
                super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)

    # ==================================================
    def context_menu(self, position):
        """
        Context menu.
        """
        index = self.indexAt(position)

        self.menu = QMenu(self)
        self.menu.addAction("insert", self.insert_row)
        if index.isValid():
            self.menu.addAction("copy", self.copy_row)
            self.menu.addAction("remove", self.remove_row)
        if self._debug["raw_data"]:
            self.menu.addAction("raw_data", lambda: print(self.model().tolist()))
        self.menu.exec(self.mapToGlobal(position))

    # ==================================================
    def insert_row(self):
        """
        Insert row.
        """
        indexes = self.selectedIndexes()
        idx = self.model().action_insert_row(indexes)
        if idx.isValid():
            self.expand(idx)

    # ==================================================
    def copy_row(self):
        """
        Copy row.
        """
        indexes = self.selectedIndexes()
        self.model().action_copy_row(indexes)

    # ==================================================
    def remove_row(self):
        """
        Remove row.
        """
        indexes = self.selectedIndexes()
        self.model().action_remove_row(indexes)

    # ==================================================
    def update_widget(self, force=False):
        """
        Update widget.
        """
        if self.isVisible() or force:
            self.blockSignals(True)
            self.setUpdatesEnabled(False)
            self.set_widget(self.model().invisibleRootItem())
            self.setUpdatesEnabled(True)
            self.blockSignals(False)
            self.hide()  # in order to refresh widget.
            self.show()

    # ==================================================
    def set_widget(self, item):
        """
        Set widget.

        Args:
            item (QStandardItem): item.
        """
        for row in range(item.rowCount()):
            child = item.child(row)
            if child:
                for column in self.model().column_widget:
                    index = self.model().index(child.row(), column, self.model().parent(self.model().indexFromItem(child)))
                    self.closePersistentEditor(index)
                    self.openPersistentEditor(index)
                self.set_widget(child)

    # ==================================================
    def selection_changed(self, selected, deselected):
        """
        For Selection changed.

        Args:
            selected (list): selected indexes.
            deselected (list): deselected indexes.
        """
        model = self.model()

        deselected = [i for i in deselected.indexes() if i.column() == 0]
        if deselected:
            index0 = deselected[0]
            row_data0 = []
            if model.rowCount(index0) == 0:
                row_data0.append(model.get_row_data(index0))
            else:
                for row in range(model.rowCount(index0)):
                    cindex0 = model.index(row, 0, index0)
                    row_data0.append(model.get_row_data(cindex0))
        else:
            row_data0 = None

        selected = [i for i in selected.indexes() if i.column() == 0]
        if selected:
            index1 = selected[0]
            row_data1 = []
            if model.rowCount(index1) == 0:
                row_data1.append(model.get_row_data(index1))
            else:
                for row in range(model.rowCount(index1)):
                    cindex1 = model.index(row, 0, index1)
                    row_data1.append(model.get_row_data(cindex1))
        else:
            row_data1 = None

        self.selectionChanged.emit(model.group_name, row_data0, row_data1)

    # ==================================================
    def select_row(self, index):
        """
        Select row.

        Args:
            index (QModelIndex): index.
        """
        index = index.siblingAtColumn(0)
        if index.parent().isValid():  # in case of child.
            self.expand(index.parent())
        index1 = index.siblingAtColumn(self.model().columnCount() - 1)
        selection = QItemSelection(index, index1)  # all columns.
        self.selectionModel().select(selection, QItemSelectionModel.ClearAndSelect)
