"""
Tests for the disk cache of MathJax SVG files, shared by processes.
"""

import os

import pytest

from qtdraw.widget.mathjax import MathJaxSVG


# ==================================================
def test_cache_file_is_written_whole_or_not_at_all(tmp_path, monkeypatch):
    target = tmp_path / "a.svg"

    def fail(src, dst):
        raise OSError("disk full")

    monkeypatch.setattr(os, "replace", fail)
    with pytest.raises(OSError):
        MathJaxSVG._write_cache_file(target, '<svg viewBox="0 0 1 1"></svg>')
    assert not target.exists()  # another process never reads a partly written file.
    assert list(tmp_path.iterdir()) == []  # no temporary file is left.


# ==================================================
def test_cache_file_is_written(tmp_path):
    target = tmp_path / "a.svg"
    MathJaxSVG._write_cache_file(target, '<svg viewBox="0 0 1 1"></svg>')
    assert target.read_text() == '<svg viewBox="0 0 1 1"></svg>'
    assert list(tmp_path.iterdir()) == [target]


# ==================================================
def test_cache_file_is_read_as_utf8_and_unreadable_one_is_ignored(tmp_path):
    good = tmp_path / "good.svg"
    good.write_bytes('<svg viewBox="0 0 1 1"><text>単位胞</text></svg>'.encode("utf-8"))
    assert MathJaxSVG._read_cache_file(good) == '<svg viewBox="0 0 1 1"><text>単位胞</text></svg>'

    old = tmp_path / "old.svg"
    old.write_bytes("<svg>単位胞</svg>".encode("cp932"))  # e.g. written by an older version on Windows.
    assert MathJaxSVG._read_cache_file(old) is None  # created again instead.
    assert MathJaxSVG._read_cache_file(tmp_path / "missing.svg") is None

    partial = tmp_path / "partial.svg"
    partial.write_text("<svg xmlns=", encoding="utf-8")  # cut off, e.g. by an older version.
    assert MathJaxSVG._read_cache_file(partial) is None


# ==================================================
def test_failing_cache_write_does_not_stop_saving_others(tmp_path, monkeypatch):
    mj = MathJaxSVG.__new__(MathJaxSVG)  # without starting a browser.
    mj._cache_dir = tmp_path
    mj._svg_cache = {"a": '<svg viewBox="0 0 1 1">a</svg>', "b": '<svg viewBox="0 0 1 1">b</svg>'}
    written = []

    def write(path, text):
        if "a" in text:
            raise PermissionError("in use by another process")
        written.append(path)

    monkeypatch.setattr(MathJaxSVG, "_write_cache_file", staticmethod(write))
    mj._save_cache()  # does not raise, so closing goes on.
    assert written == [mj._get_cache_path("b")]
