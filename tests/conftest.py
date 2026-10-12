"""
Common fixtures for automated tests.
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
import shiboken6

from qtdraw.widget.qt_event_util import get_qt_application
from gui_helpers import close_open_widgets, process_deleted


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
def no_open_widgets(process_deleted_widgets):
    """
    Fail a test that leaves a drawing open, after closing it: on Linux with Mesa and the off-screen Qt platform,
    a window left open crashes later tests that use off-screen widgets (#197).

    The closed windows are deleted afterwards by process_deleted_widgets.
    """
    yield
    left = close_open_widgets()
    if left:
        pytest.fail("left open by the test (closed now, without saving): " + ", ".join(left))


# ==================================================
@pytest.fixture(autouse=True)
def isolated_settings(tmp_path_factory):
    """
    Keep settings such as recent files in a temporary directory, not in the user's settings.
    """
    from PySide6.QtCore import QSettings

    directory = str(tmp_path_factory.mktemp("settings"))
    for scope in (QSettings.UserScope, QSettings.SystemScope):  # also no fallback to installed system settings.
        QSettings.setPath(QSettings.IniFormat, scope, directory)
    yield


# ==================================================
@pytest.fixture(autouse=True)
def isolated_svg_cache(tmp_path_factory, monkeypatch):
    """
    Keep the MathJax SVG cache of widgets created by a test in a temporary directory, not in the user's.
    """
    from qtdraw.widget import mathjax

    directory = tmp_path_factory.mktemp("svg_cache")
    init = mathjax.MathJaxSVG.__init__

    def isolated(self, cache_dir=None, **kwargs):
        init(self, cache_dir=cache_dir or directory, **kwargs)

    monkeypatch.setattr(mathjax.MathJaxSVG, "__init__", isolated)


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
