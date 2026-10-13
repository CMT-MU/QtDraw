"""
QtDraw runs with the functions of MultiPie turned off when MultiPie is not installed, or is installed but cannot
be loaded (e.g. a broken or incompatible installation).
"""

import os
import subprocess
import sys
import textwrap
from pathlib import Path


from qtdraw.util.util import MULTIPIE_INSTALL, check_multipie, multipie_message

SI_CIF = Path(__file__).resolve().parents[1] / "docs" / "src" / "examples" / "Si.cif"


# ==================================================
def broken_multipie(path):
    """
    A MultiPie that is found and imported, but whose parts used by QtDraw fail to load.
    """
    package = path / "multipie"
    package.mkdir()
    (package / "__init__.py").write_text(
        'import importlib\n__version__ = "2.3.4"\n\n\ndef __getattr__(name):\n    importlib.import_module("multipie.group")\n'
    )
    (package / "group.py").write_text("s = (\n")  # a syntax error.
    return path


ISOLATED = """
import os
from pathlib import Path
from PySide6.QtCore import QSettings
for scope in (QSettings.UserScope, QSettings.SystemScope):  # not the user's settings.
    QSettings.setPath(QSettings.IniFormat, scope, os.environ["QTDRAW_TEST_HOME"])
import qtdraw.widget.mathjax as mathjax
init = mathjax.MathJaxSVG.__init__
mathjax.MathJaxSVG.__init__ = lambda self, cache_dir=None, **kw: init(
    self, cache_dir=cache_dir or Path(os.environ["QTDRAW_TEST_HOME"]) / "svg_cache", **kw
)  # not the user's cache.
"""


def run(code, path):
    """
    Run code in a process that finds the MultiPie in path, with its settings and cache in path.
    """
    env = {**os.environ, "QT_QPA_PLATFORM": "offscreen", "PYTHONPATH": os.pathsep.join([str(path), *sys.path])}
    env["QTDRAW_TEST_HOME"] = str(path)
    code = ISOLATED + textwrap.dedent(code)
    ret = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=120, env=env)
    assert ret.returncode == 0 and "OK" in ret.stdout, ret.stdout + ret.stderr[-3000:]
    return ret.stdout


# ==================================================
def test_multipie_that_fails_to_load_is_not_available(tmp_path):
    out = run(
        """
        import multipie  # found, and its package imports.
        from qtdraw.util.util import check_multipie, multipie_message
        assert not check_multipie()
        print("MESSAGE", multipie_message())
        print("OK")
        """,
        broken_multipie(tmp_path),
    )
    message = out.split("MESSAGE ")[1].split("\nOK")[0]
    assert "cannot be loaded" in message and "SyntaxError" in message, message
    assert "pip install multipie" not in message, message  # it is installed.


def test_qtdraw_runs_with_multipie_turned_off(tmp_path):
    run(
        f"""
        from PySide6.QtWidgets import QMessageBox
        from qtdraw.core.qtdraw_app import QtDraw
        from qtdraw.core.dialog_about import get_version_info  # without the version of MultiPie.
        shown = []
        QMessageBox.information = lambda *a, **k: shown.append(a[2]) or QMessageBox.Ok
        QMessageBox.question = lambda *a, **k: QMessageBox.Discard
        window = QtDraw()
        window.pyvista_widget.add_site()
        window.misc_button_multipie.click()  # tells why, without opening the dialog.
        assert len(shown) == 1 and "cannot be loaded" in shown[0], shown
        assert window.multipie_dialog is None
        pvw = window.pyvista_widget
        pvw.load({str(SI_CIF)!r})  # a material file opens.
        sites = pvw._data["site"].rowCount()
        assert sites > 0
        from qtdraw.util.util import read_dict
        file = Path(os.environ["QTDRAW_TEST_HOME"]) / "mp.qtdw"
        pvw.save(str(file))
        drawing = read_dict(str(file))
        drawing["status"]["multipie"] = {{"version": "2.3.4", "group": {{"group": "D6h"}}}}
        file.write_text(str(drawing))
        pvw.add_site(position="[0.1,0.2,0.3]", name="current")  # only in the current drawing.
        current = pvw.get_data_dict()
        try:  # a drawing with a MultiPie group is not opened, the current one is kept.
            pvw.load(str(file))
        except Exception as e:
            assert "mp.qtdw uses MultiPie" in str(e) and "cannot be loaded" in str(e), e
        else:
            raise AssertionError("a MultiPie drawing opened without MultiPie")
        assert pvw.get_data_dict() == current
        try:
            pvw.mp_set_group("D6h")
        except Exception as e:
            assert "cannot be loaded" in str(e), e
        else:
            raise AssertionError("mp_set_group without MultiPie")
        assert "MultiPie" not in get_version_info()
        window.close()
        print("OK")
        """,
        broken_multipie(tmp_path),
    )


def test_message_without_multipie_tells_how_to_install(monkeypatch):
    monkeypatch.setitem(sys.modules, "multipie", None)  # MultiPie is not installed: importing it fails.
    assert not check_multipie()
    assert multipie_message() == MULTIPIE_INSTALL
