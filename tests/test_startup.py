"""
Regression tests for startup in an environment without optional tools.

Each case runs in a subprocess with a timeout, because the failure mode is a hang.
"""

import os
import subprocess
import sys
import textwrap

TIMEOUT = 60


def run_python(code):
    ret = subprocess.run(
        [sys.executable, "-c", textwrap.dedent(code)],
        capture_output=True,
        text=True,
        timeout=TIMEOUT,
        env={**os.environ, "QT_QPA_PLATFORM": "offscreen"},
    )
    assert ret.returncode == 0, ret.stdout + ret.stderr
    assert "OK" in ret.stdout, ret.stdout + ret.stderr
    return ret


# fake playwright: records what was started, cancelled and closed.
FAKE_PLAYWRIGHT = """
import asyncio
import qtdraw.widget.mathjax as mj

events = []

class FakeBrowser:
    async def close(self):
        events.append("browser.close.begin")
        await asyncio.sleep(0.2)  # yield, to detect interrupted cleanup.
        events.append("browser.close.end")

class FakeChromium:
    async def launch(self, **kwargs):
        try:
            {launch}
        except asyncio.CancelledError:
            events.append("launch.cancelled")
            raise
        return FakeBrowser()

class FakePlaywright:
    chromium = FakeChromium()
    async def stop(self):
        events.append("playwright.stop.begin")
        await asyncio.sleep(0.2)  # yield, to detect interrupted cleanup.
        events.append("playwright.stop.end")

class FakeStarter:
    async def start(self):
        events.append("playwright.start")
        return FakePlaywright()

mj.async_playwright = lambda: FakeStarter()
"""

LAUNCH_FAIL = "raise RuntimeError('Executable does not exist')"
LAUNCH_HANG = "await asyncio.sleep(3600)"
LAUNCH_OK = "pass"


# ==================================================
def test_mathjax_without_browser_does_not_hang():
    run_python(FAKE_PLAYWRIGHT.format(launch=LAUNCH_FAIL) + """
m = mj.MathJaxSVG()
assert not m.available
m.close()
assert not m._thread.is_alive()
assert events == ["playwright.start", "playwright.stop.begin", "playwright.stop.end"], events
print("OK")
""")


# ==================================================
def test_mathjax_launch_timeout_cancels_and_cleans_up():
    run_python(FAKE_PLAYWRIGHT.format(launch=LAUNCH_HANG) + """
import time
m = mj.MathJaxSVG(timeout=1)
assert not m.available
svg, wh = m.convert("x", "black", 12)
m.close()
assert not m._thread.is_alive()
assert events == ["playwright.start", "launch.cancelled", "playwright.stop.begin", "playwright.stop.end"], events
print("OK")
""")


# ==================================================
def test_mathjax_close_after_successful_start():
    run_python(FAKE_PLAYWRIGHT.format(launch=LAUNCH_OK) + """
m = mj.MathJaxSVG()
assert m.available
m.close()
assert not m._thread.is_alive()
assert events == ["playwright.start", "browser.close.begin", "browser.close.end", "playwright.stop.begin", "playwright.stop.end"], events
print("OK")
""")


# ==================================================
def test_mathjax_close_from_two_threads():
    run_python(FAKE_PLAYWRIGHT.format(launch=LAUNCH_HANG) + """
import threading
m = mj.MathJaxSVG(timeout=0.5)
threads = [threading.Thread(target=m.close) for _ in range(2)]
for t in threads:
    t.start()
for t in threads:
    t.join(10)
assert not any(t.is_alive() for t in threads)
assert not m._thread.is_alive()
assert events == ["playwright.start", "launch.cancelled", "playwright.stop.begin", "playwright.stop.end"], events
print("OK")
""")


# ==================================================
def test_plain_text_fallback_is_drawn():
    run_python(FAKE_PLAYWRIGHT.format(launch=LAUNCH_FAIL) + """
import xml.etree.ElementTree as ET
from qtdraw.widget.qt_event_util import get_qt_application
app = get_qt_application()
from qtdraw.util.basic_object import _svg_to_qimage

m = mj.MathJaxSVG()
for latex in ["$$x^2$$", "$a<b & c>d$"]:
    svg, (w, h) = m.convert(latex, "black", 12)
    root = ET.fromstring(svg)
    assert "".join(root.itertext()) == latex.strip("$"), svg
    assert w > 0 and h > 0
    img = _svg_to_qimage(latex, m, size=100)
    assert (img[:, :, 3] > 0).sum() > 0  # some pixels are drawn.
m.close()
print("OK")
""")


# ==================================================
def test_widget_starts_without_browser():
    run_python(FAKE_PLAYWRIGHT.format(launch=LAUNCH_FAIL) + """
from qtdraw.widget.qt_event_util import get_qt_application
app = get_qt_application()
from qtdraw.core.pyvista_widget import PyVistaWidget
from qtdraw.core.pyvista_widget_setting import COLUMN_NAME_ACTOR
w = PyVistaWidget(off_screen=True)
w.add_caption(caption="$x^2$")
w.add_text2d(caption="$\\\\alpha$")
assert len(w._data["caption"].tolist()) == 1 and len(w._data["text2d"].tolist()) == 1
assert all(row[COLUMN_NAME_ACTOR] != "" for row in w._data["text2d"].tolist())  # actor is created.
w.close()
print("OK")
""")


# ==================================================
def test_exception_hook_without_ipython():
    run_python("""
import sys
import importlib.abc


class BlockIPython(importlib.abc.MetaPathFinder):  # simulate an environment without IPython.
    def find_spec(self, name, path=None, target=None):
        if name == "IPython" or name.startswith("IPython."):
            raise ModuleNotFoundError(f"No module named '{name}'")


sys.meta_path.insert(0, BlockIPython())
from qtdraw.widget.qt_event_util import get_qt_application, ExceptionHook
app = get_qt_application()
import qtdraw.core.qtdraw_app


def broken_function():
    return 1 / 0


hook = ExceptionHook()
messages = []
hook.msg_signal.disconnect()
hook.msg_signal.connect(lambda summary, details: messages.append((summary, details)))
try:
    broken_function()
except ZeroDivisionError:
    hook.hook(*sys.exc_info())
summary, msg = messages[0]
assert summary == "ZeroDivisionError: division by zero", summary
assert "Traceback" in msg and "broken_function" in msg and "ZeroDivisionError: division by zero" in msg, msg
print("OK")
""")
