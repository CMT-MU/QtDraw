"""
MessageBox dialog.

This module provides message box dialog.
"""

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QGridLayout, QPlainTextEdit
from PySide6.QtGui import QFont


# ==================================================
class MessageBox(QDialog):
    # ==================================================
    def __init__(self, msg, title="Message Box"):
        """
        Message box.

        Args:
            msg (str): message.
            title (str): window title.
        """
        super().__init__()
        self.setWindowTitle(title)
        self.resize(800, 400)

        font = QFont("Monaco", 11)
        font.setStyleHint(QFont.TypeWriter)

        text = QPlainTextEdit(msg, self)
        text.setFont(font)
        text.setReadOnly(True)

        button = QDialogButtonBox(QDialogButtonBox.Ok)
        button.accepted.connect(self.accept)

        layout = QGridLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        self.setLayout(layout)
        layout.addWidget(text, 0, 0, 1, 1)
        layout.addWidget(button, 1, 0, 1, 1)

        self.exec()
