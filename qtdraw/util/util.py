"""
Utility.

This module contains the versatile utilities.
"""

import ast
from pathlib import Path
import pyvista as pv
import numpy as np
import matplotlib.pyplot as plt
from gcoreutils.convert_util import text_to_list, apply
from qtdraw.util.util_str import str_to_sympy1


# ==================================================
def convert_to_str(v):
    """
    Convert from object to str, and remove spaces.

    Args:
        v (Any): object.

    Returns:
        - (str) -- converted str.
    """
    return str(v).replace(" ", "").replace("\t", "").replace("\n", "")


# ==================================================
def read_dict(filename):
    """
    Read dict text file.

    Args:
        filename (str): file name.

    Returns:
        - (dict) -- dictionary from dict text.
    """
    with open(filename, mode="r", encoding="utf-8") as f:
        s = f.read()

    if s[: s.find("{")].count("=") > 0:
        s = s.split("=")[-1].strip(" ")

    c = ast.get_docstring(ast.parse(s))
    if c is not None:
        s = s.replace(c, "").replace('"""', "")
    d = ast.literal_eval(s)

    return d


# ==================================================
def write_dict(filename, dic, header=None, var=None):
    """
    write dict text file.

    Args:
        filename (str): filename.
        dic (dict): dictionary to write.
        header (str, optional): header comment at the top of file.
        var (str, optional): varialbe of dict.
    """
    with open(filename, mode="w", encoding="utf-8") as f:
        if header is not None:
            print('"""' + header + '"""', file=f)
        if var is None:
            print(dic, file=f)
        else:
            print(f"{var} =", dic, file=f)


# ==================================================
def convert_str_vector(vector, cell="[0,0,0]", transform=True, A=None):
    """
    Convert 3-component vector(s) to A.(position+cell).

    Args:
        vector (str): vector, str([float]) or str([[float]]).
        cell (str, optional): cell, str([int]).
        transform (bool, optional): transform by using A ?
        A (numpy.ndarray, optional): A.

    Returns:
        - (numpy.ndarray) -- transformed position.
    """
    cell = np.array(apply(int, text_to_list(cell)))
    vector = str_to_sympy1(vector).astype(float)

    vectorT = vector + cell
    if transform:
        A = A[0:3, 0:3].T
        vectorT = vectorT @ A

    return vectorT


# ==================================================
def check_multipie():
    """
    Check if multipie is installed or not.

    Returns:
        - (bool) -- installed ?
    """
    try:
        import multipie

        return True
    except ImportError:
        return False


# ==================================================
def set_latex_setting():
    """
    Set LaTeX setting.
    """
    package = ["amsmath", "amssymb", "physics"]
    pre = "\n".join([r"\usepackage{" + i + "}" for i in package])
    tex_setting = {"text.usetex": True, "text.latex.preamble": pre}
    plt.rcParams.update(tex_setting)


# ==================================================
def create_grid(grid_n, grid_min, grid_max, A=None, endpoint=False):
    """
    Create grid.

    Args:
        grid_n (list): grid size.
        grid_min (list): grid minimum.
        grid_max (list): grid maximum.
        A (list): [a1,a2,a3].
        endpoint (bool, optional): include end points ?

    Returns:
        UniformGrid: uniform grid.

    Note:
        - grid in column-major order.
    """
    if A is None:
        A = np.eye(4)
    if endpoint:
        s = [(ma - mi) / (n - 1) for mi, ma, n in zip(grid_min, grid_max, grid_n)]
    else:
        s = [(ma - mi) / n for mi, ma, n in zip(grid_min, grid_max, grid_n)]
    grid = pv.ImageData(dimensions=grid_n, origin=grid_min, spacing=s).cast_to_unstructured_grid()
    grid.transform(A, inplace=True)

    return grid


# ==================================================
def split_filename(filename):
    """
    Split file name.

    Args:
        filename (str): filename.

    Returns:
        - (str) -- filename with absolute path.
        - (str) -- filename with relative path.
        - (str) -- base filename.
        - (str) -- extension.
        - (str) -- directory.
    """
    path = Path(filename)
    path_abs = path if path.is_absolute() else (Path.cwd() / path).resolve()
    path_rel = path_abs.relative_to(Path.cwd())
    base = str(path_rel.stem)
    ext = str(path_rel.suffix)
    folder = str(path_abs.parent)

    return str(path_abs), str(path_rel), base, ext, folder


# ==================================================
def cat_filename(base, ext=None):
    """
    Cat filename.

    Args:
        base (str): (base) filename.
        ext (str, optional): extension.

    Returns:
        - (str) -- full file name.
    """
    if ext is not None:
        base = base + ext
    path = str(Path.cwd() / Path(base))

    return path


# ==================================================
def create_style_sheet(size):
    """
    Create style sheet.

    Args:
        size (int): font size (point).

    Returns:
        - (str) -- style sheet string.
    """
    return f"""
    QTreeView::item {{
        padding: 10px 15px 10px 15px;
        border: none;
        outline: none;
        background: none;
    }}

    QTreeView::item:selected {{
        border: none;
        outline: none;
        color: black;
        background: lightyellow;
    }}
    QTreeView::item:focus {{
        border: none;
        outline: none;
        color: black;
        background: lightyellow;
    }}

    QComboBox {{
        font-size: {size}pt;
        min-width: 40px;
    }}

    QLabel {{
        font-size: {size}pt;
    }}

    QPushButton {{
        font-size: {size}pt;
    }}
    """


# ==================================================
def get_data_range(data):
    v1 = data.min()
    v2 = data.max()
    v = max(abs(v1), abs(v2))
    if v1 * v2 < 0.0:
        clim = [-v, v]
    elif v1 < 0.0:
        clim = [-v, 0.0]
    else:
        clim = [0.0, v]
    return clim
