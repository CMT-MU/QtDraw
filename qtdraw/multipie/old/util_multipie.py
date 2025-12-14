"""
Utility.

This module contains utilities for multipie plugin.
"""

import sympy as sp
import numpy as np

from qtdraw.util.util import str_to_list, str_to_sympy
from qtdraw.widget.validator import convert_to_bond


# ==================================================
def check_get_site(txt):
    """
    Check and get site.

    Args:
        txt (str): site.

    Returns:
        - (ndarray) -- site or None if invalid.
    """
    try:
        return str_to_sympy(txt, check_shape=(3,))
    except ValueError:
        return None


# ==================================================
def check_get_bond(txt):
    """
    Check and get bond.

    Args:
        txt (str): bond.

    Returns:
        - (ndarray) -- bond ([v,c]) or None if invalid.
    """
    v, c = convert_to_bond(txt)
    if v is None:
        return None
    else:
        return np.concatenate([v, c])


# ==================================================
def check_get_site_bond(txt, ret_site=False):
    """
    Check and get site (bond center) from site_bond.

    Args:
        txt (str): site_bond.
        ret_site (bool, optional): return site ?

    Returns:
        - (ndarray) -- site, bond ([v,c]) or bond center, or None if invalid.
    """
    if "@" in txt or ";" in txt or ":" in txt:  # bond.
        b = check_get_bond(txt)
        if b is None:
            return None
        if ret_site:
            return b[3:]
        else:
            return b
    else:
        return check_get_site(txt)


# ==================================================
def create_samb_object(z_samb, site, c_samb, z_head, irrep, pg, v, t_odd):
    """
    Create SAMB object.

    Args:
        z_samb (dict): combined SAMB.
        site (ndarray): site.
        c_samb (dict): cluster SAMB.
        z_head (str): multipole type.
        irrep (int): irrep. index.
        pg (PointGroup): point group.
        v (ndarray): vector variable.
        t_odd (bool): magnetic bond ?

    Returns:
        - (ndarray) -- (xyz)-polynomial at each cluster site.
    """
    obj = np.full(len(site), sp.S(0))
    for i in z_samb[z_head][irrep][1]:
        coeff, tag_h, tag_c = i
        harm = pg.harmonics[tag_h].expression(v=v)
        cluster = c_samb[tag_c]
        obj += coeff * harm * cluster

    if t_odd:
        obj *= -sp.I

    return obj


# ==================================================
def check_linear_combination(z_samb, form, head):
    """
    Check form of linear combination.

    Args:
        z_samb (dict): combined SAMB.
        form (str): expression of linear combination.
        head (str): multipole type.

    Returns:
        - (str) -- expression of linear combination (lower case).
        - (set) -- used variables.
        - (bool) -- magnetic bond ?
    """
    irrep_num = {i: len(z_samb[i]) for i in ["Q", "G", "T", "M"]}
    var_e = set([f"q{i+1:02d}" for i in range(irrep_num["Q"])] + [f"g{i+1:02d}" for i in range(irrep_num["G"])])
    var_m = set([f"t{i+1:02d}" for i in range(irrep_num["T"])] + [f"m{i+1:02d}" for i in range(irrep_num["M"])])

    form = form.lower()
    form_variable = str_to_sympy(form).free_symbols

    t_odd = "Q"
    if form_variable.issubset(var_m):
        t_odd = "T"
    elif not form_variable.issubset(var_e):
        return None, None, None
    t_odd = head.replace("M", "T").replace("G", "Q") != t_odd

    return form, form_variable, t_odd


# ==================================================
def combined_format(tag_list):
    """
    Create formatted combined SAMB.

    Args:
        tag_list (tuple): (Z,X,Y) tag.

    Returns:
        - (str) -- formatted combined SAMB.
    """
    z_tag, x_tag, y_tag = tag_list
    t1 = (",".join(str(x_tag).split(",")[:-1]) + ")").replace("h", "a")
    t2 = ",".join(str(y_tag).split(",")[:-1]) + ")"
    tag = f"{z_tag} = {t1} x {t2}"

    return tag


# ==================================================
def parse_modulation_list(lst):
    """
    Parse modulation list.

    Args:
        lst (str): modulation list in str, [[basis,coeff,k,cos/sin]]

    Returns:
        - (list) -- modulation list.
    """
    try:
        lst = str_to_list(lst)
    except ValueError:
        return [[]]

    mod_data = []
    for i, row in enumerate(lst):
        basis, weight, k, cs = row
        mod_data.append([str(i), basis, weight, "[" + ",".join(k) + "]", cs])

    return mod_data
