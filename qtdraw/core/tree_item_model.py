import pandas as pd
from qtpy.QtCore import QAbstractItemModel, QModelIndex, Qt, QVariant, Signal
from qtdraw.core.tree_item import TreeItem


# ==================================================
class TreeItemModel(QAbstractItemModel):
    """
    tree item model.

    References:
        - https://qiita.com/kenasman/items/794d2874d56d0dc37aea
        - https://ymt-lab.com/post/2020/pyqt5-qtreeview-sample/
        - https://doc.qt.io/qtforpython/overviews/qtwidgets-itemviews-editabletreemodel-example.html
        - https://github.com/baoboa/pyqt5/blob/master/examples/itemviews/editabletreemodel/editabletreemodel.py
    """

    rawDataChanged = Signal(str, int)  # (name, row)

    # ==================================================
    def __init__(self, ds, name, def_value=None, parent=None):
        """
        initialize the class.

        Args:
            ds (DataSet): data set.
            name (str): name of data.
            def_value (list, optional): default value.
            parent (QWidget, optional): parent QWidget.
        """
        super().__init__(parent)

        self.name = name  # name of data
        self.ds = ds  # reference of dataset
        self.header = ds[name].columns.values.tolist()  # header
        self.n_column = len(self.header)  # no of columns

        if def_value is None:
            def_value = ["" for _ in range(self.n_column)]
        self.def_value = def_value

        self.root, self.view, self.group = self.setViewData(ds[name])
        self.apply(self.setDisplayData)

        # self._debug_print()

    # ==================================================
    def setViewData(self, df):
        """
        set view data.

        Args:
            df (DataFrame): data frame.

        Returns:
            tuple: view data.
                - TreeItem: root of tree data.
                - DataFrame: data frame for view role.
                - list: data for group top.
        """
        view = df.copy()

        group = df.groupby(df.columns[0])
        child = [i.tolist() for i in group.groups.values()]
        root = TreeItem.create(child)
        gview = [[None for _ in range(len(df.columns))] for _ in range(len(group.groups))]

        return root, view, gview

    # ==================================================
    def apply(self, f, index=QModelIndex()):
        """
        apply function to all indices.

        Args:
            f (function): a function to apply, f(index).
            index (QModelIndex, optional): start index.
        """
        if index.isValid():
            for column in range(self.columnCount(index)):
                f(self.index(index.row(), column, index.parent()))

        if not self.hasChildren(index) or index.flags() & Qt.ItemNeverHasChildren:
            return

        rows = self.rowCount(index)
        for i in range(rows):
            self.apply(f, self.index(i, 0, index))

    # ==================================================
    def rowCount(self, parent=QModelIndex()):
        """
        number of rows for given parent index.

        Args:
            parent (QModelIndex, optional): parent index.

        Returns:
            int: number of rows.
        """
        if not parent.isValid():
            pitem = self.root
        else:
            pitem = parent.internalPointer()
        return pitem.n_child()

    # ==================================================
    def columnCount(self, parent=QModelIndex()):
        """
        number of columns for given parent index.

        Args:
            parent (QModelIndex, optional): parent index.

        Returns:
            int: number of columns.
        """
        return self.n_column

    # ==================================================
    def flags(self, index):
        """
        flag setting.

        Args:
            index (QModelIndex): index

        Returns:
            Qt.Flags: add Editable.
        """
        if not index.isValid():
            return 0

        return Qt.ItemIsEditable | super().flags(index)

    # ==================================================
    def parent(self, index):
        """
        parent index for given index.

        Args:
            index (QModelIndex): index.

        Returns:
            QModelIndex: parent index. For invalid index, return QModelIndex().
        """
        if not index.isValid():
            return QModelIndex()
        citem = index.internalPointer()
        pitem = citem.parent()
        if pitem == self.root:
            return QModelIndex()
        return self.createIndex(pitem.row(), 0, pitem)

    # ==================================================
    def index(self, row, column, parent=QModelIndex()):
        """
        index obtained from row, column, and parent.

        Args:
            row (int): row in parent.
            column (int): column in parent.
            parent (QModelIndex, optional): parent index.

        Returns:
            QModelIndex: index. For invalid index, return QModelIndex().
        """
        if not parent.isValid():
            pitem = self.root
        else:
            pitem = parent.internalPointer()
        citem = pitem.child(row)
        if citem:
            return self.createIndex(row, column, citem)
        else:
            return QModelIndex()

    # ==================================================
    def absIndex(self, index):
        """
        absolute index of data frame from index.

        Args:
            index (QModelIndex): index.

        Returns:
            tuple: absolute index (table-row, table-column, level). For invalid index, return None.
        """
        if not index.isValid():
            return None, None, None

        item = index.internalPointer()
        if item.n_child() == 0:
            row = item.data()
        else:
            row = item.child(0).data()
        column = index.column()
        level = item.level()

        return row, column, level

    # ==================================================
    def childIndex(self, index):
        """
        child and parent indices.

        Args:
            index (QModelIndex): index.

        Returns:
            list: (child and) parent indices.
        """
        indices = [self.index(i, index.column(), index) for i in range(self.rowCount(index))]
        indices += [index]

        return indices

    # ==================================================
    def data(self, index, role):
        """
        data for given index and role.

        Args:
            index (QModelIndex): index.
            role (Qt.Role): role, Qt.DisplayRole, Qt.EditRole, Qt.UserRole.

        Returns:
            Any: data for given index and role. For invalid role/index, return QVariant().

        Notes:
            - return display data for DisplayRole and EditRole, otherwise return raw data.
        """
        if role != Qt.DisplayRole and role != Qt.EditRole and role != Qt.UserRole:
            return QVariant()

        row, column, level = self.absIndex(index)
        if row is None or level == 0 or level > 2:
            return QVariant()

        if role == Qt.UserRole:
            return self.ds[self.name].iat[row, column]

        if level == 1:
            return self.group[index.row()][column]

        return self.view.iat[row, column]

    # ==================================================
    def headerData(self, section, orientation=Qt.Horizontal, role=Qt.DisplayRole):
        """
        header data.

        Args:
            section (int): column.
            orientation (Qt.Orientation, optional): only for Horizontal.
            role (Qt.Role, optional): only for DisplayRole.

        Returns:
            Any: header column of data frame. For invalid section, return None.
        """
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[section]

        return None

    # ==================================================
    def setData(self, index, value, role=Qt.EditRole, emit=True):
        """
        set data.

        Args:
            index (QModelIndex): index.
            value (Any): value to set.
            role (Qt.Role, optional): only for Edit.

        Returns:
            bool: return True if sucess, otherwise False.
        """
        if role != Qt.EditRole:
            return False

        row, column, level = self.absIndex(index)
        if row is None or level == 0 or level > 2:
            return False

        index = self.childIndex(index)

        single = len(index) == 1
        for index1 in index:
            row, column, level = self.absIndex(index1)
            if row is not None and (level == 2 or single):
                self.ds[self.name].iat[row, column] = value
                if emit:
                    self.rawDataChanged.emit(self.name, row)
            self.setDisplayData(index1)
            if level == 2:
                self.setDisplayData(index1.parent().siblingAtColumn(index1.column()))

        return True

    # ==================================================
    def setDisplayData(self, index):
        """
        set data for display.

        Args:
            index (QModelIndex): index.

        Notes:
            - self.view and self.group for corresponding index are modified for display.
        """
        row, column, level = self.absIndex(index)
        if row is None:
            return

        item = self.setDisplayDataRaw(index)
        if level == 1:
            self.group[index.row()][column] = item
        else:
            self.view.iat[row, column] = item

    # ==================================================
    def setDisplayDataRaw(self, index):
        """
        function to obtain data for display from raw data.

        Args:
            index (QIndexModel): index.

        Returns:
            Any: data for display.
        """
        # return str((index.row(), index.column())) + " => " + str(self.absIndex(index))
        data = index.data(role=Qt.UserRole)
        return str(data)

    # ==================================================
    def _debug_print(self):
        """
        print tree structure for deubug.
        """

        def debug(index):
            row, column, level = self.absIndex(index)
            if row is not None:
                if level == 1:
                    g = "group"
                else:
                    g = "orig"
                print(g, ": (", index.row(), index.column(), ") => (", row, column, ")", index.data())

        self.apply(debug)
        print("=====")

    # ==================================================
    def appendRow(self, index=QModelIndex(), name=None):
        """
        append row.

        Args:
            index (QModelIndex, optional): index.
            key (str, optional): name.

        Returns:
            bool: True if insert is success.

        Notes:
            - inserted row is simply appended at the last raw of data frame.
        """
        index = index.siblingAtColumn(0)

        # add row data.
        add = self.def_value.copy()
        null = [None for _ in range(self.columnCount())]
        if not index.isValid():  # add
            names = [self.index(row, 0).data(Qt.UserRole) for row in range(self.root.n_child())]
            add[0] = name
            if name not in names:
                self.group.append(null)
            else:
                grow = names.index(name)
                index = self.index(grow, 0)
        else:  # insert
            add[0] = self.data(index, Qt.UserRole)
        last_row = len(self.ds[self.name])
        self.ds.append(self.name, add)
        self.view = pd.concat([self.view, pd.DataFrame([null], columns=self.header)], ignore_index=True)

        # set index.
        if not index.isValid():  # root
            pitem = self.root
            row = pitem.n_child()
            self.beginInsertRows(index, row, row)
            item = TreeItem(last_row, pitem)
            pitem.append(item)
            self.endInsertRows()
            index = self.index(row, 0)
        else:
            _, _, level = self.absIndex(index)
            if level == 1:  # for group
                pitem = index.internalPointer()
                row = pitem.n_child()
                if row == 0:  # no child
                    self.beginInsertRows(index, 0, 1)
                    item = TreeItem(pitem.data(), pitem)
                    pitem.append(item)
                    item = TreeItem(last_row, pitem)
                    pitem.append(item)
                    pitem.setData(None)
                    self.endInsertRows()
                    index1 = self.index(0, 0, index)
                    for column in range(self.columnCount()):
                        index1 = index1.siblingAtColumn(column)
                        self.setDisplayData(index1)
                    index = self.index(1, 0, index)
                else:  # with child
                    self.beginInsertRows(index, row, row)
                    item = TreeItem(last_row, pitem)
                    pitem.append(item)
                    self.endInsertRows()
                    index = self.index(row, 0, index)
            else:  # for child
                pitem = index.parent().internalPointer()
                row = pitem.n_child()
                self.beginInsertRows(index.parent(), row, row)
                item = TreeItem(last_row, pitem)
                pitem.append(item)
                self.endInsertRows()
                index = self.index(row, 0, index.parent())

        # set data.
        for column, value in enumerate(add):
            index = index.siblingAtColumn(column)
            self.setData(index, value, emit=False)

        self.rawDataChanged.emit(self.name, self.absIndex(index)[0])

        return True

    # ==================================================
    def removeRow(self, index=QModelIndex()):
        """
        remove row.

        Args:
            parent (QModelIndex), optional): parent index.

        Returns:
            bool: True if remove is success.

        Notes:
            - removed row is set simply as (first column)="" instead of removing row itself in raw data frame.
        """
        index = index.siblingAtColumn(0)
        row, _, level = self.absIndex(index)

        parent = index.parent()
        if not parent.isValid():
            pitem = self.root
        else:
            pitem = parent.internalPointer()

        if level == 1:  # for group
            self.beginRemoveRows(parent, index.row(), index.row())
            del self.group[index.row()]
            item = index.internalPointer()
            if item.n_child() == 0:
                self.ds[self.name].iloc[row, 0] = ""
                self.view.iloc[row, 0] = ""
                self.rawDataChanged.emit(self.name, self.absIndex(index)[0])
            else:
                for row in range(item.n_child()):
                    arow = item.child(row).data()
                    self.ds[self.name].iloc[arow, 0] = ""
                    self.view.iloc[arow, 0] = ""
                    self.rawDataChanged.emit(self.name, self.absIndex(index.child(row, 0))[0])
            pitem.remove(index.row())
            self.endRemoveRows()
        else:  # for child
            self.ds[self.name].iloc[row, 0] = ""
            self.view.iloc[row, 0] = ""
            self.rawDataChanged.emit(self.name, self.absIndex(index)[0])
            if pitem.n_child() == 2:
                self.beginRemoveRows(parent, 0, 1)
                if index.row() == 0:
                    pitem.setData(pitem.child(1).data())
                else:
                    pitem.setData(pitem.child(0).data())
                pitem.remove(0)
                pitem.remove(0)
                self.endRemoveRows()
            else:
                self.beginRemoveRows(parent, index.row(), index.row())
                pitem.remove(index.row())
                self.endRemoveRows()
            for column in range(self.columnCount()):
                parent1 = parent.siblingAtColumn(column)
                self.setDisplayData(parent1)

        self.apply(self.setDisplayData)  # update all display data.

        return True
