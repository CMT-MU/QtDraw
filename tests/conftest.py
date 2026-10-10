"""
Common fixtures for automated tests.
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
import shiboken6

from qtdraw.widget.qt_event_util import get_qt_application
from gui_helpers import process_deleted


# ==================================================
@pytest.fixture(autouse=True)
def process_deleted_widgets():
    """
    Delete widgets scheduled for deletion by a test (tests run without an event loop).
    """
    yield
    process_deleted()


# ==================================================
@pytest.fixture(autouse=True)
def isolated_settings(tmp_path_factory):
    """
    Keep settings such as recent files in a temporary directory, not in the user's settings.
    """
    from PySide6.QtCore import QSettings

    QSettings.setPath(QSettings.IniFormat, QSettings.UserScope, str(tmp_path_factory.mktemp("settings")))
    yield


# ==================================================
@pytest.fixture(scope="session")
def qapp():
    return get_qt_application()


# ==================================================
@pytest.fixture
def widget(qapp, tmp_path, monkeypatch):
    from qtdraw.core.pyvista_widget import PyVistaWidget

    monkeypatch.chdir(tmp_path)
    w = PyVistaWidget(off_screen=True)
    yield w
    if shiboken6.isValid(w):  # not yet closed (and deleted) by the test.
        w.close()
