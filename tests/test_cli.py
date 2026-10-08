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
    assert ret.exit_code == 2, ret.output
    assert "missing.qtdw" in ret.output
    assert fake_app.opened == []


# ==================================================
def test_qtdraw_too_many_arguments_is_error(fake_app, tmp_path):
    ret = CliRunner().invoke(qtdraw_script.cmd, ["a.qtdw", "b.qtdw"])
    assert ret.exit_code == 2, ret.output
    assert fake_app.opened == []


# ==================================================
@pytest.mark.parametrize("name", [".", "/", ""])
def test_qtdraw_invalid_name_is_usage_error(fake_app, name):
    ret = CliRunner().invoke(qtdraw_script.cmd, [name])
    assert ret.exit_code == 2, ret.output
    assert fake_app.opened == []


# ==================================================
def test_qtdraw_relative_path(fake_app, tmp_path, monkeypatch):
    (tmp_path / "sub").mkdir()
    file = tmp_path / "sub" / "a.qtdw"
    file.write_text("{}")
    monkeypatch.chdir(tmp_path)
    ret = CliRunner().invoke(qtdraw_script.cmd, ["sub/a"])
    assert ret.exit_code == 0, ret.output
    assert fake_app.opened == [file.resolve()]


# ==================================================
def test_qtdraw_directory_with_same_name(fake_app, tmp_path):
    (tmp_path / "a").mkdir()
    file = tmp_path / "a.qtdw"
    file.write_text("{}")
    ret = CliRunner().invoke(qtdraw_script.cmd, [str(tmp_path / "a")])
    assert ret.exit_code == 0, ret.output
    assert fake_app.opened == [file.resolve()]

    ret = CliRunner().invoke(qtdraw_script.cmd, [str(tmp_path)])  # directory only.
    assert ret.exit_code == 2, ret.output


# ==================================================
def test_conv_qtdraw3(monkeypatch, tmp_path):
    converted = []
    monkeypatch.setattr(conv_qtdraw3, "convert_qtdraw_v3", converted.append)
    file = tmp_path / "old.qtdw"
    file.write_text("{}")

    assert CliRunner().invoke(conv_qtdraw3.cmd, [str(file)]).exit_code == 0
    assert CliRunner().invoke(conv_qtdraw3.cmd, [str(tmp_path / "old")]).exit_code == 0
    assert converted == [file.resolve(), file.resolve()]

    for args in [[], [str(tmp_path / "missing.qtdw")], [str(file), str(file)], ["."]]:
        ret = CliRunner().invoke(conv_qtdraw3.cmd, args)
        assert ret.exit_code == 2, (args, ret.output)
    assert converted == [file.resolve(), file.resolve()]
    assert "version 3" in CliRunner().invoke(conv_qtdraw3.cmd, ["--help"]).output
