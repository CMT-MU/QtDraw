"""
TableView widget.

This module provides table view widget.
"""

from PySide6.QtWidgets import QTableWidget, QWidget, QSizePolicy, QHeaderView
from PySide6.QtCore import Qt, QTimer

from qtdraw.widget.custom_widget import MathWidget, Layout
from qtdraw.widget.mathjax import MathJaxSVG


# ==================================================
class TableView(QTableWidget):
    # ==================================================
    def __init__(self, parent=None, data=None, header=None, vertical=False, color="black", size=12, mathjax=None):
        """
        Table view (math).

        Args:
            parent (QWidget, optional): parent.
            data (list, optional): table data in LaTeX code without "$".
            header (list, optional): header string.
            vertical (bool, optional): show vertical number header ?
            color (str, optional): color name.
            size (int, optional): font size.
        """
        super().__init__(parent)
        if mathjax is None:
            self._mathjax = MathJaxSVG()
        else:
            self._mathjax = mathjax

        if data is None:
            data = [[""]]

        if not data or not data[0]:
            self.setRowCount(0)
            self.setColumnCount(0)
            return

        row = len(data)
        column = len(data[0])

        if header is not None and len(header) != column:
            raise ValueError("Header length must match number of columns.")

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
                if item:
                    math = MathWidget(self.viewport(), text=item, color=color, size=size, mathjax=self._mathjax)

                    wrapper = QWidget(self)
                    layout = Layout(wrapper)
                    layout.setContentsMargins(10, 10, 10, 10)
                    layout.addWidget(math)
                    layout.setAlignment(math, Qt.AlignCenter)

                    math.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
                    wrapper.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
                    self.setCellWidget(i, j, wrapper)

        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        QTimer.singleShot(0, self.resizeColumnsToContents)
        QTimer.singleShot(0, self.resizeRowsToContents)

        self.horizontalHeader().setMinimumSectionSize(30)

        self.setStyleSheet(
            """
            QTableWidget::item:selected {
                background-color: LemonChiffon;
            }
        """
        )
