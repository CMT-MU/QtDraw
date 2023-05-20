from PyQt5.QtWidgets import QDialog, QTableWidget, QGridLayout
from qtdraw.core.editable_widget import QtText, QtMath
from qtdraw.core.setting import rcParams


# ==================================================
class TableWidget(QTableWidget):
    # ==================================================
    def __init__(self, data, header, vheader, role, align, parent=None):
        row = len(data)
        if row == 0:
            col = 0
        else:
            col = len(data[0])
        super().__init__(row, col, parent)

        for i, row in enumerate(data):
            for j, item in enumerate(row):
                w = self.get_widget(str(item), role[j], align[j], parent)
                self.setCellWidget(i, j, w)

        if header is not None:
            self.setHorizontalHeaderLabels(header)
        else:
            self.horizontalHeader().hide()
        if vheader is not None:
            self.setVerticalHeaderLabels(vheader)
        else:
            self.verticalHeader().hide()

        self.resizeColumnsToContents()
        self.resizeRowsToContents()

    # ==================================================
    def get_widget(self, item, role, align, parent):
        if role == "math":
            color = rcParams["detail.latex.color"]
            style = rcParams["detail.latex.format"]
            dpi = rcParams["detail.latex.dpi"]
            w = QtMath(
                item,
                style=style,
                color=color,
                dpi=dpi,
                read_only=True,
                align=align,
                parent=parent,
            )
        else:  # text.
            item = str(item).replace("j", "i").strip(" ()")
            w = QtText(item, read_only=True, align=align, parent=parent)
        return w


# ==================================================
class TableDialog(QDialog):
    # ==================================================
    def __init__(
        self, data, title="TableDialog", header=None, vheader=None, role=None, align=None, width=512, height=600, parent=None
    ):
        super().__init__(parent)

        self.setWindowTitle(title)
        self.resize(width, height)

        if role is None:
            role = [""] * len(data)
        if align is None:
            align = ["left"] * len(data)

        table = TableWidget(data, header, vheader, role, align, parent)

        bg = rcParams["detail.table.bg_color"]
        table.setStyleSheet(f"selection-background-color: {bg}")

        layout = QGridLayout(self)
        layout.addWidget(table, 0, 0, 1, 1)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.setLayout(layout)
