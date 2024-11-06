"""
Two-layer tree model for managing objects.

This module provides a class to manage objects to draw.
The objects are grouped by the first column, "name".
All the objects in the same group can be modified together.
When there are more than two objects in the same group,
a child tree appears and the parent tree is the same as
the first row of the child tree.

The raw data is maintained by dict, and the index model
is just to keep the relation between parent and child,
which is necessary to use other Qt functionalities.
"""

import copy
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Signal, Qt, QModelIndex, QTimer
from qtdraw.core.pyvista_widget_setting import CUSTOM_WIDGET
from qtdraw.core.pyvista_widget_setting import COLUMN_NAME_ACTOR, COLUMN_LABEL_ACTOR


# ==================================================
class GroupModel(QStandardItemModel):
    updateWidget = Signal()  # update widget when append/remove rows.
    updateData = Signal(str, list, int, QModelIndex)  # name, row_data, role, index.

    # data/check state changed signal for user.
    dataRemoved = Signal(str, list, QModelIndex)  # object_type, row_data, index.
    dataModified = Signal(str, list, QModelIndex)  # object_type, row_data, index.
    checkChanged = Signal(str, list, QModelIndex)  # object_type, row_data, index.

    # role.
    AppendRow = Qt.UserRole + 11
    RemoveRow = Qt.UserRole + 12
    MoveRow = Qt.UserRole + 13

    # ==================================================
    def __init__(self, name, column_info, parent=None):
        """
        Group data model (2 layer parent-child tree model).

        Args:
            name (str): model name.
            column_info (list): {header: (type,option,default)} for each column.
            parent (QWidget, optional): parent.
        """
        super().__init__(parent)
        self._name = name
        self._update_widget = True

        self.setHorizontalHeaderLabels(column_info.keys())
        self.column_type = []
        self.column_option = []
        self.column_default = []
        for c_type, c_option, c_default in column_info.values():
            self.column_type.append(c_type)
            self.column_option.append(c_option)
            self.column_default.append(c_default)

        self.column_widget = [i for i, c in enumerate(self.column_type) if c in CUSTOM_WIDGET]

        self.dataChanged.connect(self.update_check_state)  # to modify bool data in column+1.
        self.updateData.connect(self.emit_update_data)

    # ==================================================
    @property
    def group_name(self):
        """
        Group name.

        Returns:
            - (str) -- group name.
        """
        return self._name

    # ==================================================
    @property
    def header(self):
        """
        Header label.

        Returns:
            - (list) -- header label.
        """
        return [self.headerData(c, Qt.Horizontal) for c in range(self.columnCount())]

    # ==================================================
    def block_update_widget(self, flag):
        """
        Block update widget.

        Args:
            flag (bool): block update ?

        Note:
            - in order to avoid unnecessary update of widget, otherwise it becomes very slow.
        """
        self._update_widget = not flag
        if not flag:
            self.updateWidget.emit()

    # ==================================================
    def is_parent(self, index):
        """
        Is parent index ?

        Args:
            index (QModelIndex): index.

        Returns:
            - (bool) -- parent index ?
        """
        depth = 0
        idx = index
        while idx.isValid():
            idx = idx.parent()
            depth += 1
        return depth == 1

    # ==================================================
    def update_check_state(self, topLeft, bottomRight, roles=[]):
        """
        Update check state data.

        Args:
            topLeft (QModelIndex): top left index.
            bottomRight (QModelIndex): bottom right index.
            roles (list, optional): list of roles.

        Note:
            - set check state (bool) in column+1.
        """
        if not Qt.CheckStateRole in roles:
            return

        for row in range(topLeft.row(), bottomRight.row() + 1):
            col = topLeft.column()
            index = self.index(row, col, topLeft.parent())
            index1 = self.index(row, col + 1, topLeft.parent())
            value = self.data(index, Qt.CheckStateRole)
            state = str(Qt.CheckState(value) == Qt.Checked)
            super().setData(index1, state)

    # ==================================================
    def set_data(self, data):
        """
        Set data from list data.

        Args:
            - (list) -- set data from string.
        """
        for row_data in data:
            self.append_row(row_data)

    # ==================================================
    def set_row_data(self, index, column, data):
        """
        Set row data.

        Args:
            index (QModelIndex): index.
            column (int): column.
            data (str): data.
        """
        self.blockSignals(True)
        super().setData(index.siblingAtColumn(column), data, Qt.EditRole)
        self.blockSignals(False)

    # ==================================================
    def set_check(self, index, column, data):
        """
        Set check state.

        Args:
            index (QModelIndex): index.
            column (int): column.
            data (QCheckState): check state.
        """
        index_c = index.siblingAtColumn(column)
        self.setData(index_c, data, Qt.CheckStateRole)

    # ==================================================
    def tolist(self):
        """
        Convert to list.

        Args:
            raw (bool, optional): raw data ?

        Returns:
            - (list) -- list data.
        """
        root_item = self.invisibleRootItem()
        data = []
        for parent_row in range(root_item.rowCount()):
            item = root_item.child(parent_row)
            if item.hasChildren():
                for row in range(item.rowCount()):
                    row_data = self.get_row_data(item.child(row).index())
                    data.append(row_data)
            else:
                row_data = self.get_row_data(root_item.child(parent_row).index())
                data.append(row_data)

        return data

    # ==================================================
    def emit_update_all(self):
        """
        Emit update for all data.
        """
        name = self.group_name
        root_item = self.invisibleRootItem()
        for parent_row in range(root_item.rowCount()):
            item = root_item.child(parent_row)
            if item.hasChildren():
                for row in range(item.rowCount()):
                    index = item.child(row).index()
                    row_data = self.get_row_data(index)
                    self.dataModified.emit(name, row_data, index)
            else:
                index = root_item.child(parent_row).index()
                row_data = self.get_row_data(index)
                self.dataModified.emit(name, row_data, index)

    # ==================================================
    def find_item(self, text, column=0, child=True):
        """
        Find item.

        Args:
            text (str): str to find.
            column (int, optional): column.
            child (bool, optional): find also for child ?

        Returns:
            - (list) -- found items.
        """
        found = []

        parent_item = self.invisibleRootItem()
        for row in range(parent_item.rowCount()):
            item = parent_item.child(row, column)
            if item and item.data(Qt.EditRole) == text:
                found.append(item)

            if child:
                item0 = parent_item.child(row, 0)
                for row in range(item0.rowCount()):
                    item1 = item0.child(row, column)
                    if item1 and item1.data(Qt.EditRole) == text:
                        found.append(item1)

        return found

    # ==================================================
    def set_check_state(self, item, row_data):
        """
        Set check state of row.

        Args:
            item (QItemModel): item of row(s).
            row_data (list): row data, [str].
        """
        for column in range(self.columnCount()):
            itemc = item[column]
            if self.column_type[column] == "check":
                itemc.setCheckable(True)
                if self.column_default[column] == "":
                    itemc.setEditable(False)
                state = str(row_data[column + 1]) == "True"
                if state:
                    itemc.setCheckState(Qt.Checked)
                else:
                    itemc.setCheckState(Qt.Unchecked)

    # ==================================================
    def get_row_data(self, index, column=None):
        """
        Get row data.

        Args:
            index (QModelIndex): index.
            column (int, optional): column.

        Returns:
            - (list) -- row data.

        Note:
            - bool string is replaced by bool.
        """
        if column is None:
            row_data = [self.itemFromIndex(index.siblingAtColumn(c)).data(Qt.EditRole) for c in range(self.columnCount())]
            row_data = [i == "True" if self.column_type[c] == "bool" else i for c, i in enumerate(row_data)]
        else:
            row_data = self.itemFromIndex(index.siblingAtColumn(column)).data(Qt.EditRole)
            if self.column_type[column] == "bool":
                row_data = row_data == "True"
        return row_data

    # ==================================================
    def emit_update_data(self, name, row_data, role, index):
        """
        Emit update data.

        Args:
            name (str): group name.
            row_data (list): row_data.
            role (int): role.
            index (QModelIndex): index.
        """
        if role in [Qt.EditRole, GroupModel.AppendRow]:
            self.dataModified.emit(name, row_data, index)
        elif role in [GroupModel.RemoveRow]:
            self.dataRemoved.emit(name, row_data, index)
        elif role in [Qt.CheckStateRole]:
            self.checkChanged.emit(name, row_data, index)

    # ==================================================
    def append_row(self, row_data=None, role=None, index=QModelIndex(), copy_row=False):
        """
        Append row.

        Args:
            row_data (list, optional): row data.
            role (int, optional): role.
            index (QModelIndex, optional): index.
            copy_row (bool, optional): copy from current index ?
        """
        if role is None:
            role = GroupModel.AppendRow

        # default.
        if row_data is None:
            row_data = copy.deepcopy(self.column_default)

        if len(row_data) != self.columnCount():
            return

        # insert copy or default.
        if index != QModelIndex():
            if copy_row:
                row_data = self.get_row_data(index)
                row_data[COLUMN_NAME_ACTOR] = ""
                row_data[COLUMN_LABEL_ACTOR] = ""
            else:
                row_data[0] = self.get_row_data(index, 0)

        name = row_data[0]  # assume tuple at first column.
        parent_item = self.find_item(name, child=False)
        if len(parent_item) > 0:
            parent_item = parent_item[0]
        else:
            parent_item = None

        if parent_item is None:  #  new group.
            item = [QStandardItem(str(i)) for i in row_data]
            self.set_check_state(item, row_data)
            self.appendRow(item)
            self.updateData.emit(self.group_name, row_data, role, item[0].index())
        else:  # existing group.
            if not parent_item.hasChildren():  # no children.
                row = parent_item.row()
                row_data0 = [self.item(row, i).data(Qt.EditRole) for i in range(self.columnCount())]
                item = [QStandardItem(str(i)) for i in row_data0]
                self.set_check_state(item, row_data0)
                parent_item.appendRow(item)
            item = [QStandardItem(str(i)) for i in row_data]
            self.set_check_state(item, row_data)
            parent_item.appendRow(item)
            self.updateData.emit(self.group_name, row_data, role, item[0].index())

        if self._update_widget:
            self.updateWidget.emit()

    # ==================================================
    def remove_row(self, index, role=None):
        """
        Remove row.

        Args:
            index (QModelIndex): index.
            role (int, optional): role.
        """
        if not index.isValid():
            return
        if role is None:
            role = GroupModel.RemoveRow

        index = index.siblingAtColumn(0)
        item = self.itemFromIndex(index)

        if item.parent():  # child.
            row = index.row()
            n = item.parent().rowCount()
            if row == 0:  # copy 2nd child to parent.
                row_data = self.get_row_data(item.parent().child(1).index())
                for c, d in enumerate(row_data):
                    super().setData(self.item(item.parent().row(), c).index(), d)
            self.updateData.emit(self.group_name, self.get_row_data(index), role, index)
            if n == 2:
                if row == 1:  # copy 1st child to parent.
                    row_data = self.get_row_data(item.parent().child(0).index())
                    for c, d in enumerate(row_data):
                        super().setData(self.item(item.parent().row(), c).index(), d)
                self.removeRow(0, index.parent())  # remove 2nd child.
                self.removeRow(0, index.parent())  # remove first child.
            else:
                self.removeRow(row, index.parent())  # remove row child.
        else:  # parent.
            n = self.rowCount(index)
            for row in range(n):
                cindex = self.index(row, 0, index)
                self.updateData.emit(self.group_name, self.get_row_data(cindex), role, cindex)
            if n == 0:
                self.updateData.emit(self.group_name, self.get_row_data(index), role, index)
            self.removeRow(index.row(), index.parent())

        if self._update_widget:
            self.updateWidget.emit()

    # ==================================================
    def move_row(self, index, value):
        """
        Move row.

        Args:
            index (QModelIndex): index.
            value (QVariant): value.
        """
        cols = range(self.columnCount())
        if index.parent() == QModelIndex():  # parent.
            item = self.itemFromIndex(index)
            if item.hasChildren():
                to_move = []
                for row in range(item.rowCount()):
                    row_data = [item.child(row, c).data(Qt.EditRole) for c in cols]
                    row_data[0] = value
                    to_move.append(row_data)
                self.remove_row(index, GroupModel.MoveRow)
                for row_data in to_move:
                    self.append_row(row_data=row_data, role=GroupModel.MoveRow)
            else:
                to_move = [self.invisibleRootItem().child(index.row(), c).data(Qt.EditRole) for c in cols]
                to_move[0] = value
                self.remove_row(index, GroupModel.MoveRow)
                self.append_row(row_data=to_move, role=GroupModel.MoveRow)
        else:  # child.
            item = self.itemFromIndex(index.parent())
            to_move = [item.child(index.row(), c).data(Qt.EditRole) for c in cols]
            to_move[0] = value
            self.remove_row(index, GroupModel.MoveRow)
            self.append_row(row_data=to_move, role=GroupModel.MoveRow)

    # ==================================================
    # action.
    # ==================================================
    def action_copy_row(self, indexes):
        """
        Slot for copy row action.

        Args:
            indexes (list): list of index.
        """
        if len(indexes) == 0:
            return

        indexes = [index for index in indexes if index.column() == 0]
        for index in indexes:
            self.append_row(index=index, copy_row=True)

    # ==================================================
    def action_insert_row(self, indexes):
        """
        Slot for insert row action.

        Args:
            indexes (list): list of index.

        Returns:
            - (QModelIndex) -- parent index of inserted row.
        """
        if len(indexes) == 0:
            self.append_row()
        else:
            indexes = [index for index in indexes if index.column() == 0]
            for index in indexes:
                self.append_row(index=index)

        # return parent index of inserted row.
        last = self.rowCount(QModelIndex()) - 1
        child = self.index(last, 0, QModelIndex())
        if self.rowCount(child) > 0:
            return child
        else:
            return QModelIndex()

    # ==================================================
    def action_remove_row(self, indexes):
        """
        Slot for remove row action.

        Args:
            indexes (list): list of index.
        """
        if len(indexes) == 0:
            return

        indexes = [index for index in indexes if index.column() == 0]

        for index in indexes:
            self.remove_row(index)

    # ==================================================
    # override.
    # ==================================================
    def setData(self, index, value, role=Qt.EditRole):
        """
        Set data (override).

        Args:
            index (QModelIndex): index.
            value (QVariant): value to set.
            role (int, optional): role.

        Returns:
            - (bool) -- success to set data ?
        """
        # in case of no change.
        if value == self.data(index, role):
            return False

        # move.
        if role == Qt.EditRole and index.column() == 0:
            # in order to close the editor, timer is used.
            QTimer.singleShot(0, lambda: self.move_row(index, value))
            return True

        # for child.
        item = self.itemFromIndex(index.siblingAtColumn(0))
        if item.hasChildren():
            for row in range(item.rowCount()):  # children.
                citem = item.child(row, index.column())
                if citem:
                    citem.setData(value, role)
                cindex = self.indexFromItem(citem)
                self.updateData.emit(self.group_name, self.get_row_data(cindex), role, cindex)
            status = super().setData(index, value, role)  # parent.
        else:
            status = super().setData(index, value, role)  # parent or child.
            self.updateData.emit(self.group_name, self.get_row_data(index), role, index)
            if not self.is_parent(index) and index.row() == 0:
                pindex = index.parent().siblingAtColumn(index.column())
                status = super().setData(pindex, value, role)

        return status

    # ==================================================
    # for debug.
    # ==================================================
    def debug_data_changed(self, topLeft, bottomRight, roles=[]):
        """
        Debug for dataChanged signal.

        Args:
            topLeft (QModelIndex): top left index.
            bottomRight (QModelIndex): bottom right index.
            roles (list, optional): list of roles.
        """
        roles = [self.get_role_str.get(i) for i in roles]

        print("roles:", roles)
        data = self.tolist_index(topLeft, bottomRight)
        for i in data:
            print("data:", i)

    # ==================================================
    def debug_updata_data(self, name, row_data, role):
        """
        Debug for updateData signal.

        Args:
            name (str): group name.
            row_data (list): row data.
            role (int): role.
        """
        role = self.get_role_str(role)
        print(role, name, row_data)

    # ==================================================
    def debug_item_tree(self):
        """
        Debug for showing item tree.
        """
        root_item = self.invisibleRootItem()

        s = ""
        for row in range(root_item.rowCount()):
            row_data = self.get_row_data(root_item.child(row).index())
            s += str(row_data) + "\n"
            p_item = root_item.child(row)
            for c_row in range(p_item.rowCount()):
                row_data = self.get_row_data(p_item.child(c_row).index())
                s += " " * 4 + str(row_data) + "\n"
        s = s[:-1]

        print(s)

    # ==================================================
    def show_index(self, index):
        """
        Get raw index.

        Args:
            index (QModelIndex): index.

        Returns:
            - (str) -- raw index, P/C(row,column).
        """
        p = "P" if self.is_parent(index) else "C"
        return f"{p}({index.row()},{index.column()})"

    # ==================================================
    def get_role_str(self, role):
        """
        Get role string.

        Args:
            role (int): role.

        Returns:
            - (str) -- role string.
        """
        # role string.
        role_str = {
            Qt.EditRole: "EditRole",
            Qt.DisplayRole: "DisplayRole",
            Qt.UserRole: "UserRole",
            Qt.CheckStateRole: "CheckStateRole",
            Qt.ToolTipRole: "ToolTipRole",
            Qt.StatusTipRole: "StatusTipRole",
            Qt.FontRole: "FontRole",
            Qt.TextAlignmentRole: "TextAlignmentRole",
            Qt.BackgroundRole: "BackgroundRole",
            Qt.ForegroundRole: "ForegroundRole",
            Qt.DecorationRole: "DecorationRole",
            Qt.SizeHintRole: "SizeHintRole",
            Qt.ItemDataRole: "ItemDataRole",
            GroupModel.AppendRow: "AppendRow",
            GroupModel.RemoveRow: "RemoveRow",
            GroupModel.MoveRow: "MoveRow",
        }
        return role_str.get(role, f"UndefinedRole({role})")

    # ==================================================
    def tolist_index(self, topLeft, bottomRight):
        """
        Row data for given index.

        Args:
            topLeft (QModelIndex): index at top left.
            bottomRight (QModelIndex): index at buttom right.

        Returns:
            - (list) -- row data.
        """
        parent = self.itemFromIndex(topLeft.parent())
        if parent is None:
            parent = self.invisibleRootItem()

        data = [self.get_row(parent.child(row).index()) for row in range(topLeft.row(), bottomRight.row() + 1)]

        return data

    # ==================================================
    def clear_data(self):
        """
        Clear data with keeping header and column info.
        """
        self.block_update_widget(True)
        for row in reversed(range(self.rowCount())):
            index = self.index(row, 0)
            for row1 in reversed(range(self.rowCount(index))):
                cindex = self.index(row1, 0, index)
                self.remove_row(cindex)
            self.remove_row(index)
        self.block_update_widget(False)
