"""
Info. dialog.

This module provides a dialog for group info. in MultiPie dialog.
"""

import sympy as sp
from PySide6.QtWidgets import QDialog
from gcoreutils.list_util import list_to_table
from gcoreutils.nsarray import NSArray
from multipie.tag.tag_multipole import TagMultipole
from multipie.tag.tag_irrep import TagIrrep
from qtdraw.widget.custom_widget import Layout
from qtdraw.widget.table_view import TableView


# ==================================================
class InfoPanel(QDialog):
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
        latex = parent.plugin._pvw._preference["latex"]

        self.setWindowTitle(title)
        self.resize(800, 600)

        layout = Layout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        color = latex["color"]
        size = latex["size"]
        dpi = latex["dpi"]
        table = TableView(self, data, header, vertical, color, size, dpi)
        layout.addWidget(table)

        self.show()


# ==================================================
def show_group_info(
    group,
    name,
    header,
    data,
    vertical,
    parent=None,
):
    """
    Show group info.

    Args:
        group (PointGroup or SpaceGroup): group.
        name (str): title of dialog.
        header (list): header string. None is for no header.
        data (list): list of latex string without "$", [[str]].
        vertical (bool): show vertical (sequential number) header ?
        parent (QWidget, optional): parent.

    Returns:
        - (InfoPanel) -- panel.
    """
    no, _, IS, setting = group.tag.info()
    s = f"No.{no}: {str(group)}, {IS}"
    if setting:
        s += " (" + setting + " setting)"
    title = name + " - " + s

    return InfoPanel(parent, data, header, title, vertical)


# ==================================================
def show_symmetry_operation(group, parent):
    """
    Show symmetry operation panel.

    Args:
        group (PointGroup): point group.
        parent (QWidget): parent.

    Returns:
        - (InfoPanel) -- symmetry operation panel.
    """
    so = group.symmetry_operation

    name = "symmetry_operation"
    header = ["symbol", "polar vector", "axial vector", "det"]

    data = []
    if not group.tag.is_point_group():
        ps = ["+" + i for i in so.plus_set.latex()]
        data.append(ps + [""] * (4 - len(ps)))
        data.append(["", "", "", ""])

    pso = so.mat(axial=False)
    aso = so.mat(axial=True)
    for no in range(len(so)):
        p = pso[no][0:3, :]
        a = aso[no][0:3, :]
        data.append([so.full[no].latex(), p.latex(), a.latex(), p[0:3, 0:3].det().latex()])

    return show_group_info(group, name, header, data, False, parent)


# ==================================================
def show_character_table(group, parent):
    """
    Show character table panel.

    Args:
        group (PointGroup): point group.
        parent (QWidget): parent.

    Returns:
        - (InfoPanel) -- character table panel.
    """
    ch = group.character

    name = "character"
    n = len(ch.symmetry_operation())
    header = ["irrep."] + [f"SO{i+1}" for i in range(n)]

    data = []
    data.append([""] + [i.latex() for i in ch.symmetry_operation()])
    for r in ch.irrep_list:
        data.append([r.latex()] + [sp.latex(j) for j in ch.character(r)])

    return show_group_info(group, name, header, data, False, parent)


# ==================================================
def show_wyckoff(group, parent):
    """
    Show Wyckoff position panel.

    Args:
        group (PointGroup): point group.
        parent (QWidget): parent.

    Returns:
        - (InfoPanel) -- Wyckoff position panel.
    """
    wp = group.wyckoff
    so = group.symmetry_operation

    name = "wyckoff_position"
    n = list(wp.keys())[-1].n
    if not group.tag.is_point_group():
        ns = len(so.plus_set)
        n = n // ns
    n = min(10, n)
    header = ["WP"] + [str(i + 1) for i in range(n)]

    data = []
    if not group.tag.is_point_group():
        ps = ["+" + i for i in so.plus_set.latex()]
        data.append([""] + ps + [""] * (n - len(ps)))
        data.append([""] * (n - len(ps) + 2))

    for w in wp.keys():
        row = list_to_table(wp.position(w).latex(), n, "")
        for i, r in enumerate(row):
            if i == 0:
                data.append([str(w)] + r)
            else:
                data.append([""] + r)

    return show_group_info(group, name, header, data, False, parent)


# ==================================================
def show_product_table(group, parent):
    """
    Show product table panel.

    Args:
        group (PointGroup): point group.
        parent (QWidget): parent.

    Returns:
        - (InfoPanel) -- product table panel.
    """
    so = group.symmetry_operation

    name = "product_table"
    op = [i.latex() for i in so.keys()]
    header = ["SO"] + [f"SO{i+1}" for i in range(len(op))]

    data = []
    data.append([""] + op)
    for i in so.keys():
        data.append([i.latex()] + [so.product(i, j).latex() for j in so.keys()])

    return show_group_info(group, name, header, data, False, parent)


# ==================================================
def show_harmonics(group, rank, head, parent):
    """
    Show harmonics panel.

    Args:
        group (PointGroup): point group.
        rank (int): harmonics rank.
        head (str): harmonics type.
        parent (QWidget): parent.

    Returns:
        - (InfoPanel) -- harmonics panel.
    """
    pgh = group.harmonics
    head = head.replace("T", "Q").replace("M", "G")
    hs = pgh.select(rank=rank, head=head)

    name = head + "_harmonics"
    header = ["symbol", "rank", "irrep.", "mul.", "comp.", "expression", "definition"]

    data = []
    for h in hs:
        mul = h.tag.mul
        comp = h.tag.comp
        irrep = h.tag.tag_irrep()
        dim = irrep.dim
        if mul < 1:
            mul = ""
        if dim == 1:
            comp = ""
        data.append(
            [
                h.latex(),
                rank,
                irrep.latex(),
                mul,
                comp,
                h.expression(v=NSArray.vector3d(head)).latex(),
                h.definition().latex(),
            ]
        )

    return show_group_info(group, name, header, data, True, parent)


# ==================================================
def show_harmonics_decomp(group, rank, head, to_pg, parent):
    """
    Show harmonics decomposition panel.

    Args:
        group (PointGroup): point group.
        rank (int): harmonics rank.
        head (str): harmonics type.
        to_pg (str): destination point group.
        parent (QWidget): parent.

    Returns:
        - (InfoPanel) -- harmonics decomposition panel.
    """
    pgh = group.harmonics

    if to_pg.count(" ") > 0:
        to_pg = to_pg.split(" ")[1]

    head = head.replace("T", "Q").replace("M", "G")
    axial = head == "G"
    hs = pgh.select(rank=rank, head=head)
    decomp = group.irrep_decomposition(to_pg, rank, axial)

    name = head + "_harmonics decomposition to " + to_pg
    header = [str(group), " \u21d2 " + to_pg]

    data = []
    for h, d in zip(hs, decomp):
        ex = sp.S(0)
        for c, b in d[1]:
            ex += c * TagMultipole(b).symbol()
        data.append([h.latex(), sp.latex(ex)])

    return show_group_info(group, name, header, data, True, parent)


# ==================================================
def show_virtual_cluster(group, wp, parent):
    """
    Show virtual cluster panel.

    Args:
        group (PointGroup): point group.
        wp (str): Wyckoff position.
        parent (QWidget): parent.

    Returns:
        - (InfoPanel) -- virtual cluster panel.
    """
    basis, site = group.virtual_cluster_basis(wyckoff=wp)
    n = min(10, len(site))

    name = f"virtual cluster ({wp})"
    header = ["symbol"] + [f"S{i+1}" for i in range(n)]

    data = []
    row = list_to_table(site.latex(), n, "")
    for i, r in enumerate(row):
        if i == 0:
            data.append([r"\text{site (r.c.)}"] + r)
        else:
            data.append([""] + r)
    for tag, v in basis.items():
        row = list_to_table(NSArray(v.tolist(), "scalar").latex(), n, "")
        for i, r in enumerate(row):
            if i == 0:
                t = tag.latex()
            else:
                t = ""
            data.append([t] + r)

    return show_group_info(group, name, header, data, False, parent)


# ==================================================
def show_atomic_multipole(group, bra, ket, am, parent):
    """
    Show atomic multipole panel.

    Args:
        group (PointGroup): point group.
        bra (list): bra basis list.
        ket (list): ket basis list.
        am (dict): atomic multipoles.
        parent (QWidget): parent.

    Returns:
        - (InfoPanel) -- symmetry operation panel.
    """
    name = "atomic multipole"
    header = ["symbol", "rank", "irrep.", "s", "k", "basis"]

    data = []
    s = r"\langle " + ",".join(bra) + r"|" + ",".join(ket) + r"\rangle"
    data.append([""] * 5 + [s])
    data.append([""] * 6)
    for tag, am1 in am.items():
        data.append(
            [
                tag.latex(),
                tag.rank,
                TagIrrep(tag.irrep).latex(),
                tag.s,
                tag.k,
                am1.latex(),
            ]
        )

    return show_group_info(group, name, header, data, False, parent)


# ==================================================
def show_response(group, rank, r_type, parent):
    """
    Show response tensor panel.

    Args:
        group (PointGroup): point group.
        rank (int): response tensor rank.
        r_type (str): response tensor type.
        parent (QWidget): parent.

    Returns:
        - (InfoPanel) -- response tensor panel.
    """
    dic = {"Q": "E_polar", "T": "M_polar", "G": "E_axial", "M": "M_axial"}
    pgr = group.response
    head = r_type
    rt = pgr.select(rank=rank, head=head)

    name = dic[head] + "_response"
    header = ["symbol", "tensor"]

    data = []
    for tag in rt.keys():
        M = rt[tag]
        data.append([tag.latex(), M.latex()])

    data.append(["", ""])
    data.append([r"\text{component}", r"\text{multipole}"])
    for tag in rt.keys():
        def_mul = rt.definition[tag]
        for t, d in def_mul.items():
            data.append([sp.latex(t), sp.latex(d)])

    return show_group_info(group, name, header, data, False, parent)
