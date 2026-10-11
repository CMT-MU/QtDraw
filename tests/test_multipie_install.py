"""
Without MultiPie, the MultiPie button offers to install it with pip, and MultiPie is used after the installation
without restarting QtDraw. The installation is replaced by a script here: pip is not run.
"""

import os
import subprocess
import sys
import textwrap

import pytest

from qtdraw.util.util import check_multipie, command_text, install_multipie_command, multipie_missing

# MultiPie is not found until the flag file is written by the (replaced) installation.
PRELUDE = """
import os, sys
from pathlib import Path
from PySide6.QtCore import QSettings
home = Path(os.environ["QTDRAW_TEST_HOME"])
for scope in (QSettings.UserScope, QSettings.SystemScope):  # not the user's settings.
    QSettings.setPath(QSettings.IniFormat, scope, str(home))
import qtdraw.widget.mathjax as mathjax
init = mathjax.MathJaxSVG.__init__
mathjax.MathJaxSVG.__init__ = lambda self, cache_dir=None, **kw: init(self, cache_dir=cache_dir or home / "svg_cache", **kw)
flag = home / "installed"
sys.path.insert(0, str(home / "site"))  # where a replaced installation may write a package.


class NotInstalled:
    def find_spec(self, name, path=None, target=None):
        if (name == "multipie" or name.startswith("multipie.")) and not flag.exists():
            raise ModuleNotFoundError(f"No module named {name!r}", name=name)


sys.meta_path.insert(0, NotInstalled())
from PySide6.QtWidgets import QApplication, QMessageBox
import qtdraw.core.qtdraw_app as qtdraw_app
from qtdraw.core.qtdraw_app import QtDraw
from qtdraw.util.util import check_multipie, multipie_missing
assert not check_multipie() and multipie_missing()
asked, shown = [], []


answers = os.environ["ANSWER"].split(",")  # one for each question, the last one also for later questions.


def question(*a, **k):
    asked.append(a[2])
    answer = answers.pop(0) if len(answers) > 1 else answers[0]
    return QMessageBox.Yes if answer == "yes" else QMessageBox.No


QMessageBox.question = question
for kind in ("information", "warning"):
    setattr(QMessageBox, kind, lambda *a, k=kind, **kw: shown.append((k, a[2])) or QMessageBox.Ok)
window = QtDraw()
import traceback
import qtdraw.widget.qt_event_util as qt_event_util


def fail(*exc):  # an error, also in a Qt slot, ends the process: no error dialog waits for a click.
    traceback.print_exception(*exc)
    sys.stderr.flush()
    os._exit(3)


sys.excepthook = qt_event_util.ExceptionHook.hook = lambda *exc: fail(*exc[-3:])


def wait():
    while window._multipie_install is not None:  # the installation runs in the background.
        QApplication.processEvents()
"""


def run(tmp_path, answer, install, code):
    """
    Click the MultiPie button without MultiPie, with the installation replaced by the script install.
    """
    script = PRELUDE + f"qtdraw_app.install_multipie_command = lambda: [sys.executable, '-c', {install!r}]\n"
    code = "window.misc_button_multipie.click()\nwait()\n" + textwrap.dedent(code) + "\nprint('OK', flush=True)\n"
    script += f"try:\n{textwrap.indent(code, '    ')}except BaseException:\n    fail(*sys.exc_info())\nos._exit(0)\n"
    env = {**os.environ, "QT_QPA_PLATFORM": "offscreen", "QTDRAW_TEST_HOME": str(tmp_path), "ANSWER": answer}
    ret = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, timeout=180, env=env)
    assert ret.returncode == 0 and "OK" in ret.stdout, ret.stdout + ret.stderr[-3000:]


INSTALLS = "import os; open(os.path.join(os.environ['QTDRAW_TEST_HOME'], 'installed'), 'w').close(); print('Successfully installed multipie')"
# a MultiPie that is installed but cannot be loaded, as MultiPie 2.3.4 on Python 3.11.
BROKEN = (
    "import os, pathlib; home = pathlib.Path(os.environ['QTDRAW_TEST_HOME']); package = home / 'site' / 'multipie'; "
    "package.mkdir(parents=True); (package / '__init__.py').write_text('from .group import Group'); "
    "(package / 'group.py').write_text('s = ('); (home / 'installed').touch()"
)
NOT_FOUND = "print('Successfully installed multipie')"  # where this Python does not search.
FAILS = "import sys; print('No module named pip'); sys.exit(1)"


# ==================================================
def test_install_command_uses_pip_of_this_python():
    assert install_multipie_command()[:4] == [sys.executable, "-m", "pip", "install"]
    assert install_multipie_command()[4:] == ["multipie"]


def test_command_text_can_be_run_in_a_shell():
    command = ["/path with space/python", "-m", "pip", "install", "multipie"]
    if sys.platform == "win32":
        assert command_text(command) == '"/path with space/python" -m pip install multipie'
    else:
        import shlex

        assert shlex.split(command_text(command)) == command
    assert not set("<>|&;") & set(command_text(install_multipie_command()))  # nothing a shell would take.


def test_missing_multipie(monkeypatch):
    monkeypatch.setitem(sys.modules, "multipie", None)  # MultiPie is not installed: importing it fails.
    assert multipie_missing()


@pytest.mark.skipif(not check_multipie(), reason="MultiPie cannot be loaded.")
def test_multipie_that_loads_is_not_missing():
    assert not multipie_missing()


# ==================================================
def test_declining_does_not_install(tmp_path):
    run(
        tmp_path,
        "no",
        INSTALLS,
        """
        assert len(asked) == 1 and "pip install" in asked[0], asked
        assert not flag.exists() and shown == [] and window.multipie_dialog is None
        """,
    )


@pytest.mark.skipif(not check_multipie(), reason="MultiPie cannot be loaded.")
def test_installing_opens_multipie_without_restart(tmp_path):
    run(
        tmp_path,
        "yes",
        INSTALLS,
        """
        assert flag.exists() and check_multipie()
        assert "Successfully installed multipie" in window.logger.log.toPlainText()
        assert window.multipie_dialog is not None, shown  # opened after the installation.
        assert window.misc_button_multipie.isEnabled()
        """,
    )


def test_installed_multipie_that_cannot_be_loaded_is_told(tmp_path):
    run(
        tmp_path,
        "yes",
        BROKEN,
        """
        assert flag.exists() and window.multipie_dialog is None
        assert len(shown) == 1 and "cannot be loaded" in shown[0][1], shown
        """,
    )


def test_installed_multipie_that_is_not_found_asks_to_restart(tmp_path):
    run(
        tmp_path,
        "yes",
        NOT_FOUND,
        """
        assert window.multipie_dialog is None
        assert len(shown) == 1 and "Restart QtDraw" in shown[0][1], shown
        """,
    )


def test_failed_installation_tells_why_and_how(tmp_path):
    run(
        tmp_path,
        "yes",
        FAILS,
        """
        assert window.multipie_dialog is None and window.misc_button_multipie.isEnabled()
        assert len(shown) == 1 and shown[0][0] == "warning", shown
        assert "No module named pip" in shown[0][1] and "sys.exit(1)" in shown[0][1], shown  # the command by hand.
        """,
    )


def test_installation_that_cannot_start_tells_how(tmp_path):
    script = PRELUDE + "qtdraw_app.install_multipie_command = lambda: [str(home / 'no-such-python')]\n"
    script += textwrap.dedent("""
        try:
            window.misc_button_multipie.click()
            wait()
            assert window.multipie_dialog is None and window.misc_button_multipie.isEnabled()
            assert len(shown) == 1 and shown[0][0] == "warning" and "no-such-python" in shown[0][1], shown
            print("OK", flush=True)
        except BaseException:
            fail(*sys.exc_info())
        os._exit(0)
        """)
    env = {**os.environ, "QT_QPA_PLATFORM": "offscreen", "QTDRAW_TEST_HOME": str(tmp_path), "ANSWER": "yes"}
    ret = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, timeout=180, env=env)
    assert ret.returncode == 0 and "OK" in ret.stdout, ret.stdout + ret.stderr[-3000:]


@pytest.mark.parametrize("stop", [False, True])
def test_closing_while_installing_asks_to_stop_it(tmp_path, stop):
    script = PRELUDE + "qtdraw_app.install_multipie_command = lambda: [sys.executable, '-c', 'import time; time.sleep(120)']\n"
    script += textwrap.dedent(f"""
        try:
            window.misc_button_multipie.click()
            process = window._multipie_install
            assert process is not None and process.waitForStarted(30000)
            window.close()
            assert "being installed" in asked[-1], asked
            if {stop}:  # stopped and closed.
                assert window._multipie_install is None and process.state() == process.ProcessState.NotRunning
                assert QApplication.overrideCursor() is None
            else:  # still installing, and the window is open.
                assert window.isVisible() and window._multipie_install is process
                assert process.state() == process.ProcessState.Running
                process.kill()
                process.waitForFinished(30000)
            print("OK", flush=True)
        except BaseException:
            fail(*sys.exc_info())
        os._exit(0)
        """)
    env = {**os.environ, "QT_QPA_PLATFORM": "offscreen", "QTDRAW_TEST_HOME": str(tmp_path)}
    env["ANSWER"] = "yes,yes" if stop else "yes,no"
    ret = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, timeout=180, env=env)
    assert ret.returncode == 0 and "OK" in ret.stdout, ret.stdout + ret.stderr[-3000:]


def test_installation_that_ends_while_asking_to_stop_it(tmp_path):
    script = PRELUDE + "qtdraw_app.install_multipie_command = lambda: [sys.executable, '-c', 'import time; time.sleep(2)']\n"
    script += textwrap.dedent("""
        def question(*a, **k):  # the installation ends while the question is shown.
            asked.append(a[2])
            if "being installed" in a[2]:
                process.waitForFinished(30000)
                while window._multipie_install is not None:
                    QApplication.processEvents()
            return QMessageBox.Yes


        QMessageBox.question = question
        try:
            window.misc_button_multipie.click()
            process = window._multipie_install
            assert process is not None and process.waitForStarted(30000)
            window.close()
            assert "being installed" in asked[-1] and not window.isVisible(), asked
            assert QApplication.overrideCursor() is None
            print("OK", flush=True)
        except BaseException:
            fail(*sys.exc_info())
        os._exit(0)
        """)
    env = {**os.environ, "QT_QPA_PLATFORM": "offscreen", "QTDRAW_TEST_HOME": str(tmp_path), "ANSWER": "yes"}
    ret = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, timeout=180, env=env)
    assert ret.returncode == 0 and "OK" in ret.stdout, ret.stdout + ret.stderr[-3000:]
