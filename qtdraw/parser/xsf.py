"""
Read data in xsf file.

Note:
    - https://web.mit.edu/xcrysden_v1.5.60/www/XCRYSDEN/doc/XSF.html#__toc__12
"""

import numpy as np
from qtdraw.util.util import create_grid


# ==================================================
def extract_data_xsf(filename):
    """
    Read xsf file (grid data part only).

    Args:
        filename (str): file name.

    Returns:
        - (dict) -- extracted data.

    Note:
        - n : [nx,ny,nz] division of grid.
        - origin : [rx,ry,rz] origin in fractional coordinate.
        - Ag : [g1,g2,g3] grid vectors in 4x4 matrix.
        - data : data at each grid point.
        - surface : surface data at each grid point.
        - endpoint : include endpoint ?
        - row_major : row-major grid ?
    """
    with open(filename, mode="r", encoding="utf-8") as f:
        s = f.read()
    s = s.replace("\n", " ")

    start = s.find("BEGIN_DATAGRID_3D_UNKNOWN")
    end = s.rfind("END_DATAGRID_3D")

    s = s[start:end]
    lst = s.split(" ")
    lst = [i for i in lst if i != ""]

    nv = np.array(lst[1:4]).astype(int)  # nx, ny, nz
    rv = np.array(lst[4:7]).astype(float)  # x0, y0, z0
    A = np.eye(4)
    A[0:3, 0] = np.array(lst[7:10]).astype(float)  # dx1, dy1, dz1
    A[0:3, 1] = np.array(lst[10:13]).astype(float)  # dx2, dy2, dz2
    A[0:3, 2] = np.array(lst[13:16]).astype(float)  # dx3, dy3, dz3
    n = nv[0] * nv[1] * nv[2]
    data = np.array(lst[16 : 16 + n]).astype(float)  # data (nx*ny*nz)
    r0 = np.linalg.inv(A)[0:3, 0:3] @ rv

    grid_data = {
        "n": nv.tolist(),
        "origin": r0.tolist(),
        "Ag": A.tolist(),
        "endpoint": True,
        "row_major": False,
        "data": np.abs(data).tolist(),
        "surface": {"phase": data.tolist()},
    }

    return grid_data


# ==================================================
def create_data(n, origin, A, endpoint, f_data, f_surface):
    r = origin + np.array([1.0, 1.0, 1.0])
    grid = create_grid(n, origin, r, A, endpoint).points

    data = f_data(grid[:, 0], grid[:, 1], grid[:, 2]).tolist()

    if f_surface is not None:
        surface = {}
        for name, f in f_surface.items():
            surface[name] = f(grid[:, 0], grid[:, 1], grid[:, 2]).tolist()
    else:
        surface = None

    grid_data = {
        "n": n,
        "origin": origin,
        "Ag": A.tolist(),
        "data": data,
        "surface": surface,
        "endpoint": endpoint,
        "row_major": False,
    }

    return grid_data
