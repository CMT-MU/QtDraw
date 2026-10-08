"""
Tests for command-line tools (the GUI is not started).
"""

from pathlib import Path

import pytest
from click.testing import CliRunner

from qtdraw.scripts import qtdraw as qtdraw_script
from qtdraw.scripts import conv_qtdraw3


class FakeQtDraw:
    opened = []

    def __init__(self, filename=None):
        FakeQtDraw.opened.append(filename)

    def exec(self):
        return 0


@pytest.fixture
def fake_app(monkeypatch):
    FakeQtDraw.opened = []
    monkeypatch.setattr(qtdraw_script, "QtDraw", FakeQtDraw)
    return FakeQtDraw


# ==================================================
def test_qtdraw_without_file(fake_app):
    ret = CliRunner().invoke(qtdraw_script.cmd, [])
    assert ret.exit_code == 0
    assert fake_app.opened == [None]


# ==================================================
def test_qtdraw_with_file(fake_app, tmp_path):
    file = tmp_path / "a.qtdw"
    file.write_text("{}")
    ret = CliRunner().invoke(qtdraw_script.cmd, [str(file)])
    assert ret.exit_code == 0
    assert fake_app.opened == [file.resolve()]


# ==================================================
def test_qtdraw_with_file_without_extension(fake_app, tmp_path):
    file = tmp_path / "a.qtdw"
    file.write_text("{}")
    ret = CliRunner().invoke(qtdraw_script.cmd, [str(tmp_path / "a")])
    assert ret.exit_code == 0
    assert fake_app.opened == [file.resolve()]


# ==================================================
def test_qtdraw_missing_file_is_error(fake_app, tmp_path):
    ret = CliRunner().invoke(qtdraw_script.cmd, [str(tmp_path / "missing.qtdw")])
    assert ret.exit_code != 0
    assert "missing.qtdw" in ret.output
    assert fake_app.opened == []


# ==================================================
def test_qtdraw_too_many_arguments_is_error(fake_app, tmp_path):
    ret = CliRunner().invoke(qtdraw_script.cmd, ["a.qtdw", "b.qtdw"])
    assert ret.exit_code != 0
    assert fake_app.opened == []


# ==================================================
def test_conv_qtdraw3(monkeypatch, tmp_path):
    converted = []
    monkeypatch.setattr(conv_qtdraw3, "convert_qtdraw_v3", converted.append)
    file = tmp_path / "old.qtdw"
    file.write_text("{}")

    assert CliRunner().invoke(conv_qtdraw3.cmd, [str(file)]).exit_code == 0
    assert converted == [file.resolve()]

    assert CliRunner().invoke(conv_qtdraw3.cmd, []).exit_code != 0
    assert CliRunner().invoke(conv_qtdraw3.cmd, [str(tmp_path / "missing.qtdw")]).exit_code != 0
    assert "version 3" in CliRunner().invoke(conv_qtdraw3.cmd, ["--help"]).output
