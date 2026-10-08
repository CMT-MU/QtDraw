"""
Regression tests for isosurface/volume data handling and position parsing.
"""

from pathlib import Path

import numpy as np
import pytest

from qtdraw.core.pyvista_widget_setting import COLUMN_NAME_ACTOR, COLUMN_POSITION, COLUMN_CELL
from qtdraw.util.basic_object import create_isosurface
from qtdraw.util.util import create_grid
from qtdraw.parser.xsf import create_data

EXAMPLES = Path(__file__).resolve().parents[1] / "docs" / "src" / "examples"


def rows(widget, object_type):
    return widget._data[object_type].tolist()


def grid_values(n, f):
    # values at grid points in column-major order (x fastest), as create_grid.
    points = create_grid(n, [0, 0, 0], [1, 1, 1], None, True).points
    return f(points[:, 0], points[:, 1], points[:, 2])


# ==================================================
def sorted_points(points):
    points = np.round(np.asarray(points), 10)
    return points[np.lexsort(points.T[::-1])]


# ==================================================
@pytest.mark.parametrize("n", [[2, 2, 2], [3, 4, 5], [4, 3, 2]])
def test_row_major_data_is_transposed(n):
    f = lambda x, y, z: x + 2 * y + 4 * z
    g = lambda x, y, z: x - y * z
    col = grid_values(n, f)
    col_s = grid_values(n, g)
    # same values in row-major order (z fastest).
    to_row = lambda v: v.reshape(n[2], n[1], n[0]).transpose(2, 1, 0).reshape(-1)

    base = {"n": n, "origin": [0, 0, 0], "Ag": np.eye(4).tolist(), "endpoint": True}
    expected = create_isosurface(base | {"data": col.tolist(), "surface": {"s": col_s.tolist()}, "row_major": False}, [3.0], "s")
    result = create_isosurface(
        base | {"data": to_row(col).tolist(), "surface": {"s": to_row(col_s).tolist()}, "row_major": True}, [3.0], "s"
    )

    assert result.n_points > 0
    np.testing.assert_allclose(sorted_points(result.points), sorted_points(expected.points), atol=1e-9)
    # surface value is attached to the same point.
    pr = np.column_stack([result.points, result["s"]])
    pe = np.column_stack([expected.points, expected["s"]])
    np.testing.assert_allclose(sorted_points(pr), sorted_points(pe), atol=1e-9)


# ==================================================
def test_isosurface_without_surface_data(widget):
    n = [5, 5, 5]
    grid = create_data(n, np.array([0.0, 0.0, 0.0]), np.eye(4), True, lambda x, y, z: x + y + z, None)
    assert grid["surface"] is None
    widget.add_isosurface(data=("nosurface", grid), value=[1.5], surface="phase")

    assert rows(widget, "isosurface")[0][COLUMN_NAME_ACTOR] != ""


# ==================================================
def test_nonrepeat_with_fractional_position(widget):
    widget.add_site(position="[1/2,1/3,0]", cell="[1,0,-1]")
    widget.add_bond(position="[1/4,0,0]", direction="[1,0,0]", cell="[0,2,0]")

    widget.set_nonrepeat()

    site = rows(widget, "site")[0]
    np.testing.assert_allclose(eval(site[COLUMN_POSITION]), [1.5, 1 / 3, -1.0])
    assert site[COLUMN_CELL].replace(" ", "") == "[0,0,0]"
    bond = rows(widget, "bond")[0]
    np.testing.assert_allclose(eval(bond[COLUMN_POSITION]), [0.25, 2.0, 0.0])


# ==================================================
@pytest.mark.parametrize("s", ["[[Q1,1,[1,0,0]", "]]", "[[Q1,1,[1,0,0]]]", "[[Q1]]"])
def test_parse_modulation_invalid(s):
    from qtdraw.multipie.multipie_data import MultiPieData

    assert MultiPieData._parse_modulation(s) == ([], False)


# ==================================================
def test_parse_modulation_valid():
    from qtdraw.multipie.multipie_data import MultiPieData

    rows_, magnetic = MultiPieData._parse_modulation("[[Q1,1,[1,0,0],cos],[Q2,2,[0,1,0],sin]]")
    assert rows_ == [["Q1", "1", "[1,0,0]", "cos"], ["Q2", "2", "[0,1,0]", "sin"]]
    assert magnetic is False
