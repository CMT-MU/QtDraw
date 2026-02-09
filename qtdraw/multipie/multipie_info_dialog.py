"""
MultiPie information dialog.

This module provides a dialog for group info. in MultiPie dialog.
"""

import numpy as np
import sympy as sp
from PySide6.QtWidgets import QDialog

from multipie.util.util_harmonics import harmonics_decomposition
from qtdraw.widget.custom_widget import Layout
from qtdraw.widget.table_view import TableView
from qtdraw.util.util import to_latex
from qtdraw.multipie.multipie_util import convert_vector_object


# ==================================================
class InfoPanel(QDialog):
    # ==================================================
    def __init__(self, parent, data, header, title, vertical):
        """
        Info panel.

        Args:
            parent (QWidget): parent.
            data (list): list of latex string without "$", [[str]].
            header (list): header. None is for no header.
            title (str): title of window.
            vertical (bool): show vertical (sequential number) header ?
        """
        super().__init__(parent)
        self._pvw = parent.parent._pvw
        mathjax = self._pvw._mathjax

        self.setWindowTitle(title)
        self.resize(800, 600)

        layout = Layout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        size = self._pvw._preference["general"]["size"]
        table = TableView(self, data, header, vertical, "black", size - 2, mathjax)
        layout.addWidget(table)

        self.show()


# ==================================================
def show_group_info(group, name, header, data, vertical, parent=None):
    """
    Show group info.

    Args:
        group (Group): group.
        name (str): title of dialog.
        header (list): header string. None is for no header.
        data (list): list of latex string without "$", [[str]].
        vertical (bool): show vertical (sequential number) header ?
        parent (QWidget, optional): parent.

    Returns:
        - (InfoPanel) -- panel.
    """
    title = name + " - " + group.name(detail=True)
    return InfoPanel(parent, data, header, title, vertical)


# ==================================================
def show_symmetry_operation(group, parent):
    """
    Show symmetry operation panel.

    Args:
        group (Group): all group.
        parent (QWidget): parent.

    Returns:
        - (InfoPanel) -- symmetry operation panel.
    """
    g_type = group.group_type
    SO = group.symmetry_operation

    name = "Symmetry Operation"
    header = ["No", "tag", "matrix (polar)", "det", "TR"]

    ops = [group.tag_symmetry_operation(i, True) for i in SO["tag"]]
    if group.is_point_group:
        mat = [sp.latex(sp.Matrix(i)) for i in SO["fractional"]]
    else:
        mat = [sp.latex(sp.Matrix(i)[0:3, :]) for i in SO["fractional"]]
    det = [str(i) for i in SO["det"]]
    if group.is_magnetic_group:
        tr = [str(i) for i in SO["tr_sign"]]

    data = []
    if g_type == "SG":
        ps = ["+" + to_latex(i, "vector") for i in SO["plus_set"]]
        data.append([r"{\rm PS}"] + ps + [""] * (4 - len(ps)))
        data.append(["", "", "", "", ""])

    if not group.is_magnetic_group:
        for no, i in enumerate(zip(ops, mat, det)):
            data.append([str(no + 1)] + list(i) + [""])
    else:
        for no, i in enumerate(zip(ops, mat, det, tr)):
            data.append([str(no + 1)] + list(i))

    return show_group_info(group, name, header, data, False, parent)


# ==================================================
def show_character_table(group, parent):
    """
    Show character table panel.

    Args:
        group (Group): point group.
        parent (QWidget): parent.

    Returns:
        - (InfoPanel) -- character table panel.
    """
    character = group.character

    name = "Character Table"
    first = [r"{\rm irrep.}"] + [group.tag_symmetry_operation(i[0], True) + f"({len(i)})" for i in character["conjugacy"]]
    row = [group.tag_irrep(i, True) for i in character["table"].keys()]

    data = [first]
    for r, i in zip(row, character["table"].values()):
        data.append([r] + [sp.latex(c) for c in i])

    return show_group_info(group, name, None, data, False, parent)


# ==================================================
def show_wyckoff_site(group, parent):
    """
    Show Wyckoff position panel.

    Args:
        group (Group): group.
        parent (QWidget): parent.

    Returns:
        - (InfoPanel) -- Wyckoff site panel.
    """
    g_type = group.group_type
    SO = group.symmetry_operation
    wp = group.wyckoff["site"]
    nop = len(SO["tag"])

    data = []
    if g_type in ["SG"]:
        ps = ["+" + to_latex(i, "vector") for i in SO["plus_set"]]
        data.append([r"{\rm PS}"] + ps + [""] * (4 - len(ps)))
        data.append(["", "", "", "", ""])

    for w, val in wp.items():
        sym = val["symmetry"]
        pos = val["conventional"]
        mp = val["mapping"]
        data.append([r"{\rm " + w + "}", r"{\rm " + sym + "}", "", "", ""])
        for no, (i, m) in enumerate(zip(pos, mp)):
            if nop > 24 and len(m) == nop:
                ms = f"[1, ..., {nop}]"
            else:
                ms = str(m)
            data.append([f"{no+1}", to_latex(i, "vector"), ms, "", ""])
        data.append(["", "", ""])

    name = "Wyckoff Site"
    header = ["No", "position", "mapping", "", ""]

    return show_group_info(group, name, header, data, False, parent)


# ==================================================
def show_wyckoff_bond(group, parent):
    """
    Show Wyckoff position panel.

    Args:
        group (Group): point/space group.
        parent (QWidget): parent.

    Returns:
        - (InfoPanel) -- Wyckoff bond panel.
    """
    g_type = group.group_type
    SO = group.symmetry_operation
    wp = group.wyckoff["bond"]
    nop = len(SO["tag"])

    data = []
    if g_type in ["SG"]:
        ps = ["+" + to_latex(i, "vector") for i in SO["plus_set"]]
        data.append([r"{\rm PS}"] + ps + [""] * (4 - len(ps)))
        data.append(["", "", "", "", ""])

    for b_wp, val in wp.items():
        # sym = val["symmetry"]
        bond = val["conventional"]
        mp = val["mapping"]
        vector, center = bond[:, 0:3], bond[:, 3:6]
        data.append([r"{\rm " + b_wp + "}", "", "", "", ""])
        for no, (v, c, m) in enumerate(zip(vector, center, mp)):
            if nop > 24 and len(m) == nop:
                ms = f"[1, ..., {nop}]"
            else:
                ms = str(m)
            data.append([f"{no+1}", to_latex(v, "vector"), to_latex(c, "vector"), ms, ""])

    name = "Wyckoff Bond"
    header = ["No", "vector", "center", "mapping", ""]

    return show_group_info(group, name, header, data, False, parent)


# ==================================================
def show_product_table(group, parent):
    """
    Show product table panel.

    Args:
        group (Group): point group.
        parent (QWidget): parent.

    Returns:
        - (InfoPanel) -- product table panel.
    """
    SO = group.symmetry_operation

    name = "Product Table"
    ops = [group.tag_symmetry_operation(i, True) for i in SO["tag"]]

    tbl = [["" for _ in range(len(ops))] for _ in range(len(ops))]
    for (i, j), p in SO["product"].items():
        ni = SO["tag"].index(i)
        nj = SO["tag"].index(j)
        tbl[ni][nj] = group.tag_symmetry_operation(p, True)

    data = []
    data.append([""] + ops)
    for r, t in zip(ops, tbl):
        data.append([r] + t)

    return show_group_info(group, name, None, data, False, parent)


# ==================================================
def show_harmonics_decomp(group, basis, rank, head, parent):
    """
    Show harmonics decomposition panel.

    Args:
        group (Group): PG expressed by basis PG.
        basis (str): basis PG.
        rank (int): rank.
        head (str): type, Q/G.
        parent (QWidget): parent.

    Returns:
        - (InfoPanel) -- harmonics decomposition panel.
    """
    pg = str(group)
    decomp = harmonics_decomposition(basis, pg, rank, head)

    name = head + "_harmonics decomposition to " + basis
    header = [pg, basis]

    data = []
    for h, d in decomp:
        ex = sp.S(0)
        for c, b in d:
            ex += c * sp.Symbol(b)
        data.append([h, to_latex(ex)])

    return show_group_info(group, name, header, data, True, parent)


# ==================================================
def show_harmonics_info(group, head, rank, parent):
    """
    Show harmonics decomposition panel.

    Args:
        group (Group): PG expressed by basis PG.
        basis (str): basis PG.
        rank (int): rank.
        head (str): type, Q/G.
        parent (QWidget): parent.

    Returns:
        - (InfoPanel) -- harmonics decomposition panel.
    """
    harmonics = group.harmonics.select(X=head, l=rank)

    name = f"Harmonics ({head}, {rank})"
    header = ["symbol", "expression"]

    data = []
    for idx, (ex, u, lc) in harmonics.items():
        for comp, e in enumerate(ex):
            data.append([group.tag_multipole(idx, comp, True), to_latex(e)])

    return show_group_info(group, name, header, data, True, parent)


# ==================================================
def show_atomic_multipole(group, bra, ket, head, basis_type, tesseral, parent):
    """
    Show atomic multipole panel.

    Args:
        group (Group): PG.
        bra (str): bra basis list.
        ket (str): ket basis list.
        head (str): head.
        basis_type (str): basis type.
        tesseral (bool): is tesseral basis ?
        parent (QWidget): parent.

    Returns:
        - (InfoPanel) -- symmetry operation panel.
    """
    rank_dict = {"s": 0, "p": 1, "d": 2, "f": 3}
    mask_idx = {
        "s : 1/2": [0, 1],
        "p : 1/2, 3/2": [0, 1, 2, 3, 4, 5],
        "p : 1/2": [0, 1],
        "p : 3/2": [2, 3, 4, 5],
        "d : 3/2, 5/2": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        "d : 3/2": [0, 1, 2, 3],
        "d : 5/2": [4, 5, 6, 7, 8, 9],
        "f : 5/2, 7/2": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
        "f : 5/2": [0, 1, 2, 3, 4, 5],
        "f : 7/2": [6, 7, 8, 9, 10, 11, 12, 13],
    }
    if basis_type == "jml":
        bra_m = mask_idx[bra]
        bra = bra.split(":")[0].replace(" ", "")
        ket_m = mask_idx[ket]
        ket = ket.split(":")[0].replace(" ", "")
        mask = (bra_m, ket_m)
    else:
        mask = None

    bra = rank_dict[bra]
    ket = rank_dict[ket]

    name = "Atomic Multipole"
    header = ["No", "multipole", "matrix"]

    samb = group.atomic_samb(basis_type, (bra, ket), mask)
    if head != "":
        samb = samb.select(X=head)

    if basis_type == "jml":
        bras = group.tag_atomic_basis_proj(basis_type, bra, bra_m, ket=False)
        kets = group.tag_atomic_basis_proj(basis_type, ket, ket_m)
        bras = ", ".join(to_latex(bras))
        kets = ", ".join(to_latex(kets))
    else:
        if tesseral:
            basis = group.atomic_basis(basis_type)
        else:
            spinful = basis_type[-1] == "s"
            samb = group.transform_atomic_samb(samb, ket, bra, spinful=spinful)
            tp = "hexagonal" if group.is_hexagonal_subgroup else "cubic"
            sf = "spinful" if spinful else "spinless"
            basis = group.global_info()["harmonics"]["atomic_basis"][sf][tp]

        bras = ", ".join([group.tag_atomic_basis(i, bra, latex=True, ket=False) for i in basis[bra]])
        kets = ", ".join([group.tag_atomic_basis(i, ket, latex=True, ket=True) for i in basis[ket]])

    samb = samb.sort(("X", ["Q", "G", "T", "M"]), "Gamma", "s", "k", "l", "n", "p")
    data = [["", r"{\rm bra}", bras], ["", r"{\rm ket}", kets], ["", "", ""]]
    no = 1
    for idx, (mat, ex) in samb.items():
        for comp, m in enumerate(mat):
            data.append([str(no), group.tag_multipole(idx, comp, True, "a"), to_latex(m, "matrix")])
            no += 1

    return show_group_info(group, name, header, data, False, parent)


# ==================================================
def show_response(group, rank, r_type, parent):
    """
    Show response tensor panel.

    Args:
        group (Group): MPG.
        rank (int): response tensor rank.
        r_type (str): response tensor type.
        parent (QWidget): parent.

    Returns:
        - (InfoPanel) -- response tensor panel.
    """
    rank_dict = {0: "s", 1: "p", 2: "d", 3: "f", 4: "g"}
    d = group.response_tensor_all(r_type)
    lst0 = group.active_multipole
    lst = {}
    for i in lst0:
        for r in range(rank + 1):
            if rank_dict[r] in i:
                lst[i[0]] = lst.get(i[0], []) + [i[1:]]

    data = []
    data.append([r"\text{active multipole}"])
    if lst.get("Q"):
        data.append([r"\text{Q: " + ", ".join(lst["Q"]) + "}"])
    if lst.get("G"):
        data.append([r"\text{G: " + ", ".join(lst["G"]) + "}"])
    if lst.get("T"):
        data.append([r"\text{T: " + ", ".join(lst["T"]) + "}"])
    if lst.get("M"):
        data.append([r"\text{M: " + ", ".join(lst["M"]) + "}"])
    data.append([""])

    for t, (m, ex) in d.items():
        X, rank1, opt = t
        if rank1 != rank:
            continue
        if opt == "":
            data.append([r"\text{" + f"rank {rank} tensor" + "}"])
        else:
            data.append([r"\text{" + f"rank {rank} tensor ({opt})" + "}"])
        if not np.all(m == sp.S(0)):
            ml = to_latex(m, "matrix")
            data.append([ml])
            for i, j in ex.items():
                data.append([sp.latex(sp.Eq(i, j))])
        data.append([""])

    name = r_type + " Response Tensor"

    return show_group_info(group, name, None, data, False, parent)


# ==================================================
def show_site_samb_panel(group, lst, wp, samb_list, samb, parent):
    """
    Show site SAMB panel.

    Args:
        group (Group): point/space group.
        lst (list): combo list.
        wp (str): wyckoff.
        samb_list (list): SAMB (index, comp) list.
        samb (dict): SAMB dict.
        parent (QWidget): parent.

    Returns:
        - (InfoPanel) -- site SAMB panel.
    """
    name = f"Site SAMB - {wp}"
    header = ["tag", "symbol", "symmetry"]

    data = []
    for tag, (s, comp) in zip(lst, samb_list):
        t = r"\texttt{" + tag + "}"
        tl = group.tag_multipole(s, comp, latex=True)
        ex = to_latex(samb[s][1][comp])
        data.append([t, tl, ex])

    return show_group_info(group, name, header, data, False, parent)


# ==================================================
def show_bond_samb_panel(group, lst, wp, samb_list, samb, parent):
    """
    Show bond SAMB panel.

    Args:
        group (Group): point/space group.
        lst (list): combo list.
        wp (str): wyckoff.
        samb_list (list): SAMB (index, comp) list.
        samb (dict): SAMB dict.
        parent (QWidget): parent.

    Returns:
        - (InfoPanel) -- bond SAMB panel.
    """
    name = f"Bond SAMB - {wp}"
    header = ["tag", "symbol", "symmetry"]

    data = []
    for tag, (s, comp) in zip(lst, samb_list):
        t = r"\texttt{" + tag + "}"
        tl = group.tag_multipole(s, comp, latex=True)
        ex = to_latex(samb[s][1][comp])
        data.append([t, tl, ex])

    return show_group_info(group, name, header, data, False, parent)


# ==================================================
def show_vector_samb_panel(group, lst, wp, tp, samb_list, samb, parent):
    """
    Show vector SAMB panel.

    Args:
        group (Group): point/space group.
        lst (list): combo list.
        wp (str): wyckoff.
        tp (str): atomic type.
        samb_list (list): SAMB (index, comp) list.
        samb (dict): SAMB dict.
        parent (QWidget): parent.

    Returns:
        - (InfoPanel) -- vector SAMB panel.
    """
    name = f"Vector SAMB - {wp}"
    header = ["tag", "symbol", "symmetry", "1st cluster (f.c.)"]

    data = []
    for tag, (s, comp) in zip(lst, samb_list):
        t = r"\texttt{" + tag + "}"
        tl = group.tag_multipole(s, comp, latex=True)
        ts = samb[s][0][comp]
        ts = to_latex(convert_vector_object([group.combined_object(wp, tp, ts)[0]])[0], "vector")
        ex = to_latex(samb[s][1][comp])
        data.append([t, tl, ex, ts])

    return show_group_info(group, name, header, data, False, parent)


# ==================================================
def show_orbital_samb_panel(group, lst, wp, tp, samb_list, samb, parent):
    """
    Show orbital SAMB panel.

    Args:
        group (Group): point/space group.
        lst (list): combo list.
        wp (str): wyckoff.
        tp (str): atomic type.
        samb_list (list): SAMB (index, comp) list.
        samb (dict): SAMB dict.
        parent (QWidget): parent.

    Returns:
        - (InfoPanel) -- orbital SAMB panel.
    """
    name = f"Orbital SAMB - {wp}"
    header = ["tag", "symbol", "symmetry", "1st cluster (c.c.)"]

    data = []
    for tag, (s, comp) in zip(lst, samb_list):
        t = r"\texttt{" + tag + "}"
        tl = group.tag_multipole(s, comp, latex=True)
        ts = samb[s][0][comp]
        ts = to_latex(group.combined_object(wp, tp, ts)[0])
        ex = to_latex(samb[s][1][comp])  # symmetry
        data.append([t, tl, ex, ts])

    return show_group_info(group, name, header, data, False, parent)
