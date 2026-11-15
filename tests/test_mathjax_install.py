# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2021- The QtDraw developers
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""
Without the browser of playwright, QtDraw offers to install it (only the headless shell of chromium), and LaTeX is
drawn with MathJax after the installation without restarting QtDraw. The installation is replaced by a script here.
"""

import asyncio
import sys
import time

import pytest
import shiboken6
from playwright.async_api import Error as PlaywrightError
from PySide6.QtWidgets import QMessageBox

import qtdraw.widget.mathjax as mathjax
from qtdraw.widget.mathjax import MathJaxSVG, install_browser_command

MISSING = "BrowserType.launch: Executable doesn't exist at /nowhere/chrome-headless-shell"
NO_LIBRARIES = "BrowserType.launch: Host system is missing dependencies to run browsers."


# ==================================================
def browser_fails(monkeypatch, message, until=None):
    """
    The browser does not start with the error message, until the file "until" exists.
    """
    init = MathJaxSVG._async_init

    async def fake(self):
        if until is not None and until.exists():
            return await init(self)
        self._init_task = asyncio.current_task()
        self._error = PlaywrightError(message)
        self._ready.set()

    monkeypatch.setattr(MathJaxSVG, "_async_init", fake)


# ==================================================
@pytest.fixture
def browser_installed():
    converter = MathJaxSVG(timeout=60)
    try:
        if not converter.available:
            pytest.skip("the browser of playwright is not installed.")
    finally:
        converter.close()


# ==================================================
def test_only_the_headless_shell_is_installed():
    command = install_browser_command()
    assert command[:3] == [sys.executable, "-m", "playwright"]
    assert command[3:] == ["install", "--only-shell", "chromium"]
    assert mathjax.INSTALL_BROWSER == "playwright install --only-shell chromium"


# ==================================================
def test_missing_browser_is_told(monkeypatch):
    browser_fails(monkeypatch, MISSING)
    converter = MathJaxSVG(timeout=10)
    try:
        assert not converter.available and converter.browser_missing and not converter.dependencies_missing
        svg, wh = converter.convert("$x$")  # plain text.
        assert "<text" in svg
    finally:
        converter.close()


# ==================================================
def test_missing_libraries_are_told(monkeypatch):
    browser_fails(monkeypatch, NO_LIBRARIES)
    converter = MathJaxSVG(timeout=10)
    try:
        assert not converter.available and converter.dependencies_missing and not converter.browser_missing
    finally:
        converter.close()


# ==================================================
def test_retry_starts_the_installed_browser(monkeypatch, tmp_path, browser_installed):
    installed = tmp_path / "installed"
    browser_fails(monkeypatch, MISSING, until=installed)
    converter = MathJaxSVG(timeout=10)
    try:
        assert converter.browser_missing
        assert not MathJaxSVG.retry_all(timeout=10)  # still missing.
        installed.touch()
        assert MathJaxSVG.retry_all(timeout=60) and converter.available and not converter.browser_missing
        svg, wh = converter.convert("$x$")
        assert "<text" not in svg  # drawn by MathJax.
    finally:
        converter.close()
    assert converter not in MathJaxSVG._instances
    assert not converter.retry(timeout=10)  # closed.


# ==================================================
@pytest.fixture
def window(qapp, tmp_path, monkeypatch):
    import qtdraw.core.qtdraw_app as app_module

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(app_module, "can_ask", lambda: True)  # as on a screen.
    created = []

    def create():
        created.append(app_module.QtDraw())
        return created[-1]

    yield create
    monkeypatch.setattr(QMessageBox, "question", lambda *a, **k: QMessageBox.Discard)
    for w in created:
        if shiboken6.isValid(w):
            w.close()


# ==================================================
def questions(monkeypatch, answer, check=False):
    """
    Questions about MathJax, answered with "answer" (and "Do not ask again" if check).
    """
    asked = []

    def ask(box):
        asked.append(box.text())
        if check:
            box.checkBox().setChecked(True)  # the check box of the dialog.
        return answer

    monkeypatch.setattr(QMessageBox, "exec", ask)
    return asked


# ==================================================
def messages(monkeypatch):
    shown = []
    monkeypatch.setattr(QMessageBox, "information", lambda parent, title, text, *a: shown.append(("info", text)))
    monkeypatch.setattr(QMessageBox, "warning", lambda parent, title, text, *a: shown.append(("warning", text)))
    return shown


# ==================================================
def wait_install(qapp, w, timeout=120):
    deadline = time.monotonic() + timeout
    while w._browser_install is not None:
        assert time.monotonic() < deadline, "the installation did not finish."
        qapp.processEvents()
        time.sleep(0.01)


# ==================================================
def installation(monkeypatch, script):
    import qtdraw.core.qtdraw_app as app_module

    monkeypatch.setattr(app_module, "install_browser_command", lambda: [sys.executable, "-c", script])


# ==================================================
def test_installed_browser_draws_latex_without_restart(qapp, window, monkeypatch, tmp_path, browser_installed):
    installed = tmp_path / "installed"
    browser_fails(monkeypatch, MISSING, until=installed)
    installation(monkeypatch, f"open({str(installed)!r}, 'w').close(); print('installed')")
    asked = questions(monkeypatch, QMessageBox.Yes)
    shown = messages(monkeypatch)

    w = window()
    assert w.pyvista_widget._mathjax.browser_missing
    qapp.processEvents()  # asked after the window is shown.
    assert len(asked) == 1 and "not installed" in asked[0] and "200 MB" in asked[0]
    wait_install(qapp, w)
    assert shown == [("info", "The browser was installed. LaTeX is drawn with MathJax.")]
    assert w.pyvista_widget._mathjax.available
    assert "installed" in w.logger.log.toPlainText()  # output of the installation in the Log window.
    qapp.processEvents()
    assert len(asked) == 1  # not asked again.


# ==================================================
def test_failed_installation_is_told(qapp, window, monkeypatch):
    browser_fails(monkeypatch, MISSING)
    installation(monkeypatch, "import sys; print('no network'); sys.exit(1)")
    questions(monkeypatch, QMessageBox.Yes)
    shown = messages(monkeypatch)

    w = window()
    qapp.processEvents()
    wait_install(qapp, w)
    assert len(shown) == 1 and shown[0][0] == "warning"
    assert "could not be installed" in shown[0][1] and "no network" in shown[0][1]
    assert "Install it by hand with:" in shown[0][1]
    assert not w.pyvista_widget._mathjax.available


# ==================================================
def test_do_not_ask_again(qapp, window, monkeypatch):
    browser_fails(monkeypatch, MISSING)
    asked = questions(monkeypatch, QMessageBox.No, check=True)

    w = window()
    qapp.processEvents()
    assert len(asked) == 1 and w._browser_install is None
    w._check_mathjax()
    assert len(asked) == 1  # not asked again, also in a new window.
    window()
    qapp.processEvents()
    assert len(asked) == 1


# ==================================================
def test_missing_libraries_are_explained(qapp, window, monkeypatch):
    browser_fails(monkeypatch, NO_LIBRARIES)
    asked = questions(monkeypatch, QMessageBox.Ok)

    w = window()
    qapp.processEvents()
    assert len(asked) == 1 and "sudo playwright install-deps chromium" in asked[0]
    assert w._browser_install is None  # not installed by QtDraw (needs root).


# ==================================================
def test_not_asked_off_screen(qapp, tmp_path, monkeypatch):
    from qtdraw.core.qtdraw_app import QtDraw

    browser_fails(monkeypatch, MISSING)
    asked = questions(monkeypatch, QMessageBox.Yes)
    monkeypatch.chdir(tmp_path)
    w = QtDraw()
    try:
        qapp.processEvents()
        assert asked == [] and w._browser_install is None  # e.g. in tests and on CI.
    finally:
        monkeypatch.setattr(QMessageBox, "question", lambda *a, **k: QMessageBox.Discard)
        w.close()
