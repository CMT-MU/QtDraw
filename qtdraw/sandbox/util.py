"""
For versatile utility.
"""

import re
import numpy as np
import sympy as sp
import matplotlib.pyplot as plt
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
    """
    if shape is None:
        return True
    return a.ndim == len(shape) and all(s == 0 or x == s for x, s in zip(a.shape, shape))


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

    # extract candidate variable names.
    var = sorted(set(re.findall(r"[A-Za-z_]\w*", s)))
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
    a = np.array(a)

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
            return np.apply_along_axis(lambda x: vec_latex(x), 1, a).astype(object)
        else:
            raise ValueError(f"invalid array shape, {a.shape}.")

    elif style == "matrix":

        def mat_latex(m):
            rows = [" & ".join(sp.latex(x) for x in row) for row in m]
            return r"\begin{bmatrix} " + r" \\ ".join(rows) + r" \end{bmatrix}"

        if a.ndim == 2:
            return mat_latex(a)
        elif a.ndim > 2:
            return np.array([mat_latex(x) for x in a.reshape(-1, *a.shape[-2:])]).reshape(*a.shape[:-2]).astype(object)
        else:
            raise ValueError(f"invalid array shape, {a.shape}.")

    raise ValueError(f"unknown style, {style}.")


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
