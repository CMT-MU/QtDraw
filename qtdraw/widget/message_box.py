"""
MessageBox dialog.

This module provides message box dialog.
"""

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QGridLayout, QMessageBox, QPlainTextEdit, QSizePolicy, QTextEdit
from PySide6.QtGui import QFontDatabase, QGuiApplication
import shiboken6
from PySide6.QtCore import QEvent, Qt, QTimer


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
class ResizableMessageBox(QMessageBox):
    """
    Message box whose size can be changed, e.g. to read long details.
    """

    MAX_SIZE = 16777215  # QWIDGETSIZE_MAX.

    # ==================================================
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowFlag(Qt.MSWindowsFixedSizeDialogHint, False)  # a resizable frame on Windows.

    # ==================================================
    def event(self, e):
        """
        Lift the fixed size that QMessageBox sets again whenever it is laid out.

        :meta private:
        """
        if not shiboken6.isValid(self):  # called while the box is being deleted.
            return False
        if e.type() == QEvent.LayoutRequest and self.isVisible():
            result = QDialog.event(self, e)  # QMessageBox would fix the size again, e.g. with wrapped text.
        else:
            result = super().event(e)
        if e.type() in (QEvent.LayoutRequest, QEvent.Resize, QEvent.Show):
            self._lift_fixed_size()
        return result

    # ==================================================
    def _unfill_screen(self, size):
        """
        Give the box its size again if it fills the screen, but keep any other size, e.g. set by the user.

        :meta private:
        """
        if not shiboken6.isValid(self) or self.screen() is None:
            return
        screen = self.screen().availableGeometry().size()
        if self.width() >= screen.width() and self.height() >= screen.height() - 40:  # the title bar is not counted.
            self.resize(size)

    # ==================================================
    def _lift_fixed_size(self):
        """
        Allow any size, and let the details grow with the box.

        :meta private:
        """
        fixed, size = self.maximumSize() == self.minimumSize(), self.size()
        self.setSizeGripEnabled(True)
        self.setMinimumSize(self.layout().totalMinimumSize())  # the buttons and the message stay visible.
        self.setMaximumSize(self.MAX_SIZE, self.MAX_SIZE)
        if fixed and self.isVisible() and QGuiApplication.platformName() == "cocoa":  # macOS then fills the screen (later).
            QTimer.singleShot(0, lambda: self._unfill_screen(size))
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        details = self.findChild(QTextEdit)
        if details is not None:
            details.setMaximumSize(self.MAX_SIZE, self.MAX_SIZE)
            details.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            layout = self.layout()
            container = details.parentWidget() if layout.indexOf(details) < 0 else details
            index = layout.indexOf(container)
            if index >= 0 and hasattr(layout, "setRowStretch"):
                container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                row = layout.getItemPosition(index)[0]
                stretch = [1 if r == row else 0 for r in range(layout.rowCount())]
                if [layout.rowStretch(r) for r in range(layout.rowCount())] != stretch:  # set once: it lays out again.
                    for r, value in enumerate(stretch):
                        layout.setRowStretch(r, value)  # only the details get the extra space.


# ==================================================
def show_error(summary, details, title="Error"):
    """
    Show an error with a short message, and the full details behind "Show Details...".

    Args:
        summary (str): short message, e.g. "ValueError: invalid value".
        details (str): details, e.g. traceback.
        title (str, optional): window title.
    """
    box = ResizableMessageBox(QMessageBox.Critical, title, summary)
    box.setInformativeText("See the details for the traceback. The error is also written to the log.")
    box.setDetailedText(details)
    box.exec()
