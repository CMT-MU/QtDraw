"""
Tests for parsing vectors given as strings, without sympy for plain numbers (display speed).
"""

import numpy as np
import pytest

import qtdraw.core.pyvista_widget as pw
from qtdraw.util.util import str_to_sympy

CASES = [
    ("[0,0,0]", "[0,0,0]"),
    ("[0.1, 0.25, -0.5]", "[1,0,-1]"),
    ("[1e-3,2E2,-3.5e+1]", "[0,0,0]"),
    ("[0.1,0.2,0.3,]", "[0,0,0]"),  # trailing comma.
    (" [ .5 , 1. , 2 ] ", "[0,0,1]"),
    ("[[0,0,0],[0.5,0.5,0.5]]", "[0,0,0]"),
    ("[1/2,0,0]", "[0,0,0]"),  # expressions still go through sympy.
    ("[sqrt(3)/2,1/3,0]", "[0,0,0]"),
    ("[0.5,0,0]", "[0.5,0,0]"),  # a fractional cell is truncated, as before.
    ("[0,0,0]", "[0.99999999999999999,0,0]"),  # exactly below 1: cell 0, as before.
    ("[0,0,0]", "[-0.99999999999999999,0,0]"),
]


def reference(vector, cell, A):
    c = str_to_sympy(cell).astype(int)
    v = str_to_sympy(vector, rational=False).astype(float)
    return (v + c) @ A[0:3, 0:3].T


# ==================================================
@pytest.mark.parametrize("vector, cell", CASES)
def test_same_result_as_sympy(vector, cell):
    A = np.array([[1.0, 0.5, 0.0, 0.0], [0.0, 2.0, 0.0, 0.0], [0.0, 0.0, 3.0, 0.0], [0.0, 0.0, 0.0, 1.0]])
    np.testing.assert_allclose(pw.convert_str_vector(vector, cell, A=A), reference(vector, cell, A))
    np.testing.assert_allclose(pw.convert_str_vector(vector, cell, transform=False), reference(vector, cell, np.eye(4)))


# ==================================================
def test_plain_numbers_do_not_use_sympy(monkeypatch):
    calls = []
    original = pw.str_to_sympy

    def spy(*args, **kwargs):
        calls.append(args[0])
        return original(*args, **kwargs)

    monkeypatch.setattr(pw, "str_to_sympy", spy)
    pw.convert_str_vector("[0.123,0.456,0.789]", "[1,0,0]", transform=False)
    assert calls == []
    pw.convert_str_vector("[1/7,0,0]", "[0,0,0]", transform=False)
    assert calls == ["[1/7,0,0]"]


# ==================================================
def test_result_is_not_shared(monkeypatch):
    a = pw.convert_str_vector("[0.1,0.2,0.3]", transform=False)
    a[0] = 99.0  # the caller changes its array.
    assert pw.convert_str_vector("[0.1,0.2,0.3]", transform=False)[0] == pytest.approx(0.1)


# ==================================================
@pytest.mark.parametrize("vector", ["[0,0", "[a,0,0]", "1"])
def test_invalid_string_raises_as_before(vector):
    with pytest.raises(Exception) as expected:
        str_to_sympy(vector, rational=False).astype(float)
    with pytest.raises(expected.type):
        pw.convert_str_vector(vector, transform=False)


# ==================================================
def test_nonrepeat_does_not_use_sympy_for_plain_numbers(widget, monkeypatch):
    widget.add_site(position="[0.25,0.5,0]", cell="[1,0,0]")
    widget.add_site(position="[1/3,0,0]", cell="[0,1,0]")
    calls = []
    original = pw.str_to_sympy

    def spy(*args, **kwargs):
        calls.append(args[0])
        return original(*args, **kwargs)

    monkeypatch.setattr(pw, "str_to_sympy", spy)
    pw._parse_cached_clear()
    widget.nonrepeat_data()

    rows = widget.get_data_dict()["site"]
    positions = sorted(np.array(eval(r[7]), dtype=float).tolist() for r in rows)  # position column.
    np.testing.assert_allclose(positions, sorted([[1.25, 0.5, 0.0], [1 / 3, 1.0, 0.0]]))
    assert all(r[8] == "[0,0,0]" for r in rows)  # cell column.
    assert calls == ["[1/3,0,0]"]  # only the expression.


# ==================================================
def test_long_strings_are_not_cached():
    pw._parse_cached_clear()
    points = "[" + ",".join(f"[{i},0,0]" for i in range(1000)) + "]"  # e.g. a polygon.
    assert pw.convert_str_vector(points, transform=False).shape == (1000, 3)
    assert pw._parse_cache_size() == 1  # only the short cell string.


# ==================================================
def test_large_results_are_not_cached():
    pw._parse_cached_clear()
    v = pw._parse_vector("[[0,0,0]]*1000")  # short string, large result.
    assert v.shape == (1000, 3)
    assert pw._parse_cache_size() == 0


# ==================================================
def test_huge_number_gives_the_same_result_as_before():
    s = "[" + "9" * 400 + ",0,0]"
    expected = str_to_sympy(s, rational=False).astype(float)
    np.testing.assert_array_equal(pw.convert_str_vector(s, transform=False), expected)
