"""
MessageBox dialog.

This module provides message box dialog.
"""

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QGridLayout, QMessageBox, QPlainTextEdit
from PySide6.QtGui import QFontDatabase


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

        font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        font.setPointSize(11)

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


# ==================================================
def show_error(summary, details, title="Error"):
    """
    Show an error with a short message, and the full details behind "Show Details...".

    Args:
        summary (str): short message, e.g. "ValueError: invalid value".
        details (str): details, e.g. traceback.
        title (str, optional): window title.
    """
    box = QMessageBox(QMessageBox.Critical, title, summary)
    box.setInformativeText("See the details for the traceback. The error is also written to the log.")
    box.setDetailedText(details)
    box.exec()
