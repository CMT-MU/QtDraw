"""
Info. dialog.

This module provides a dialog for group info. in MultiPie dialog.
"""

import sympy as sp
from PySide6.QtWidgets import QDialog

from qtdraw.widget.custom_widget import Layout
from qtdraw.widget.table_view import TableView
from qtdraw.util.util import to_latex


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
        self._pvw = parent.parent()._pvw
        mathjax = self._pvw._mathjax

        self.setWindowTitle(title)
        self.resize(800, 600)

        layout = Layout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        size = self._pvw._preference["general"]["size"]
        table = TableView(self, data, header, vertical, "black", size, mathjax)
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
    SO = group["symmetry_operation"]

    name = "Symmetry Operation"
    header = ["No", "tag", "matrix (polar)", "det", "TR"]

    ops = [group.tag_symmetry_operation(i, True) for i in SO["tag"]]
    if g_type in ["PG", "MPG"]:
        mat = [sp.latex(sp.Matrix(i)) for i in SO["fractional"]]
    else:
        mat = [sp.latex(sp.Matrix(i)[0:3, :]) for i in SO["fractional"]]
    det = [str(i) for i in SO["det"]]
    if g_type in ["MPG", "MSG"]:
        tr = [str(i) for i in SO["tr_sign"]]

    data = []
    if g_type in ["SG"]:
        ps = ["+" + to_latex(i, "vector") for i in SO["plus_set"]]
        data.append([r"{\rm PS}"] + ps + [""] * (4 - len(ps)))
        data.append(["", "", "", "", ""])

    if g_type in ["PG", "SG"]:
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
    character = group["character"]

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
        group (Group): point/space group.
        parent (QWidget): parent.

    Returns:
        - (InfoPanel) -- Wyckoff site panel.
    """
    g_type = group.group_type
    SO = group["symmetry_operation"]
    wp = group["wyckoff"]["site"]

    data = []
    if g_type in ["SG"]:
        ps = ["+" + to_latex(i, "vector") for i in SO["plus_set"]]
        data.append([r"{\rm PS}"] + ps + [""] * (4 - len(ps)))
        data.append(["", "", "", "", ""])

    for w, val in wp.items():
        sym = val["symmetry"]
        pos = val["expression"]
        mp = val["mapping"]
        data.append([r"{\rm " + w + "}", "", r"{\rm " + sym + "}", "", ""])
        for no, (i, m) in enumerate(zip(pos, mp)):
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
    SO = group["symmetry_operation"]
    wp = group["wyckoff"]["bond"]

    data = []
    if g_type in ["SG"]:
        ps = ["+" + to_latex(i, "vector") for i in SO["plus_set"]]
        data.append([r"{\rm PS}"] + ps + [""] * (4 - len(ps)))
        data.append(["", "", "", "", ""])

    for b_wp, val in wp.items():
        # sym = val["symmetry"]
        bond = val["expression"]
        mp = val["mapping"]
        vector, center = bond[:, 0:3], bond[:, 3:6]
        data.append([r"{\rm " + b_wp + "}", "", "", "", ""])
        for no, (v, c, m) in enumerate(zip(vector, center, mp)):
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
    SO = group["symmetry_operation"]

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
