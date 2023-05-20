from qtpy.QtCore import Qt, QSize, QModelIndex
from qtpy.QtWidgets import QItemDelegate, QStyle
from qtpy.QtGui import QColor
from qtdraw.core.tree_item_model import TreeItemModel
from qtdraw.core.editable_widget import (
    EditableWidget,
    QtText,
    QtImage,
    QtMath,
    QtCheckBox,
    QtRadioGroup,
    QtComboBox,
    QtColorSelector,
)
from qtdraw.core.setting import rcParams
from qtdraw.core.color_palette import all_colors


# ==================================================
class GroupModel(TreeItemModel):
    # ==================================================
    def __init__(self, ds, name, read_only=False, align=None, parent=None):
        roles = ds.role[name]
        if roles is None:
            roles = [""] * ds[name].shape[1]
        if align is None:
            align = ["left"] * ds[name].shape[1]

        self.parent_widget = parent
        self.read_only = read_only
        self.roles = []
        self.roles_opt = []
        self.init = []
        self.hide = []
        for i, role in enumerate(roles):
            self.roles.append(role[0])
            self.roles_opt.append(role[1:-1])
            self.init.append(role[-1])
            if role[0] == "hide":
                self.hide.append(i)
        self.align = align

        super().__init__(ds, name, self.init, parent)

    # ==================================================
    def _associated_index(self, index, key):
        if key not in self.header:
            return QModelIndex()
        else:
            return index.siblingAtColumn(self.header.index(key))

    # ==================================================
    def setDisplayDataRaw(self, index):
        # return QtText(str((index.row(), index.column())) + " => " + str(self.absIndex(index)), parent=self.parent_widget)
        # return QtText(str(index.data(Qt.UserRole)), parent=self.parent_widget)

        def _check(index_s, flag, index, data):
            self.setData(index_s, flag, emit=False)
            self.setData(index, data)

        parent = self.parent_widget
        data = index.data(Qt.UserRole)
        role = self.roles[index.column()]
        opt = self.roles_opt[index.column()]
        align = self.align[index.column()]

        if role == "check":
            if len(opt) == 0:
                item = QtText(
                    data, callback=lambda txt: self.setData(index, txt), read_only=self.read_only, align=align, parent=parent
                )
            else:
                index_s = self._associated_index(index, opt[0])  # check status.
                if index_s.column() == index.column():  # check only.
                    item = QtCheckBox(
                        current=data,
                        callback_check=lambda flag: self.setData(index_s, flag),
                        read_only=self.read_only,
                        parent=parent,
                    )
                else:  # check with text.
                    status = index_s.data(Qt.UserRole)
                    item = QtCheckBox(
                        label=data,
                        current=status,
                        callback_check=lambda flag: _check(index_s, flag, index, data),
                        read_only=self.read_only,
                        parent=parent,
                    )
        elif role == "check_edit":
            index_s = self._associated_index(index, opt[0])  # check status.
            status = index_s.data(Qt.UserRole)
            item = QtCheckBox(
                label=data,
                current=status,
                callback_check=lambda flag: _check(index_s, flag, index, data),
                callback_label=lambda text: self.setData(index, text, emit=True),
                read_only=self.read_only,
                parent=parent,
            )
        elif role == "text":
            if len(opt) == 0:  # no validator.
                data = str(data).replace("j", "i").strip(" ()")
                item = QtText(
                    data, callback=lambda txt: self.setData(index, txt), read_only=self.read_only, align=align, parent=parent
                )
            elif len(opt) == 1:  # validator only.
                item = QtText(
                    data,
                    callback=lambda txt: self.setData(index, txt),
                    validator=opt[0],
                    read_only=self.read_only,
                    align=align,
                    parent=parent,
                )
            else:  # validator + decimal
                item = QtText(
                    data,
                    callback=lambda txt: self.setData(index, txt),
                    validator=opt[0],
                    decimal=opt[1],
                    read_only=self.read_only,
                    align=align,
                    parent=parent,
                )
        elif role == "image":
            w = rcParams["detail.image.width"]
            item = QtImage(data, width=w, read_only=self.read_only, parent=parent)
        elif role == "math":
            color = rcParams["detail.latex.color"]
            style = rcParams["detail.latex.format"]
            dpi = rcParams["detail.latex.dpi"]
            if len(opt) == 0:  # no validator.
                item = QtMath(
                    data,
                    callback=lambda txt: self.setData(index, txt),
                    color=color,
                    style=style,
                    dpi=dpi,
                    read_only=self.read_only,
                    align=align,
                    parent=parent,
                )
            elif len(opt) == 1:  # validator only.
                item = QtMath(
                    data,
                    callback=lambda txt: self.setData(index, txt),
                    validator=opt[0],
                    color=color,
                    style=style,
                    dpi=dpi,
                    read_only=self.read_only,
                    align=align,
                    parent=parent,
                )
            else:  # validator + acceptable variables.
                item = QtMath(
                    data,
                    callback=lambda txt: self.setData(index, txt),
                    validator=opt[0],
                    check_var=opt[1],
                    color=color,
                    style=style,
                    dpi=dpi,
                    read_only=self.read_only,
                    align=align,
                    parent=parent,
                )
        elif role in ["color", "colormap", "color_both"]:
            item = QtColorSelector(
                current=data,
                color_type=role,
                callback=lambda color: self.setData(index, color),
                parent=parent,
            )
        elif role == "radio":
            lst = opt[0]
            vertical = opt[1] == "V"
            item = QtRadioGroup(
                lst=lst,
                current=data,
                vertical=vertical,
                callback=lambda idx: self.setData(index, idx),
                parent=parent,
            )
        elif role == "combo":
            lst = opt[0]
            item = QtComboBox(lst=lst, current=data, callback=lambda idx: self.setData(index, idx), parent=parent)
        elif role == "hide":
            return QtText("", read_only=True, parent=parent)
        else:
            item = QtText(
                str(data), callback=lambda txt: self.setData(index, txt), read_only=self.read_only, align=align, parent=parent
            )

        if not isinstance(item, EditableWidget):
            item = QtText("unknown widget", read_only=True, align=align, parent=parent)

        return item


# ==================================================
class Delegate(QItemDelegate):
    def __init__(self, bgcolor, parent=None):
        super().__init__(parent)
        self.bgcolor = QColor(all_colors[bgcolor][0])

    # ==================================================
    def paint(self, painter, option, index):

        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, self.bgcolor)

        self.parent().setIndexWidget(index, index.data(Qt.DisplayRole))

    # ==================================================
    def sizeHint(self, option, index):
        item = index.data(Qt.DisplayRole)

        if item:
            return QSize(item.width(), item.height())
        else:
            return super().sizeHint(option, index)
