"""
The examples of the documentation (notebooks and scripts in docs/src/examples) run and draw objects.

Each example runs in its own process on a copy of the examples, without an event loop: the code cells of a
notebook are run as one script. An error dialog ends the process with the error instead of waiting.
"""

import json
import os
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

from qtdraw.util.util import check_multipie

EXAMPLES = Path(__file__).resolve().parents[1] / "docs" / "src" / "examples"
TIMEOUT = 600

PRELUDE = """
import os, sys
from PySide6.QtCore import QSettings
QSettings.setPath(QSettings.IniFormat, QSettings.UserScope, os.environ["QTDRAW_TEST_SETTINGS"])  # not the user's settings.
import qtdraw.widget.message_box as _message_box
import qtdraw.widget.qt_event_util as _qt_event_util

def _fail(summary, details, title=""):  # an error in a slot: report it and stop, instead of a dialog.
    print(details, file=sys.stderr, flush=True)
    os._exit(3)

_message_box.show_error = _qt_event_util.show_error = _fail
from PySide6.QtWidgets import QApplication, QMessageBox
QMessageBox.question = lambda *args, **kwargs: QMessageBox.Discard
import qtdraw.core.qtdraw_app as _qtdraw_app
_qtdraw_app.QtDraw.exec = lambda self: None  # no event loop: the example only draws.
"""

DRAWN = """
from qtdraw.core.pyvista_widget import PyVistaWidget as _Widget

def _rows():
    widgets = [w for w in QApplication.allWidgets() if isinstance(w, _Widget)]
    return [sum(len(rows) for rows in w.get_data_dict().values()) for w in widgets]

print("ROWS", _rows(), flush=True)
assert _rows() and all(n > 0 for n in _rows()), _rows()
"""


def notebook_code(name):
    cells = json.loads((EXAMPLES / name).read_text())["cells"]
    lines = []
    for cell in cells:
        if cell["cell_type"] == "code":
            source = "".join(cell["source"])
            lines += [line for line in source.splitlines() if not line.lstrip().startswith(("%", "!"))]
    return "\n".join(lines)


def run_example(code, tmp_path):
    work = tmp_path / "examples"
    shutil.copytree(EXAMPLES, work)
    env = {**os.environ, "QT_QPA_PLATFORM": "offscreen", "QTDRAW_TEST_SETTINGS": str(tmp_path / "settings")}
    script = work / "run_example.py"
    script.write_text(textwrap.dedent(PRELUDE) + "\n" + code + "\nprint('OK', flush=True)\n")
    ret = subprocess.run([sys.executable, str(script)], cwd=work, capture_output=True, text=True, timeout=TIMEOUT, env=env)
    assert ret.returncode == 0 and "OK" in ret.stdout, ret.stdout[-2000:] + ret.stderr[-4000:]
    return work, ret


needs_multipie = pytest.mark.skipif(not check_multipie(), reason="MultiPie is not installed.")


# ==================================================
@pytest.mark.parametrize(
    "name",
    [
        "qtdraw.ipynb",
        "pyvista_widget.ipynb",
        pytest.param("mp_graphene.ipynb", marks=needs_multipie),
        pytest.param("mp_Te.ipynb", marks=needs_multipie),
    ],
)
def test_notebook_draws(name, tmp_path):
    run_example(notebook_code(name) + "\n" + DRAWN, tmp_path)


@needs_multipie
def test_multipie_notebook_draws_every_example(tmp_path):
    every = """
for _number, _draw in enumerate(fl):  # the notebook draws one of them, chosen by `no`.
    win.clear_data()
    _draw(win)
    assert sum(len(rows) for rows in win.pyvista_widget.get_data_dict().values()) > 0, _number
"""
    run_example(notebook_code("multipie.ipynb") + "\n" + every, tmp_path)


def test_pyvista_widget_notebook_writes_a_file(tmp_path):
    work, _ = run_example(notebook_code("pyvista_widget.ipynb") + "\nex1()\n", tmp_path)
    from qtdraw.util.util import read_dict

    assert read_dict(str(work / "example_output.qtdw"))["data"]


# ==================================================
@pytest.mark.parametrize("name", ["background.py", "background_s.py"])
def test_script_writes_a_drawing(name, tmp_path):
    work, _ = run_example((EXAMPLES / name).read_text(), tmp_path)
    from qtdraw.util.util import read_dict

    assert len(read_dict(str(work / "output.qtdw"))["data"]["site"]) == 32


@pytest.mark.parametrize("name", ["isosurface.py", "load.py"])
def test_script_draws(name, tmp_path):
    run_example((EXAMPLES / name).read_text() + "\n" + DRAWN, tmp_path)
