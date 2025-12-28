"""
MultiPie utility.

This module provides utilities for MultiPie dialog.
"""

import numpy as np
import sympy as sp

from qtdraw.util.util import str_to_sympy, igrid


# ==================================================
def phase_factor(modulation, repeat, pset):
    """
    Create phase factor.

    Args:
        modulation (list): modulation info. [(basis, coeff, k, n)].
        repeat (list): repeat.
        pset (ndarray): plus_set.

    Returns:
        - (dict) -- {(k(str),n(int),plus_set no(int)): [phase at each grid(float)]}.
        - (list) -- cell grid.
    """
    grid = igrid(repeat)
    if pset is None:
        pset = np.ndarray([[0, 0, 0]])

    phase_dict = {}
    for _, _, k, n in modulation:
        kvec = str_to_sympy(k).astype(float)
        for p_no, p in enumerate(pset):
            lst = []
            for i in grid:
                kr = 2.0 * np.pi * kvec @ (i + p)
                phase = np.cos(kr) if n == "cos" else np.sin(kr)
                lst.append(phase)
            phase_dict[(k, n, p_no)] = lst
    grid = grid.astype(int).tolist()

    return phase_dict, grid


# ==================================================
def create_samb_modulation(group, modulation, phase_dict, igrid, pset, samb, samb_list, wp, site):
    igrid = np.asarray(igrid)

    ns = len(site)
    n_pset = len(pset)
    n_prim = ns // n_pset
    n_grid = len(igrid)

    obj = np.full((n_grid, ns), sp.S(0), dtype=object)
    for basis, coeff, k, n in modulation:
        tp = basis[0]
        idx = int(basis[1:]) - 1
        coeff = str_to_sympy(coeff)
        samb1, comp = samb_list[tp][idx]
        samb2 = samb[tp][samb1][0][comp]
        m_obj = group.combined_object(wp, tp, samb2)
        m_obj = np.tile(m_obj, n_pset)
        phase_all = np.empty((n_grid, n_pset), dtype=object)
        for p_no in range(n_pset):
            phase_all[:, p_no] = phase_dict[(k, n, p_no)]
        m = m_obj.reshape(n_pset, -1)
        obj += coeff * (phase_all[:, :, None] * m[None, :, :]).reshape(n_grid, ns)
    obj = obj.reshape(-1)

    fs_no = np.tile(np.arange(ns), n_grid)
    p_no = fs_no // n_prim
    s_no = fs_no % n_prim
    site_idx = np.column_stack((p_no, s_no))
    site_idx = [f"(p{i[0]+1},s{i[1]+1})" for i in site_idx]
    full_site = (igrid[:, None] + site[None, :]).reshape(-1, site.shape[1])

    return obj, site_idx, full_site


# ==================================================
def convert_vector_object(obj):
    x, y, z = sp.symbols("x y z", real=True)
    ex = {x: sp.Matrix([1, 0, 0]), y: sp.Matrix([0, 1, 0]), z: sp.Matrix([0, 0, 1])}
    obj = np.array([sp.Matrix([0, 0, 0]) if i == 0 else i.subs(ex) for i in obj]).reshape(-1, 3)

    return obj


# ==================================================
def check_linear_combination(ex, basis_var):
    var_e = set(basis_var["Q"] + basis_var["G"])
    var_m = set(basis_var["T"] + basis_var["M"])

    ex = str_to_sympy(ex.upper())
    ex_var = set(map(str, ex.free_symbols))

    if ex_var.issubset(var_e) or ex_var.issubset(var_m):
        return ex, ex_var
    else:
        return None, None
