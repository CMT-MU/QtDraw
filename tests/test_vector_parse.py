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
@pytest.mark.parametrize("vector", ["[0,0", "[01,0,0]", "[a,0,0]"])
def test_invalid_string_raises_as_before(vector):
    with pytest.raises(Exception) as expected:
        str_to_sympy(vector, rational=False).astype(float)
    with pytest.raises(expected.type):
        pw.convert_str_vector(vector, transform=False)
