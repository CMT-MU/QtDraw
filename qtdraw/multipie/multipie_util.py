import numpy as np
import sympy as sp


# ==================================================
def create_samb_object(group, samb_tp, samb, wp, site, vec=False):
    sgn = {"Q": 1, "G": 1, "T": -1, "M": -1}
    tp = "bond" if "@" in wp else "site"
    c_samb = group.cluster_samb(wp, tp)

    obj = np.full(len(site), sp.S(0))
    for coeff, a_key, a_comp, c_key, c_comp in samb:
        s = 1 if sgn[samb_tp] * sgn[a_key[0]] == 1 else -sp.I
        a_key = (a_key[0].replace("T", "Q").replace("M", "G"), *a_key[1:])
        a_val = group.harmonics[a_key][0][a_comp]
        c_val = c_samb[c_key][0][c_comp]
        obj += s * coeff * a_val * c_val

    if vec:
        x, y, z = sp.symbols("x y z", real=True)
        obj = np.array(
            [i.subs({x: sp.Matrix([1, 0, 0]), y: sp.Matrix([0, 1, 0]), z: sp.Matrix([0, 0, 1])}).tolist() for i in obj]
        ).reshape(-1, 3)

    return obj


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
