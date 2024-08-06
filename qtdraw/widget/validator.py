"""
Validator type.

- type: option ["*": no limit, digit only for no variable list=None(no check), [""](no variable)]
    - int: (min, max)
    - float: (min, max, digit)
    - sympy_float: (digit)
    - sympy: (variable list)
    - ilist: (shape)
    - list: (shape, variable list, digit)
    - site: (use variable?)
    - bond: (use variable?)
    - site_bond: (use variable?)
    - vector_site_bond: (use variable?)
    - orbital_site_bond: (use variable?)
"""

import numpy as np
import sympy as sp
from qtdraw.util.util_str import str_to_numpy, apply_to_numpy


# ==================================================
def validator_int(text, opt):
    """
    Validator for int.

    Args:
        text (str): int string.
        opt (tuple, optional): option, (min, max).

    Returns:
        - (str) -- formatted string if it is valid, otherwise None.
    """
    r_min, r_max = opt

    # type conversion.
    try:
        s = int(text)
    except:
        return None

    # range check.
    if r_min != "*" and s < int(r_min):
        return None
    if r_max != "*" and s > int(r_max):
        return None

    return str(s)


# ==================================================
def validator_float(text, opt):
    """
    Validator for float.

    Args:
        text (str): int string.
        opt (tuple, optional): option, (min, max, digit).

    Returns:
        - (str) -- formatted string if it is valid, otherwise None.
    """
    r_min, r_max, digit = opt

    # type conversion.
    try:
        s = float(text)
    except:
        return None

    # range check.
    if r_min != "*" and s < float(r_min):
        return None
    if r_max != "*" and s > float(r_max):
        return None
    s = np.round(s, digit)
    s = format(s, f".0{digit}f")

    return s


# ==================================================
def validator_sympy_float(text, opt):
    """
    Validator for sympy.

    Args:
        text (str): sympy string.
        opt (int, optional): option, digit.

    Returns:
        - (str) -- formatted string if it is valid, otherwise None.
    """
    digit = opt

    # convert to sympy, (1x1).
    try:
        s = str_to_numpy(text, digit, None, ())
    except:
        return None
    if s is None:
        return None
    s = s.tolist()
    if digit is not None:
        s = format(s, f".0{digit}f")
    else:
        s = str(s)

    return s


# ==================================================
def validator_sympy(text, opt):
    """
    Validator for sympy.

    Args:
        text (str): sympy string.
        opt (list, optional): option, var.

    Returns:
        - (str) -- LaTeX string if it is valid, otherwise None.
    """
    var = opt

    # convert to sympy, (1x1).
    try:
        s = str_to_numpy(text, None, var, ())
    except:
        return None
    if s is None:
        return None
    s = s.tolist()
    s = sp.latex(s)

    return s


# ==================================================
def validator_ilist(s, opt):
    """
    Validator for int list.

    Args:
        s (str): int list string.
        opt (tuple, optional): option, shape, (), (n,), (n,m), ...

    Returns:
        - (str) -- formatted string if it is valid, otherwise None.
    """
    shape = opt

    # convert to sympy with shape and no varialbes.
    try:
        s = str_to_numpy(s, check_var=[""], check_shape=shape)
    except:
        return None
    if s is None:
        return None

    # type conversion.
    try:
        s = s.astype(int)
    except:
        return None

    s = str(s.tolist())

    return s


# ==================================================
def validator_list(s, opt):
    """
    Validator for sympy list.

    Args:
        s (str): sympy list string.
        opt (tuple, optional): option, (shape, var, digit).

    Returns:
        - (str) -- formatted string if it is valid, otherwise None.
    """
    shape, var, digit = opt

    # convert to sympy with shape and no varialbes.
    try:
        s = str_to_numpy(s, digit, var, check_shape=shape)
    except:
        return None
    if s is None:
        return None
    if digit is not None and var is not None and len("".join(var)) == 0:
        s = apply_to_numpy(lambda x: format(x, f".0{digit}f"), s)

    s = str(s.tolist()).replace("'", "")

    return s


# ==================================================
def validator_site(s, use_var=False):
    """
    Validator for site.

    Args:
        s (str): site string, [x,y,z].
        use_var (bool, optional): use [x,y,z] for site/bond ?

    Returns:
        - (str) -- input s if it is valid, otherwise None.
    """
    if use_var:
        var = ["x", "y", "z"]
    else:
        var = [""]
    try:
        status = str_to_numpy(s, None, var, (3,))
    except:
        return None
    if status is not None:
        return s
    else:
        return None


# ==================================================
def validator_bond(s, use_var=False):
    """
    Validator for bond.

    Args:
        s (str): bond string.
        use_var (bool, optional): use [x,y,z] for site/bond ?

    Returns:
        - (str) -- input s if it is valid, otherwise None.

    Note:
        - bond sytles, start:vector, tail;head, vector@center, are accepted.
    """
    if s.count(":"):
        s2 = s.split(":")
    elif s.count(";"):
        s2 = s.split(";")
    elif s.count("@"):
        s2 = s.split("@")
    else:
        return None

    if len(s2) != 2:
        return None
    sa, sb = s2
    sa = validator_site(sa, use_var)
    if sa is None:
        return None
    sb = validator_site(sb, use_var)
    if sb is None:
        return None

    return s


# ==================================================
def validator_site_bond(s, use_var=False):
    """
    Validator for site or bond.

    Args:
        s (str): site or bond string.
        use_var (bool, optional): use [x,y,z] for site/bond ?

    Returns:
        - (str) -- input s if it is valid, otherwise None.

    Note:
        - bond sytles, start:vector, tail;head, vector@center, are accepted.
    """
    if (":" in s) or (";" in s) or ("@" in s):
        return validator_bond(s, use_var)
    else:
        return validator_site(s, use_var)


# ==================================================
def validator_vector_site_bond(s, use_var=False):
    """
    Validator for vector on site or bond.

    Args:
        s (str): vector on site or bond string.
        use_var (bool, optional): use [x,y,z] for site/bond ?

    Returns:
        - (str) -- input s if it is valid, otherwise None.

    Note:
        - bond sytles, start:vector, tail;head, vector@center, are accepted.
    """
    if s.count("#"):
        s2 = s.split("#")
        if len(s2) != 2:
            return None
        v, sb = s2
        v = validator_site(v, use_var)
        if v is None:
            return None
        sb = validator_site_bond(sb, use_var)
        if sb is None:
            return None
    else:
        return None

    return s


# ==================================================
def validator_orbital_site_bond(s, use_var=False):
    """
    Validator for orbital on site or bond.

    Args:
        s (str): orbital on site or bond string.
        use_var (bool, optional): use [x,y,z] for site/bond ?

    Returns:
        - (str) -- input s if it is valid, otherwise None.

    Note:
        - orbital can contain x, y, z, r.
        - bond sytles, start:vector, tail;head, vector@center, are accepted.
    """
    if s.count("#"):
        s2 = s.split("#")
        if len(s2) != 2:
            return None
        o, sb = s2
        o = str_to_numpy(o, None, ["x", "y", "z", "r"], ())
        if o is None:
            return None
        sb = validator_site_bond(sb, use_var)
        if sb is None:
            return None
    else:
        return None

    return s
