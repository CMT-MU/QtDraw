"""
Simple PDF viewer.

This module contains a class for simple PDF viewer.
It can load PDF file, and save the same file to
different directory (just by copying it).
"""

from PySide6.QtWidgets import QFileDialog, QGridLayout, QWidget, QPushButton
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from shutil import copy
import os


# ==================================================
class PDFViewer(QWidget):

    # ==================================================
    def __init__(self, filename=None):
        """
        Simple PDF viewer.

        Args:
            filename (str, optional): file name to load.
        """
        super().__init__()

        self.document = QPdfDocument(self)
        if filename is not None:
            self.document.load(filename)
            self.filename = filename

        view = QPdfView(self)
        view.setDocument(self.document)
        view.setPageMode(QPdfView.PageMode.MultiPage)
        view.setZoomMode(QPdfView.ZoomMode.FitToWidth)

        open_btn = QPushButton("Open")
        open_btn.clicked.connect(self.load)
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save)

        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(7)
        layout.addWidget(open_btn, 0, 0, 1, 1)
        layout.addWidget(save_btn, 0, 1, 1, 1)
        layout.addWidget(view, 1, 0, 1, 12)

        self.setLayout(layout)
        self.resize(800, 1000)
        self.set_title()

    # ==================================================
    def load(self):
        """
        Load PDF file.
        """
        self.filename, _ = QFileDialog.getOpenFileName(self, filter="PDF (*.pdf)")
        if self.filename != "":
            self.document.load(self.filename)
            self.set_title(self.filename)

    # ==================================================
    def save(self):
        """
        Save PDF file (default = current directory).
        """
        full = os.path.join(os.getcwd(), os.path.split(self.filename)[1])
        filename, _ = QFileDialog.getSaveFileName(self, dir=full, filter="PDF (*.pdf)")
        if filename != "":
            copy(self.filename, filename)

    # ==================================================
    def set_title(self, filename=None):
        """
        Set window title.

        Args:
            filename (str, optional): file name.
        """
        if filename is None:
            filename = "None"

        self.setWindowTitle(f"PDF Viewer - {filename}")
