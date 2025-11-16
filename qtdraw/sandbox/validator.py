"""
Validator type.

- type: option.
    - int: (min, max)
    - float: (min, max, digit)
    - sympy_float: (digit, shape, var)
    - sympy_int: (shape, var)
    - sympy_latex: (shape, var)
    - site: (use var?)
    - bond: (use var?)
    - site_bond: (use var?)
    - vector_site_bond: (use var?)
    - orbital_site_bond: (use var?)
"""

import numpy as np
from qtdraw.sandbox.util import str_to_sympy, to_latex

DISPLAY_DIGIT = 5


# ==================================================
def check_symbol(expr):
    """
    Check symbol.

    Args:
        expr (sympy or ndarray)

    Returns:
        - (bool) -- if expr contains symbol, return True otherwise False.
    """
    if isinstance(expr, np.ndarray):
        return any(check_symbol(e) for e in expr.flat)

    return bool(expr.free_symbols)


# ==================================================
def convert_to_bond(bond, use_var=False):
    """
    Convert to bond from str.

    Args:
        bond (str): bond.
        use_var (bool, optional): use [x,y,z] for site/bond ?

    Returns:
        - (ndarray) -- bond vector.
        - (ndarray) -- bond center.

    Note:
        - bond string is "[tail];[head]/[vector]@[center]/[start]:[vector]".
    """
    var = ["x", "y", "z"] if use_var else [""]
    try:
        if ";" in bond:
            t, h = bond.split(";")
            t = str_to_sympy(t, check_var=var, check_shape=(3,))
            h = str_to_sympy(h, check_var=var, check_shape=(3,))
            v = h - t
            c = (t + h) / 2
        elif "@" in bond:
            v, c = bond.split("@")
            v = str_to_sympy(v, check_var=var, check_shape=(3,))
            c = str_to_sympy(c, check_var=var, check_shape=(3,))
        elif ":" in bond:
            s, v = bond.split(":")
            s = str_to_sympy(s, check_var=var, check_shape=(3,))
            v = str_to_sympy(v, check_var=var, check_shape=(3,))
            c = s + v / 2
        else:
            raise Exception(f"invalid separator in {bond}.")
        return v, c
    except Exception:
        return None, None


# ==================================================
def validator_int(text, **opt):
    """
    Validator for int.

    Args:
        text (str): int string.
        opt (dict, optional): option, "min/max". (default: "*","*")

    Returns:
        - (str) -- formatted string if it is valid, otherwise None.
    """
    try:
        s = int(text)
    except ValueError:
        return None

    r_min = opt.get("min", "*")
    r_max = opt.get("max", "*")

    if (r_min != "*" and s < int(r_min)) or (r_max != "*" and s > int(r_max)):
        return None

    return str(s)


# ==================================================
def validator_float(text, **opt):
    """
    Validator for float.

    Args:
        text (str): int string.
        opt (dict, optional): option, "min/max/digit". (default: "*","*",5)

    Returns:
        - (str) -- formatted string if it is valid, otherwise None.
    """
    try:
        s = float(text)
    except ValueError:
        return None

    r_min = opt.get("min", "*")
    r_max = opt.get("max", "*")
    digit = opt.get("digit", DISPLAY_DIGIT)

    if (r_min != "*" and s < float(r_min)) or (r_max != "*" and s > float(r_max)):
        return None

    return f"{np.round(s, digit):.{digit}f}"


# ==================================================
def validator_sympy_float(text, **opt):
    """
    Validator for sympy float.

    Args:
        text (str): sympy string.
        opt (dict, optional): option, "digit/shape/var". (default: 5,None,[""])
            e.g., 15, (), (n,), (n,m), ..., ["x", "y", ...].

    Returns:
        - (str) -- formatted string if it is valid, otherwise None.
    """
    digit = opt.get("digit", DISPLAY_DIGIT)
    shape = opt.get("shape", None)
    var = opt.get("var", [""])

    try:
        s = str_to_sympy(text, check_var=var, check_shape=shape)
    except Exception:
        return None

    if digit is not None and not check_symbol(s):
        if isinstance(s, np.ndarray):
            s = np.vectorize(lambda x: f"{float(x):.{digit}f}")(s)
            return str(s.tolist()).replace("'", "").replace(" ", "")
        else:
            return f"{float(s):.{digit}f}"

    if isinstance(s, np.ndarray):
        return str(s.tolist()).replace(" ", "")
    else:
        return str(s)


# ==================================================
def validator_sympy_int(text, **opt):
    """
    Validator for sympy int.

    Args:
        text (str): sympy int string (w/o variable).
        opt (dict, optional): option, "shape/var". (default: None,[""])
            e.g., (), (n,), (n,m), ..., ["x", "y", ...].

    Returns:
        - (str) -- formatted string if it is valid, otherwise None.
    """
    shape = opt.get("shape", None)
    var = opt.get("var", [""])

    try:
        s = str_to_sympy(text, check_var=var, check_shape=shape)
    except Exception:
        return None

    if not check_symbol(s):
        try:
            if isinstance(s, np.ndarray):
                s = np.vectorize(lambda x: f"{int(x)}")(s)
                return str(s.tolist()).replace("'", "").replace(" ", "")
            else:
                return f"{int(s)}"
        except Exception:
            return None

    if isinstance(s, np.ndarray):
        return str(s.tolist()).replace(" ", "")
    else:
        return str(s)


# ==================================================
def validator_sympy_latex(text, **opt):
    """
    Validator for sympy.

    Args:
        text (str): sympy string.
        opt (dict, optional): option, "shape/var". (default: None,None)

    Returns:
        - (str) -- LaTeX string if it is valid, otherwise None.
    """
    shape = opt.get("shape", None)
    var = opt.get("var", None)

    try:
        s = str_to_sympy(text, check_var=var, check_shape=shape)
    except Exception:
        return None

    if isinstance(s, np.ndarray):
        s = str(to_latex(s)).replace("'", "").replace(" ", "")
    else:
        s = to_latex(s)

    return s


# ==================================================
def validator_site(s, use_var=False):
    """
    Validator for site.

    Args:
        s (str): site string, [x,y,z].
        use_var (bool, optional): use [x,y,z] for site ?

    Returns:
        - (str) -- input s if it is valid, otherwise None.
    """
    var = ["x", "y", "z"] if use_var else [""]
    return validator_sympy_float(s, shape=(3,), var=var)


# ==================================================
def validator_bond(s, use_var=False):
    """
    Validator for bond.

    Args:
        s (str): bond string.
        use_var (bool, optional): use [x,y,z] for bond ?

    Returns:
        - (str) -- input s if it is valid, otherwise None.

    Note:
        - bond sytles, start:vector, tail;head, vector@center, are accepted.
    """

    def fmt(a):
        return str([f"{i:.{DISPLAY_DIGIT}f}" for i in a]).replace("'", "").replace(" ", "")

    v, c = convert_to_bond(s, use_var)
    return None if v is None else f"{fmt(v)}@{fmt(c)}"


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
    if "#" not in s:
        return None

    v, sb = s.split("#", 1)
    v = validator_site(v, use_var)
    sb = validator_site_bond(sb, use_var)

    return None if v is None or sb is None else v + "#" + sb


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
    if "#" not in s:
        return None

    v, sb = s.split("#", 1)
    v = validator_sympy_float(v, var=["x", "y", "z", "r"], shape=())
    sb = validator_site_bond(sb, use_var)

    return None if v is None or sb is None else v + "#" + sb
