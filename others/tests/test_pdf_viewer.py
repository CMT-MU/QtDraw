# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2021- The QtDraw developers
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""
Test for PDFViewer.

This module provides a test for PDF viewer.
"""

from PySide6.QtWidgets import QApplication

from qtdraw.widget.pdf_viewer import PDFViewer


# ==================================================
def test_pdf_viewer():
    app = QApplication([])
    pdf = PDFViewer()
    pdf.show()
    app.exec()


# ================================================== main
test_pdf_viewer()
