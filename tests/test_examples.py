"""
The examples of the documentation (notebooks and scripts in docs/src/examples) run and draw objects.

Each example runs in its own process on a copy of the examples, without an event loop: the code cells of a
notebook are run as one script, so the Qt integration of IPython (the event loop of a notebook) is not tested here.
Any uncaught exception, error dialog, render failure or traceback on stderr fails the example.
"""

import importlib.util
import json
import os
import shutil
import signal
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

EXAMPLES = Path(__file__).resolve().parents[1] / "docs" / "src" / "examples"
TIMEOUT = 600

PRELUDE = """
import os, sys, traceback
from pathlib import Path

def _fail(*exc):  # an error anywhere, also in a Qt slot: report it and stop.
    traceback.print_exception(*exc)
    sys.stderr.flush()
    os._exit(3)

sys.excepthook = _fail
from PySide6.QtCore import QSettings
for _scope in (QSettings.UserScope, QSettings.SystemScope):  # not the user's settings.
    QSettings.setPath(QSettings.IniFormat, _scope, os.environ["QTDRAW_TEST_HOME"])
import qtdraw.widget.mathjax as _mathjax
_init = _mathjax.MathJaxSVG.__init__
_mathjax.MathJaxSVG.__init__ = lambda self, cache_dir=None, **kw: _init(
    self, cache_dir=cache_dir or Path(os.environ["QTDRAW_TEST_HOME"]) / "svg_cache", **kw
)  # not the user's cache.
import qtdraw.widget.message_box as _message_box
import qtdraw.widget.qt_event_util as _qt_event_util

def _dialog(summary, details, title=""):  # the error dialog of QtDraw's exception hook.
    print(details, file=sys.stderr, flush=True)
    os._exit(3)

_message_box.show_error = _qt_event_util.show_error = _dialog
from PySide6.QtWidgets import QApplication, QMessageBox
QMessageBox.question = lambda *args, **kwargs: QMessageBox.Discard
import qtdraw.core.qtdraw_app as _qtdraw_app
_qtdraw_app.QtDraw.exec = lambda self: None  # no event loop: the example only draws.
from qtdraw.core.pyvista_widget import PyVistaWidget as _Widget
_write_info = _Widget.write_info

def _info(self, text):  # e.g. "* failed to render: ..." after a load.
    if "failed" in text:
        print(text, file=sys.stderr, flush=True)
        os._exit(4)
    _write_info(self, text)

_Widget.write_info = _info
"""

DRAWN = """
def _rows():
    widgets = [w for w in QApplication.allWidgets() if isinstance(w, _Widget)]
    for w in widgets:
        w.render()  # draws without an error.
    return [sum(len(rows) for rows in w.get_data_dict().values()) for w in widgets]

print("ROWS", _rows(), flush=True)
assert _rows() and all(n > 0 for n in _rows()), _rows()
"""

END = """
print("OK", flush=True)
os._exit(0)  # widgets left open (as in a notebook) would keep background threads alive.
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
    home = tmp_path / "home"
    home.mkdir()
    env = {**os.environ, "QT_QPA_PLATFORM": "offscreen", "QTDRAW_TEST_HOME": str(home)}
    script = work / "run_example.py"
    script.write_text(textwrap.dedent(PRELUDE) + "\n" + code + "\n" + END)
    out, err = tmp_path / "stdout.txt", tmp_path / "stderr.txt"
    with open(out, "w") as fout, open(err, "w") as ferr:  # files: a helper process may keep pipes open.
        proc = subprocess.Popen(
            [sys.executable, str(script)], cwd=work, stdout=fout, stderr=ferr, env=env, start_new_session=True
        )
        try:
            proc.wait(timeout=TIMEOUT)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)  # also helper processes, e.g. the browser for MathJax.
            proc.wait()
    stdout, stderr = out.read_text(), err.read_text()
    report = stdout[-2000:] + stderr[-4000:]
    assert proc.returncode == 0 and "OK" in stdout, report
    assert "Traceback" not in stderr, report
    return work


needs_multipie = pytest.mark.skipif(importlib.util.find_spec("multipie") is None, reason="MultiPie is not installed.")


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
    run_example(notebook_code("multipie.ipynb") + "\n" + every + "\n" + DRAWN, tmp_path)


def test_pyvista_widget_notebook_writes_a_file(tmp_path):
    code = notebook_code("pyvista_widget.ipynb")
    assert code.rstrip().endswith("ex2()")
    code = code.rstrip()[: -len("ex2()")] + "ex1()\n"  # its other example, alone in its process.
    work = run_example(code, tmp_path)
    from qtdraw.util.util import read_dict

    assert read_dict(str(work / "example_output.qtdw"))["data"]


# ==================================================
@pytest.mark.parametrize("name", ["background.py", "background_s.py"])
def test_script_writes_a_drawing(name, tmp_path):
    work = run_example((EXAMPLES / name).read_text(), tmp_path)
    from qtdraw.util.util import read_dict

    assert len(read_dict(str(work / "output.qtdw"))["data"]["site"]) == 32


@pytest.mark.parametrize("name", ["isosurface.py", "load.py"])
def test_script_draws(name, tmp_path):
    run_example((EXAMPLES / name).read_text() + "\n" + DRAWN, tmp_path)
