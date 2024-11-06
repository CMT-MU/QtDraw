"""
Versatile utility.

This module contains the utilities mainly for string and list.
"""

import numpy as np
from fractions import Fraction
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication, rationalize
from sympy import SympifyError, Symbol, Basic


# ==================================================
def str_to_list(s):
    """
    Convert a string to a list of strings.

    Args:
        s (str): a string with irregular-shaped list format.

    Returns:
        - (list) -- a list of strings.

    Note:
        - in case of no bracket, return as it is.
        - raise ValueError for invalid brackets.
    """
    if s.count("[") != s.count("]"):
        raise ValueError(f"invalid blackets in '{s}'.")

    if s.count("[") == 0:
        return s

    nested_list = []
    stack = []
    current_word = ""

    for char in s:
        if char == "[":
            if current_word.strip():  # remove space, and append it for non-null string.
                stack[-1].append(current_word.strip())
                current_word = ""
            stack.append([])
        elif char == "]":
            if current_word.strip():  # remove space, and append it for non-null string.
                stack[-1].append(current_word.strip())
                current_word = ""
            if stack:
                popped = stack.pop()
                if stack:
                    stack[-1].append(popped)
                else:
                    nested_list.append(popped)
        elif char == ",":
            if current_word.strip():  # remove space, and append it for non-null string.
                stack[-1].append(current_word.strip())
                current_word = ""
        else:
            current_word += char

    if current_word.strip():  # parse last word.
        if stack:
            stack[-1].append(current_word.strip())
        else:
            nested_list.append(current_word.strip())

    return nested_list[0]


# ==================================================
def is_regular_list(lst):
    """
    Is regular-shaped list ?

    Args:
        lst (list): a list.

    Returns:
        - (bool) -- is regular-shaped list ?
    """
    try:
        np.array(lst)
        return True
    except ValueError:
        return False


# ==================================================
def apply_to_list(func, lst):
    """
    Apply a function to each element of a list.

    Args:
        func (function): a function.
        lst (list): a list.

    Returns:
        - (list) -- an applied list.

    Note:
        - applicable to an irregular-shaped list.
    """
    if not isinstance(lst, list):
        return func(lst)

    result = []
    for sub_lst in lst:
        if isinstance(sub_lst, list):
            # apply function to sub list recursively.
            result.append(apply_to_list(func, sub_lst))
        else:
            # apply function to non list.
            result.append(func(sub_lst))
    return result


# ==================================================
def apply_to_numpy(func, lst):
    """
    Apply a function to each element of ndarray.

    Args:
        func (function): a function.
        lst (ndarray): a numpy array.

    Returns:
        - (ndarray) -- an applied array.

    Note:
        - applicable only to a regular-shaped ndarray.
    """
    return np.vectorize(func)(lst)


# ==================================================
def to_fraction(x, max_denominator=1000000):
    """
    Convert a float number to a fractional one.

    Args:
        x (float): a float number.
        max_denominator (int, optional): max. of denominator.

    Returns:
        - (str) -- a fractional string.
    """
    return str(Fraction(x).limit_denominator(max_denominator))


# ==================================================
def get_variable(sp_ex):
    """
    Get variables used in a sympy expression.

    Args:
        sp_ex (sympy): a sympy expression (except for Matrix).

    Returns:
        - (list) -- variable strings (sorted).
    """
    var = set()

    if isinstance(sp_ex, Basic):
        var.update(set(map(str, sp_ex.atoms(Symbol))))

    return sorted(var)


# ==================================================
def str_to_sympy(s, check_var=None, rational=True, subs=None):
    """
    Convert a string to a sympy.

    Args:
        s (str): a string.
        local (dict, optional): variables to replace.
        check_var (list, optional): variables to accept.
        rational (bool, optional): use rational number ?
        subs (dict, optional): replace dict for local variables.

    Returns:
        - (sympy) -- a sympy.

    Notes:
        - if format error occurs, return None.
        - if s cannot be converted to a sympy, return None.
    """
    if check_var is None:
        check_var = []

    check_var = set(check_var)

    transformations = standard_transformations + (implicit_multiplication,)
    if rational:
        transformations += (rationalize,)

    try:
        expression = parse_expr(s, transformations=transformations, local_dict=subs)
    except (SympifyError, SyntaxError, TypeError):
        return None
    var = set(get_variable(expression))
    if len(check_var) != 0 and not (var <= check_var):
        return None

    return expression


# ==================================================
def str_to_numpy(s, digit=None, check_var=None, check_shape=None):
    """
    Convert a string (list) to a numpy array.

    Args:
        s (str): a string (list).
        digit (int, optional): accuracy digit (only for numerical vector).
        check_var (list, optional): variables to accept.
        check_shape (tuple, optional): shape to check.

    Returns:
        - (ndarray): a numpy array.

    Note:
        - when parse error occurrs, return None.
        - in check_shape, '0' means no check.
    """
    try:
        sl = str_to_list(s)
    except:
        return None
    if sl is None:
        return None
    sl = np.array(sl)
    if check_shape is not None:
        if sl.ndim != len(check_shape):
            return None
        shape = sl.shape
        for i in range(len(shape)):
            if check_shape[i] > 0 and shape[i] != check_shape[i]:
                return None

    try:
        is_ex = digit == None
        sl = apply_to_numpy(lambda x: str_to_sympy(x, check_var, rational=is_ex), sl)
        if np.any(sl == None):
            return None
        if not is_ex:
            sl = apply_to_numpy(float, sl).round(digit)
    except:
        return None

    return sl


# ==================================================
def affine_trans(v, s=None, A=None, digit=None, check_var=None):
    """
    Affine transformation, A.v + s.

    Args:
        v (str): site/vector or a list of site/vector.
        s (str, optional): shift vector or a list of shift vector.
        A (str, optional): rotaional matrix (3x3), [a1, a2, a3].
        digit (int, optional): accuracy digit (only for numerical vector).
        check_var (list, optional): variables to accept.

    Returns:
        - (ndarray) -- transformed vector.
    """
    v = str_to_numpy(v, digit, check_var)
    if v is None:
        return None
    if v.ndim != 1 and v.ndim != 2:
        return None
    if v.ndim == 1 and v.shape[0] != 3:
        return None
    if v.ndim == 2 and v.shape[1] != 3:
        return None

    if A is not None:
        A = str_to_numpy(A, digit, check_var, (3, 3))
        if A is None:
            return None

        v = v @ A.T

    if s is not None:
        s = str_to_numpy(s, digit, check_var)
        if s is None:
            return None
        if s.ndim != 1 and s.ndim != 2:
            return None
        if s.ndim == 1 and s.shape[0] != 3:
            return None
        if s.ndim == 2 and s.shape[1] != 3:
            return None

        if v.ndim == s.ndim:
            v += s
        else:
            if v.ndim == 1:
                v = np.tile(v, (s.shape[0], 1)) + s
            else:
                v = v + np.tile(s, (v.shape[0], 1))

    return v


# ==================================================
def str_to_sympy1(s, check_var=None, rational=True, subs=None):
    """
    Convert a string to a sympy (new version).

    Args:
        s (str): a string.
        check_var (list, optional): variables to accept.
        rational (bool, optional): use rational number ?
        subs (dict, optional): replace dict for local variables.

    Returns:
        - (ndarray) -- (list of) sympy.

    Notes:
        - if format error occurs, raise ValueError.
        - if s cannot be converted to a sympy, raise ValueError.
    """
    if check_var is None:
        check_var = []

    check_var = set(check_var)

    transformations = standard_transformations + (implicit_multiplication,)
    if rational:
        transformations += (rationalize,)

    try:
        expression = parse_expr(s, transformations=transformations, local_dict=subs)
    except (SympifyError, SyntaxError, TypeError):
        raise ValueError(f"invalid string '{s}'.")
    var = set(get_variable(expression))
    if len(check_var) != 0 and not (var <= check_var):
        raise ValueError(f"invalid variable in '{s}'.")

    expression = np.asarray(expression)

    return expression
