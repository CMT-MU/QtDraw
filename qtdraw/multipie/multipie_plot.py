"""
MultiPie plot.

This module provides plot functions for MultiPie dialog.
"""

import numpy as np

from qtdraw.multipie.multipie_setting import setting_detail as detail

CHOP = 1e-6


# ==================================================
def plot_cell_site(dialog, sites, wp=None, label=None, size=None, color=None, opacity=None, name=None):
    """
    Plot cell site.

    Args:
            dialog (MultiPieDialog): multipie dialog.
            sites (ndarray): sites (fractional, conventional).
            wp (str, optional): Wyckoff site.
            label (list, optional): label.
            size (float, optional): size [default: 0.05].
            color (str, optional): color [default: silver].
            opacity (float, optional): opacity [default: 1.0].
            name (str, optional): plot name.
    """
    pvw = dialog._pvw

    if name is None:
        if wp is None:
            cnt = dialog._set_counter("site")
            name = f"site{cnt}"
        else:
            cnt = dialog._set_counter(wp)
            name = f"{wp}({cnt})"

    if label is None:
        label = [""] * len(sites)

    default = detail["site"]
    if size is None:
        size = default["size"]
    if color is None:
        color = default["color"]
    if opacity is None:
        opacity = default["opacity"]

    for no, (pt, m) in enumerate(zip(sites, label)):
        lbl = f"S{no+1}:{m}".replace(" ", "")
        pvw.add_site(position=pt, name=name, label=lbl, size=size, color=color, opacity=opacity)


# ==================================================
def plot_cell_bond(dialog, bonds, wp=None, label=None, width=None, color=None, color2=None, opacity=None, name=None):
    """
    Plot cell bond.

    Args:
            dialog (MultiPieDialog): multipie dialog.
            bonds (ndarray): bonds (fractional, conventional).
            wp (str, optional): Wyckoff bond.
            label (list, optional): label.
            width (float, optional): width [default: 0.01].
            color (str, optional): color [default: silver].
            color2 (str, optional): color for directional bond [default: iron].
            opacity (float, optional): opacity [default: 1.0].
            name (str, optional): plot name.
    """
    pvw = dialog._pvw

    if name is None:
        if wp is None:
            cnt = dialog._set_counter("bond")
            name = f"bond{cnt}"
        else:
            cnt = dialog._set_counter(wp)
            name = f"{wp}({cnt})"

    if label is None:
        label = [""] * len(bonds)
        directional = False
    else:
        directional = not any(x < 0 for x in sum(label, []))

    default = detail["bond"]
    if width is None:
        width = default["width"]
    if color is None:
        color = default["color1"]
    if color2 is None:
        color2 = default["color2"]
    if opacity is None:
        opacity = default["opacity"]

    if not directional:
        color2 = color

    for no, (b, m) in enumerate(zip(bonds, label)):
        v, c = b[0:3], b[3:6]
        lbl = f"B{no+1}:{m}".replace(" ", "")
        pvw.add_bond(direction=v, position=c, width=width, color=color, color2=color2, opacity=opacity, name=name, label=lbl)


# ==================================================
def plot_cell_vector(
    dialog,
    vectors,
    sites,
    X="Q",
    wp=None,
    label=None,
    length=None,
    width=None,
    color=None,
    opacity=None,
    average=True,
    cartesian=False,
    name=None,
):
    """
    Plot cell vector.

    Args:
        dialog (MultiPieDialog): multipie dialog.
            vectors (ndarray): vectors (fractional/cartesian).
            sites (ndarray): site/bond (fractional, conventional).
            X (str, optional): type, "Q/G/T/M".
            wp (str, optional): Wyckoff site/bond.
            label (list, optional): label.
            length (float, optional): length [default: 0.3].
            width (float, optional): width [default: 0.02].
            color (_type_, optional): color [default: orange/yellowgreen/hotpink/lightskyblue for Q/G/T/M].
            opacity (float, optional): opacity [default: 1.0].
            average (bool, optional): average at each site ?
            cartesian (bool, optional): vector in cartesian coordinate ?
            name (str, optional): plot name.
    """
    pvw = dialog._pvw

    if name is None:
        if wp is None:
            cnt = dialog._set_counter("vector")
            name = f"vector{cnt}"
        else:
            cnt = dialog._set_counter(wp)
            name = f"{wp}({cnt})"

    if label is None:
        label = [""] * len(sites)

    default = detail["vector"]
    if length is None:
        length = default["length"]
    if width is None:
        width = default["width"]
    if color is None:
        color = default["color"][X]
    if opacity is None:
        opacity = default["opacity"]

    vectors = vectors.astype(float)

    if average:
        for no, (v, s, m) in enumerate(zip(vectors, sites, label)):
            if np.linalg.norm(v) < CHOP:
                continue
            lbl = f"V{no+1}:{m}".replace(" ", "")
            pvw.add_vector(
                direction=v,
                length=-length,
                width=width,
                color=color,
                opacity=opacity,
                cartesian=cartesian,
                position=s,
                name=name,
                label=lbl,
            )
    else:
        no = -1
        for vl, s, ml in zip(vectors, sites, label):
            for v, m in zip(vl, ml):
                no += 1
                if np.linalg.norm(v) < CHOP:
                    continue
                lbl = f"V{no+1}:[{m}]".replace(" ", "")
                pvw.add_vector(
                    direction=v,
                    length=-length,
                    width=width,
                    color=color,
                    opacity=opacity,
                    cartesian=cartesian,
                    position=s,
                    name=name,
                    label=lbl,
                )


# ==================================================
def plot_cell_multipole(
    dialog, multipoles, sites, X="Q", wp=None, label=None, size=None, color=None, opacity=None, average=True, name=None
):
    """
    Plot cell multipole.

    Args:
        dialog (MultiPieDialog): multipie dialog.
            multipoles (ndarray): multipoles (cartesian).
            sites (ndarray): site/bond (fractional, conventional).
            X (str, optional): type, "Q/G/T/M".
            wp (str, optional): Wyckoff site/bond.
            label (list, optional): label.
            size (float, optional): size [default: 0.2].
            color (_type_, optional): color [default: Wistia/PiYG/coolwarm/GnBu for Q/G/T/M].
            opacity (float, optional): opacity [default: 1.0].
            average (bool, optional): average at each site ?
            name (str, optional): plot name.
    """
    pvw = dialog._pvw

    if name is None:
        if wp is None:
            cnt = dialog._set_counter("orbital")
            name = f"orbital{cnt}"
        else:
            cnt = dialog._set_counter(wp)
            name = f"{wp}({cnt})"

    if label is None:
        label = [""] * len(sites)

    default = detail["orbital"]
    if size is None:
        size = default["size"]
    if color is None:
        color = default["color"][X]
    if opacity is None:
        opacity = default["opacity"]

    if average:
        for no, (v, s, m) in enumerate(zip(multipoles, sites, label)):
            if v == 0:
                continue
            lbl = f"O{no+1}:{m}".replace(" ", "")
            pvw.add_orbital(shape=v, surface=v, size=-size, color=color, opacity=opacity, position=s, name=name, label=lbl)
    else:
        no = -1
        for vl, s, ml in zip(multipoles, sites, label):
            for v, m in zip(vl, ml):
                no += 1
                if v == 0:
                    continue
                lbl = f"O{no+1}:[{m}]".replace(" ", "")
                pvw.add_orbital(shape=v, surface=v, size=-size, color=color, opacity=opacity, position=s, name=name, label=lbl)


# ==================================================
def plot_bond_definition(
    dialog,
    bonds,
    wp,
    label=None,
    rep=True,
    name=None,
    length=None,
    width=None,
    opacity=None,
    color=None,
    arrow_color=None,
    arrow_color_rep=None,
):
    pvw = dialog._pvw

    default = detail["bond_samb"]

    if length is None:
        length = default["length"]
    if width is None:
        width = default["width"]
    if opacity is None:
        opacity = default["opacity"]
    if color is None:
        color = default["color"]
    if arrow_color is None:
        arrow_color = default["arrow_color"]
    if arrow_color_rep is None:
        arrow_color_rep = default["arrow_color_rep"]

    if name is None:
        cnt = dialog._set_counter(wp)
        name = f"{wp}({cnt})"

    if label is None:
        label = [""] * len(bonds)

    opt = opacity
    for no, (b, m) in enumerate(zip(bonds, label)):
        v, c = b[0:3], b[3:6]
        lbl = f"B{no+1}:{m}".replace(" ", "")
        pvw.add_bond(
            position=c,
            direction=v,
            color=color,
            color2=color,
            width=width,
            cartesian=False,
            opacity=opt,
            label=lbl,
            name=name,
        )
        acolor = arrow_color_rep if rep and no == 0 else arrow_color
        pvw.add_vector(position=c, direction=v, length=-length, color=acolor, width=0.01, cartesian=False, label=lbl, name=name)


# ==================================================
def plot_site_cluster(
    dialog, site, samb, wp, label=None, color=None, color_neg=None, color_pos=None, zero_size=None, size_ratio=None
):
    pvw = dialog._pvw

    if isinstance(samb, np.ndarray):
        samb = samb.astype(float)

    default = detail["site_samb"]
    if color is None:
        color = default["color"]
    if color_neg is None:
        color_neg = default["color_neg"]
    if color_pos is None:
        color_pos = default["color_pos"]
    if zero_size is None:
        zero_size = default["zero_size"]
    if size_ratio is None:
        size_ratio = default["size_ratio"]

    cnt = dialog._set_counter(wp)
    name = f"{wp}({cnt})"

    if label is None:
        label = [""] * len(site)

    for i, (no, s, v) in enumerate(zip(label, site, samb)):
        lbl = f"S{i+1}:{no}".replace(" ", "")
        if v > 0:
            c = color_pos
        elif v < 0:
            c = color_neg
        else:
            c = color
            v = zero_size
        pvw.add_site(position=s, size=size_ratio * abs(v), color=c, name=name, label=lbl)


# ==================================================
def plot_bond_cluster(
    dialog,
    bond,
    samb,
    wp,
    label=None,
    sym=True,
    color=None,
    color_neg=None,
    color_pos=None,
    width=None,
    arrow_ratio=None,
    width_ratio=None,
):
    pvw = dialog._pvw

    if isinstance(samb, np.ndarray):
        if sym:
            samb = samb.astype(float)
        else:
            samb = samb.astype(complex).imag

    default = detail["bond_samb"]
    if color is None:
        color = default["color"]
    if color_neg is None:
        color_neg = default["color_neg"]
    if color_pos is None:
        color_pos = default["color_pos"]
    if width is None:
        width = default["width"]
    if arrow_ratio is None:
        arrow_ratio = default["arrow_ratio"]
    if width_ratio is None:
        width_ratio = default["width_ratio"]

    cnt = dialog._set_counter(wp)
    name = f"{wp}({cnt})"

    if label is None:
        label = [""] * len(bond)

    if sym:
        for i, (no, b, h) in enumerate(zip(label, bond, samb)):
            v, c = b[0:3], b[3:6]
            lbl = f"B{i+1}:{no}".replace(" ", "")
            if abs(h) < CHOP:
                pvw.add_bond(
                    position=c, direction=v, color=color, color2=color, width=width, cartesian=False, name=name, label=lbl
                )
            else:
                cl = color_neg if h < 0 else color_pos
                width = width_ratio * abs(h)
                pvw.add_bond(position=c, direction=v, color=cl, color2=cl, width=width, cartesian=False, name=name, label=lbl)
    else:
        for i, (no, b, h) in enumerate(zip(label, bond, samb)):
            v, c = b[0:3], b[3:6]
            lbl = f"B{i+1}:{no}".replace(" ", "")
            if abs(h) < CHOP:
                pvw.add_bond(
                    position=c,
                    direction=arrow_ratio * v,
                    color=color,
                    color2=color,
                    width=width,
                    cartesian=False,
                    name=name,
                    label=lbl,
                )
            else:
                if h < 0:
                    v = -v
                cl = color_pos
                width = width_ratio * abs(h)
                pvw.add_vector(
                    position=c, direction=v, length=-arrow_ratio, color=cl, width=width, cartesian=False, name=name, label=lbl
                )


# ==================================================
def plot_vector_cluster(
    dialog, site, samb, X="Q", wp=None, label=None, cartesian=True, length=None, width=None, color=None, opacity=None, name=None
):
    pvw = dialog._pvw

    if name is None:
        if wp is None:
            cnt = dialog._set_counter("vector")
            name = f"vector{cnt}"
        else:
            cnt = dialog._set_counter(wp)
            name = f"{wp}({cnt})"

    default = detail["vector"]
    if length is None:
        length = default["length"]
    if width is None:
        width = default["width"]
    if color is None:
        color = default["color"][X]
    if opacity is None:
        opacity = default["opacity"]

    if isinstance(samb, np.ndarray):
        samb = samb.astype(float)

    if label is None:
        label = [""] * len(site)

    for i, (no, v, s) in enumerate(zip(label, samb, site)):
        if np.linalg.norm(v) < CHOP:
            continue
        lbl = f"V{i+1}:{no}".replace(" ", "")
        pvw.add_vector(
            direction=v,
            length=-length,
            width=width,
            color=color,
            opacity=opacity,
            cartesian=cartesian,
            position=s,
            name=name,
            label=lbl,
        )


# ==================================================
def plot_orbital_cluster(dialog, site, samb, X="Q", wp=None, label=None, size=None, color=None, opacity=None, name=None):
    pvw = dialog._pvw

    if name is None:
        if wp is None:
            cnt = dialog._set_counter("orbital")
            name = f"orbital{cnt}"
        else:
            cnt = dialog._set_counter(wp)
            name = f"{wp}({cnt})"

    default = detail["orbital"]
    if size is None:
        size = default["size"]
    if color is None:
        color = default["color"][X]
    if opacity is None:
        opacity = default["opacity"]

    if label is None:
        label = [""] * len(site)

    for i, (no, v, s) in enumerate(zip(label, samb, site)):
        if v == 0:
            continue
        lbl = f"O{i+1}:{no}".replace(" ", "")
        pvw.add_orbital(shape=v, surface=v, size=-size, color=color, opacity=opacity, position=s, name=name, label=lbl)
