"""
Validator type.

- type: option.
    - int: (min, max)
    - float: (min, max, digit)
    - list_int: (shape, var)
    - list_float: (shape, var ,digit)
    - math: (shape, var)
    - site: (use var?)
    - bond: (use var?)
    - site_bond: (use var?)
    - vector_site_bond: (use var?)
    - orbital_site_bond: (use var?)
"""

import cmath
import math

import numpy as np

from qtdraw.util.util import str_to_sympy, to_latex

DISPLAY_DIGIT = 5
INT_LIMIT = 2**63  # integers must fit in 64 bits.


# ==================================================
def check_symbol(expr):
    """
    Check symbol.

    Args:
        expr (sympy or ndarray)

    Returns:
        - (bool) -- if expr contains symbol, return True otherwise False.
    """
    if isinstance(expr, (list, tuple, np.ndarray)):  # also rows of different lengths.
        return any(check_symbol(e) for e in _flat(expr))

    return bool(expr.free_symbols)


# ==================================================
def _flat(s):
    """
    Elements of a (nested, possibly ragged) list or array.

    :meta private:
    """
    if isinstance(s, (list, tuple, np.ndarray)):
        for x in s:
            yield from _flat(x)
    else:
        yield s


# ==================================================
def _format(s, fmt):
    """
    Text of a (nested, possibly ragged) list or array, with each element formatted by fmt.

    :meta private:
    """
    if isinstance(s, (list, tuple, np.ndarray)):
        return "[" + ",".join(_format(x, fmt) for x in s) + "]"
    return fmt(s)


# ==================================================
def _finite_floats(s):
    """
    Floats of numbers, None if one is not a finite real number (e.g. nan, oo or I).

    :meta private:
    """
    try:
        values = [float(x) for x in _flat(s)]
    except (TypeError, ValueError, OverflowError):
        return None
    return values if all(math.isfinite(x) for x in values) else None


# ==================================================
def _finite_complex(s):
    """
    Complex numbers of numbers, None if one is not a finite number (e.g. nan or zoo).

    :meta private:
    """
    try:
        values = [complex(x) for x in _flat(s)]
    except (TypeError, ValueError, OverflowError):
        return None
    return values if all(cmath.isfinite(x) for x in values) else None


# ==================================================
def _integers(s):
    """
    Integers of numbers, None if one is not an integer fitting in 64 bits.

    :meta private:
    """
    values = []
    for x in _flat(s):
        if not getattr(x, "is_integer", False):
            return None
        x = int(x)
        if not -INT_LIMIT <= x < INT_LIMIT:
            return None
        values.append(x)
    return values


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
    if not -INT_LIMIT <= s < INT_LIMIT:
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
        text (str): float string.
        opt (dict, optional): option, "min/max/digit". (default: "*","*",5)

    Returns:
        - (str) -- formatted string if it is valid, otherwise None.
    """
    try:
        s = float(text)
    except ValueError:
        return None
    if not math.isfinite(s):  # nan, inf or too large.
        return None

    r_min = opt.get("min", "*")
    r_max = opt.get("max", "*")
    digit = opt.get("digit", DISPLAY_DIGIT)

    if (r_min != "*" and s < float(r_min)) or (r_max != "*" and s > float(r_max)):
        return None

    return f"{np.round(s, digit):.{digit}f}"


# ==================================================
def validator_list_float(text, **opt):
    """
    Validator for list float.

    Args:
        text (str): string with list.
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
    if np.size(s) == 0:  # an empty list.
        return None
    if not check_symbol(s) and _finite_floats(s) is None:
        return None

    if digit is not None and not check_symbol(s):
        return _format(s, lambda x: f"{float(x):.{digit}f}")

    if isinstance(s, np.ndarray):
        return str(s.tolist()).replace(" ", "")
    else:
        return str(s)


# ==================================================
def validator_list_int(text, **opt):
    """
    Validator for list int.

    Args:
        text (str): string with list.
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
    if np.size(s) == 0:  # an empty list.
        return None

    if not check_symbol(s):
        if _integers(s) is None:
            return None
        return _format(s, lambda x: f"{int(x)}")

    if isinstance(s, np.ndarray):
        return str(s.tolist()).replace(" ", "")
    else:
        return str(s)


# ==================================================
def validator_math(text, **opt):
    """
    Validator for math to LaTeX.

    Args:
        text (str): sympy string.
        opt (dict, optional): option, "shape/var/real". (default: None,None,False)
            real: a constant must be a real number (otherwise also complex).

    Returns:
        - (str) -- LaTeX string if it is valid, otherwise None.
    """
    shape = opt.get("shape", None)
    var = opt.get("var", None)

    try:
        s = str_to_sympy(text, check_var=var, check_shape=shape)
    except Exception:
        return None
    if np.size(s) == 0:  # an empty list.
        return None
    if not check_symbol(s) and (_finite_floats(s) if opt.get("real", False) else _finite_complex(s)) is None:
        return None  # a constant must be a finite (real) number.

    if isinstance(s, np.ndarray):
        s = str(to_latex(s).tolist()).replace("'", "").replace("\\\\", "\\")
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
    return validator_list_float(s, shape=(3,), var=var)


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
    v = validator_list_float(v, var=["x", "y", "z", "r"], shape=())
    sb = validator_site_bond(sb, use_var)

    return None if v is None or sb is None else v + "#" + sb


# ==================================================
def validator_hint(vtype, option=None):
    """
    Explanation of accepted input for validator (used as tooltip).

    Args:
        vtype (str): validator type.
        option (dict, optional): validator option.

    Returns:
        - (str) -- explanation.
    """
    if option is None:
        option = {}

    def value_range():
        r_min, r_max = option.get("min", "*"), option.get("max", "*")
        if r_min == "*" and r_max == "*":
            return ""
        if r_max == "*":
            return f" (≥ {r_min})"
        if r_min == "*":
            return f" (≤ {r_max})"
        return f" ({r_min} to {r_max})"

    def shape_text(kind):
        shape = option.get("shape", None)
        if shape is None:
            return f"{kind} or list of {kind}s"
        if len(shape) == 0:
            return kind
        if len(shape) == 1:
            if shape[0] == 0:  # 0 means any length.
                return f"list of {kind}s of any length, e.g. [1] or [1,2]"
            example = "[" + ",".join(["0"] * shape[0]) + "]"
            return f"list of {shape[0]} {kind}s, e.g. {example}"
        dims = ", ".join("n" if n == 0 else str(n) for n in shape)
        text = f"nested list of {kind}s with shape ({dims})" + (", n is any length" if 0 in shape else "")
        if len(shape) == 2 and shape[1] == 0:
            text += ", rows may have different lengths"
        return text

    def variables(var):
        var = [v for v in (var or []) if v != ""]
        return f" Variables: {', '.join(var)}." if var else ""

    expression = " Expressions such as 1/2 or sqrt(3)/2 are accepted."
    site = "[x,y,z], e.g. [1/2,0,0]"
    bond = "[tail];[head], [vector]@[center] or [start]:[vector]"
    xyz = " x, y, z can be used." if option.get("use_var", False) else ""

    if vtype == "int":
        return f"Integer{value_range()}."
    if vtype == "float":
        return f"Number{value_range()}."
    if vtype == "list_float":
        return f"Number: {shape_text('number')}.{expression}{variables(option.get('var'))}"
    if vtype == "list_int":
        return f"Integer: {shape_text('integer')}.{variables(option.get('var'))}"
    if vtype == "math":
        return f"Math expression: {shape_text('expression')}.{variables(option.get('var'))}"
    if vtype == "site":
        return f"Site {site}.{expression}{xyz}"
    if vtype == "bond":
        return f"Bond {bond}.{expression}{xyz}"
    if vtype == "site_bond":
        return f"Site {site}, or bond {bond}.{xyz}"
    if vtype == "vector_site_bond":
        return f"[vector]#[site or bond], e.g. [0,0,1]#[0,0,0]. Bond is {bond}.{xyz}"
    if vtype == "orbital_site_bond":
        return f"[orbital]#[site or bond], e.g. x*y#[0,0,0]. Orbital uses x, y, z, r. Bond is {bond}.{xyz}"
    return ""
