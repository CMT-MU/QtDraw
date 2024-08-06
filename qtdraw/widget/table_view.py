"""
TableView widget.

This module provides table view widget.
"""

from PySide6.QtWidgets import QTableWidget
from qtdraw.widget.custom_widget import Label


# ==================================================
class TableView(QTableWidget):
    # ==================================================
    def __init__(self, parent=None, data=[[""]], header=None, vertical=False, color="black", size=12, dpi=120):
        """
        Table view (math).

        Args:
            parent (QWidget, optional): parent.
            data (list, optional): table data in LaTeX code without "$".
            header (list, optional): header string.
            vertical (bool, optional): show vertical number header ?
            color (str, optional): color name.
            size (int, optional): font size.
            dpi (int, optional): DPI.
        """
        super().__init__(parent)

        row = len(data)
        column = len(data[0])

        self.setRowCount(row)
        self.setColumnCount(column)
        if header is not None:
            self.setHorizontalHeaderLabels(header)
            self.horizontalHeader().setStyleSheet("font-weight: bold;")
        else:
            self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(vertical)

        for i, r in enumerate(data):
            for j, item in enumerate(r):
                item = str(item)
                if item != "":
                    label = Label(self, item, color=color, size=size, math=True, dpi=dpi)
                    label.setContentsMargins(5, 5, 5, 5)
                    self.setCellWidget(i, j, label)

        self.resizeColumnsToContents()
        self.resizeRowsToContents()
