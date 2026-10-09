"""
Small isosurface data for tests (the 72x72x72 grid of the example Si.xsf is slow to write and read again).
"""

from pathlib import Path

import numpy as np

from qtdraw.parser.xsf import extract_data_xsf

HEADER = """CRYSTAL
PRIMVEC
  -2.6988040   0.0000000   2.6988040
   0.0000000   2.6988040   2.6988040
  -2.6988040   2.6988040   0.0000000
PRIMCOORD
     2  1
Si      0.0000000   0.0000000   0.0000000
Si      1.3494020   1.3494020   1.3494020

BEGIN_BLOCK_DATAGRID_3D
3D_field
BEGIN_DATAGRID_3D_UNKNOWN
"""


# ==================================================
def write_small_xsf(filename, n=8):
    """
    Write an XSF file with an n x n x n grid, the lattice of the example Si.xsf.

    The data has both signs, and its absolute value crosses the isosurface value 0.01 used in the tests.

    Args:
        filename (str or Path): file name.
        n (int, optional): number of grid points in each direction.
    """
    x = np.linspace(0.0, 1.0, n)
    X, Y, Z = np.meshgrid(x, x, x, indexing="ij")
    data = 0.05 * np.cos(2 * np.pi * X) * np.cos(2 * np.pi * Y) * np.cos(2 * np.pi * Z)
    values = " ".join(f"{v:.5E}" for v in data.ravel(order="F"))  # x runs fastest in XSF.
    text = (
        HEADER
        + f"    {n}    {n}    {n}\n"
        + "    0.000000    0.000000    0.000000\n"
        + "  -5.3226412   0.0000000   5.3226412\n"
        + "   0.0000000   5.3226412   5.3226412\n"
        + "  -5.3226412   5.3226412   0.0000000\n"
        + values
        + "\nEND_DATAGRID_3D\nEND_BLOCK_DATAGRID_3D\n"
    )
    Path(filename).write_text(text)


# ==================================================
def small_grid(tmp_path):
    """
    Grid data of a small XSF file.

    Args:
        tmp_path (Path): directory for the file.

    Returns:
        - (dict) -- grid data as extract_data_xsf() returns it.
    """
    file = Path(tmp_path) / ".small_grid.xsf"
    write_small_xsf(file)
    return extract_data_xsf(str(file))
