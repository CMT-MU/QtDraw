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
