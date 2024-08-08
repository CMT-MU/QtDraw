"""
Test for PDFViewer.

This module provides a test for PDF viewer.
"""

from PySide6.QtWidgets import QApplication
from qtdraw.util.pdf_viewer import PDFViewer


# ==================================================
def test_pdf_viewer():
    app = QApplication([])
    pdf = PDFViewer()
    pdf.show()
    app.exec()


# ================================================== main
test_pdf_viewer()
