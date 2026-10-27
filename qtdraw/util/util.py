# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2021- The QtDraw developers
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""
For versatile utility.
"""

import re
import ast
import sys
import shlex
import copy
import numpy as np
import sympy as sp
from sympy import SympifyError
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication, rationalize
import pyvista as pv


# ==================================================
def _check_shape(a, shape):
    """
    Check array shape.

    Args:
        a (ndarray): array.
        shape (tuple): shape, (), (n,), (n,m), ...

    Returns:
        - (bool) -- if a is given shape, return True otherwise False.

    Note:
        - "0" in shape means any size.
        - for shape (n,0), rows of different lengths are also accepted, e.g. faces of a polygon.
    """
    if shape is None:
        return True
    if a.ndim == len(shape) and all(s == 0 or x == s for x, s in zip(a.shape, shape)):
        return not any(isinstance(x, (list, tuple)) for x in a.flat)  # not deeper than the shape, e.g. [[[0]],[1]].
    if len(shape) == 2 and shape[1] == 0 and a.ndim == 1 and shape[0] in (0, len(a)):  # rows of different lengths.
        return all(isinstance(row, (list, tuple)) and not any(isinstance(x, (list, tuple)) for x in row) for row in a)
    return False


# ==================================================
def str_to_sympy(s, check_var=None, check_shape=None, rational=True, subs=None, **assumptions):
    """
    Convert a string to a sympy.

    Args:
        s (str): a string.
        check_var (list, optional): variables to accept, None (all).
        check_shape (tuple, optional): shape, (), (n,), (n,m), ...
        rational (bool, optional): use rational number ?
        subs (dict, optional): replace dict for local variables.
        **assumptions (dict, optional): common assumptions for all variables.

    Returns:
        - (ndarray) -- (list of) sympy.

    Notes:
        - if format error occurs, raise ValueError.
        - if s cannot be converted to a sympy, raise ValueError.
    """
    # reserved words in sympy (functions, constants, etc.).
    reserved = set(sp.__all__) | {"pi", "E", "I", "oo", "zoo"}

    # extract candidate variable names, without the exponents of numbers such as 1e-3.
    var = sorted(set(re.findall(r"[A-Za-z_]\w*", re.sub(r"(?<![\w.])(\d+\.?\d*|\.\d+)[eE][+-]?\d+", "0", s))))
    # remove reserved ones.
    var = [v for v in var if v not in reserved]

    # check var validation.
    if (check_var is not None) and not (set(var) <= set(check_var)):
        raise ValueError(f"not found variable '{var}' in '{check_var}'.")

    # set up local symbol environment.
    local_dict = {v: sp.Symbol(v, **assumptions) for v in var}
    if subs:
        local_dict.update(subs)

    # setup parser transformations.
    transformations = standard_transformations + (implicit_multiplication,)
    if rational:
        transformations += (rationalize,)

    # parse string.
    try:
        s = re.sub(r",\s*]", "]", s)
        expression = parse_expr(s, transformations=transformations, local_dict=local_dict)
    except (SympifyError, SyntaxError, TypeError):
        raise ValueError(f"invalid string '{s}'.")

    expression = np.asarray(expression, dtype=object)

    if not _check_shape(expression, check_shape):
        raise ValueError(f"invalid shape, {expression.shape}!={check_shape}.")

    if expression.ndim == 0:
        return expression.item()
    return expression


# ==================================================
def to_latex(a, style="scalar"):
    """
    convert list to latex list.

    Args:
        a (array-like): list of sympy.
        style (str, optional): style, "scalar/vector/matrix".

    Returns:
        - (ndarray or str) -- (list of) LaTeX string without "$".
    """
    a = np.array(a, dtype=object)

    if style == "scalar":
        if a.ndim == 0:
            return sp.latex(a.item())
        else:
            return np.vectorize(lambda x: sp.latex(x))(a).astype(object)

    elif style == "vector":

        def vec_latex(v):
            return r"\left[ " + r",\, ".join(sp.latex(x) for x in v) + r" \right]"

        if a.ndim == 1:
            return vec_latex(a)
        elif a.ndim > 1:
            s = a.shape
            sz, v = s[:-1], s[-1]
            return np.asarray([vec_latex(i) for i in a.reshape(-1, v)], dtype=object).reshape(sz)
        else:
            raise ValueError(f"invalid array shape, {a.shape}.")

    elif style == "matrix":

        def mat_latex(m):
            rows = [" & ".join(sp.latex(x) for x in row) for row in m]
            return r"\begin{bmatrix} " + r" \\ ".join(rows) + r" \end{bmatrix}"

        if a.ndim == 2:
            return mat_latex(a)
        elif a.ndim > 2:
            s = a.shape
            sz, v = s[:-2], s[-2:]
            return np.asarray([mat_latex(i) for i in a.reshape(-1, *v)], dtype=object).reshape(sz)
        else:
            raise ValueError(f"invalid array shape, {a.shape}.")

    raise ValueError(f"unknown style, {style}.")


MULTIPIE_INSTALL = "MultiPie is not installed. Install it with: pip install multipie"


# ==================================================
def _load_multipie():
    """
    Import the parts of MultiPie used by QtDraw, which raises the error when they cannot be loaded.
    """
    from multipie import Group
    from multipie.util.util_harmonics import harmonics_decomposition
    from multipie.util.util_response_tensor import convert_mp_alias


# ==================================================
def check_multipie():
    """
    Check if multipie is installed and can be loaded.

    Returns:
        - (bool) -- available ?

    Note:
        - without it, the functions of MultiPie are turned off.
    """
    try:
        _load_multipie()
        return True
    except Exception:
        return False


# ==================================================
def multipie_message():
    """
    Tell why MultiPie cannot be used.

    Returns:
        - (str) -- how to install MultiPie, or why the installed one cannot be loaded.
    """
    try:
        _load_multipie()
    except Exception as e:
        if isinstance(e, ModuleNotFoundError) and e.name == "multipie":
            return MULTIPIE_INSTALL
        return f"MultiPie cannot be loaded ({type(e).__name__}: {e})."
    return MULTIPIE_INSTALL


# ==================================================
def multipie_missing():
    """
    Check if MultiPie is not installed, not only that it cannot be loaded.

    Returns:
        - (bool) -- not installed ?
    """
    try:
        _load_multipie()
    except ModuleNotFoundError as e:
        return e.name == "multipie"
    except Exception:
        return False
    return False


# ==================================================
def install_multipie_command():
    """
    Command to install MultiPie with pip of this Python.

    Returns:
        - (list) -- program and arguments.
    """
    return [sys.executable, "-m", "pip", "install", "multipie"]  # no version specifier: ">" is a redirection in a shell.


# ==================================================
def command_text(command):
    """
    Command as text to run in a shell, quoted.

    Args:
        command (list): program and arguments.

    Returns:
        - (str) -- command line.
    """
    if sys.platform == "win32":  # for cmd.exe: quote the arguments with spaces or its special characters.
        return " ".join(f'"{a}"' if not a or set(a) & set(" \t&|<>^()") else a for a in command)
    return shlex.join(command)


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
class _NotFinite(ast.NodeTransformer):
    """
    Read nan and inf (as Python writes such float values) as numbers.
    """

    def visit_Name(self, node):
        if node.id in ("nan", "inf"):
            return ast.copy_location(ast.Constant(float(node.id)), node)
        return node


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
    try:
        d = ast.literal_eval(s)
    except ValueError:  # e.g. nan or inf (slower, so only when needed).
        d = ast.literal_eval(_NotFinite().visit(ast.parse(s, mode="eval")))

    return d


# ==================================================
def to_plain(obj):
    """
    Convert numpy values in nested dict, list and tuple to Python values, which can be written as text and read again.

    Args:
        obj (any): object.

    Returns:
        - (any) -- copy of the object with Python values.
    """
    if isinstance(obj, np.ndarray):
        return to_plain(obj.tolist()) if obj.dtype == object else obj.tolist()  # elements of an object array may be arrays.
    if isinstance(obj, np.generic):
        return obj.item()
    if isinstance(obj, dict):
        return {to_plain(k): to_plain(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return type(obj)(to_plain(v) for v in obj)
    return copy.deepcopy(obj)  # not shared with the given object.


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
def text_to_list(text):
    """
    Convert single text to list.

    Args:
        text (str): text to convert.

    Returns:
        - (list or str) -- converted list.

    Notes:
        - if format error occurs, return None.
    """
    if not isinstance(text, str):
        return None

    lb = text.count("[")
    rb = text.count("]")
    if lb != rb:
        return None
    elif lb == 0 and rb == 0:
        return text

    text = re.sub(r"\s*\[\s*", "[", text)
    text = re.sub(r"\s*\]\s*", "]", text)

    text = text.replace("[", "['").replace("]", "']").replace(",", "','").replace("'[", "[").replace("]'", "]")
    try:
        lst = ast.literal_eval(text)
    except (SyntaxError, ValueError):
        return None

    return lst


# ==================================================
def apply(f, lst):
    """
    Apply function to (nested) list.

    Args:
        f (function): function to apply to each element of list.
        lst (list or value): (nested) list to apply.

    Returns:
        - (list or value) -- applied list.
    """
    if isinstance(lst, list):
        return [apply(f, x) for x in lst]
    else:
        return f(lst)


# ==================================================
def distance(s1, s2, G=None, accuracy=4):
    """
    group of sites with the same distance (in increasing order).

    Args:
        s1 (ndarray): vector array.
        s2 (ndarray): vector array.
        G (ndarray, optional): metric matrix (None = unit matrix).
        accuracy (int, optional): accuracy of digit.

    Returns:
        dict : i, j are indices of positions (i<=j only for s1=s2), { distance(float): [(i(int),j(int))] }.
    """
    if G is None:
        G = np.eye(s1.shape[0])
    diff = id(s1) != id(s2)
    s1 = s1.astype(float)
    if diff:
        s2 = s2.astype(float)
    else:
        s2 = s1

    d = {0: []}
    for i, v1 in enumerate(s1):
        for j, v2 in enumerate(s2):
            if diff or i <= j:
                r = v1 - v2
                dist = round(float(np.sqrt(r @ G @ r)), accuracy)
                d[dist] = d.get(dist, []) + [(i, j)]
    d = {i: j for i, j in sorted(d.items())}

    return d


# ==================================================
def igrid(N, offset=None):
    """
    create integer grid points.

    Args:
        N (list): number of points in each direction.
        offset (tuple, optional): offset in each direction. 0 is used for None.

    Returns:
        ndarray: grid points.

    Notes:
        - grid point: increase of indices from left to right.
        - x[i] = offset + i.
    """
    d = len(N)
    if offset is None:
        offset = [0] * d
    g = [np.arange(offset[i], offset[i] + N[i]) for i in range(d)]
    g = np.meshgrid(*g[::-1], indexing="ij")
    grid = np.stack([i.ravel() for i in g][::-1], axis=1)

    return grid
