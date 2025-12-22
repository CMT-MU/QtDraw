import numpy as np

from qtdraw.multipie.multipie_setting import setting_detail as detail

CHOP = 1e-6


# ==================================================
def plot_cell_site(dialog, site, size=None, color=None, opacity=None, name=None):
    """
    Plot cell site.

    Args:
            dialog (MultiPieDialog): multipie dialog.
            site (str or ndarray): representative site (fractional, conventional).
            size (float, optional): size [default: 0.05].
            color (str, optional): color [default: silver].
            opacity (float, optional): opacity [default: 1.0].
            name (str, optional): plot name.
    """
    group = dialog.group
    pvw = dialog._pvw

    if name is None:
        cnt = dialog._set_counter("site")
        name = f"site{cnt}"

    default = detail["site"]
    if size is None:
        size = default["size"]
    if color is None:
        color = default["color"]
    if opacity is None:
        opacity = default["opacity"]

    sites, mp = group.create_cell_site(site)

    for no, (pt, m) in enumerate(zip(sites, mp)):
        label = f"S{no+1}: " + f"{m}".replace(" ", "")
        pvw.add_site(position=pt, name=name, label=label, size=size, color=color, opacity=opacity)


# ==================================================
def plot_cell_bond(dialog, bond, width=None, color=None, color2=None, opacity=None, name=None):
    """
    Plot cell bond.

    Args:
            dialog (MultiPieDialog): multipie dialog.
            bond (str or ndarray): representative bond (fractional, conventional).
            width (float, optional): width [default: 0.01].
            color (str, optional): color [default: silver].
            color2 (str, optional): color for directional bond [default: iron].
            opacity (float, optional): opacity [default: 1.0].
            name (str, optional): plot name.
    """
    group = dialog.group
    pvw = dialog._pvw

    if name is None:
        cnt = dialog._set_counter("bond")
        name = f"bond{cnt}"

    default = detail["bond"]
    if width is None:
        width = default["width"]
    if color is None:
        color = default["color1"]
    if color2 is None:
        color2 = default["color2"]
    if opacity is None:
        opacity = default["opacity"]

    bonds, mp = group.create_cell_bond(bond)
    directional = not any(x < 0 for x in sum(mp, []))
    if not directional:
        color2 = color
    for no, (b, m) in enumerate(zip(bonds, mp)):
        v, c = b[0:3], b[3:6]
        label = f"B{no+1}: " + f"{m}".replace(" ", "")
        pvw.add_bond(direction=v, position=c, width=width, color=color, color2=color2, opacity=opacity, name=name, label=label)


# ==================================================
def plot_cell_vector(
    dialog, vector, X="Q", length=None, width=None, color=None, opacity=None, average=True, cartesian=False, name=None
):
    """
    Plot cell vector.

    Args:
        dialog (MultiPieDialog): multipie dialog.
            vector (str): representative vector (fractional/cartesian) # site/bond (fractional, conventional).
            X (str, optional): type, "Q/G/T/M".
            length (float, optional): length [default: 0.3].
            width (float, optional): width [default: 0.02].
            color (_type_, optional): color [default: orange/yellowgreen/hotpink/lightskyblue for Q/G/T/M].
            opacity (float, optional): opacity [default: 1.0].
            average (bool, optional): average at each site ?
            cartesian (bool, optional): vector in cartesian coordinate ?
            name (str, optional): plot name.
    """
    group = dialog.group
    pvw = dialog._pvw

    if name is None:
        cnt = dialog._set_counter("vector")
        name = f"vector{cnt}"

    default = detail["vector"]
    if length is None:
        length = default["length"]
    if width is None:
        width = default["width"]
    if color is None:
        color = default["color"][X]
    if opacity is None:
        opacity = default["opacity"]

    vectors, sites, mp = group.create_cell_vector(vector, X, average, cartesian)
    vectors = vectors.astype(float)

    if average:
        for no, (v, s, m) in enumerate(zip(vectors, sites, mp)):
            if np.linalg.norm(v) < CHOP:
                continue
            label = f"V{no+1}: " + f"{m}".replace(" ", "")
            pvw.add_vector(
                direction=v,
                length=-length,
                width=width,
                color=color,
                opacity=opacity,
                cartesian=cartesian,
                position=s,
                name=name,
                label=label,
            )
    else:
        no = -1
        for vl, s, ml in zip(vectors, sites, mp):
            for v, m in zip(vl, ml):
                no += 1
                if np.linalg.norm(v) < CHOP:
                    continue
                label = f"V{no+1}: " + f"[{m}]".replace(" ", "")
                pvw.add_vector(
                    direction=v,
                    length=-length,
                    width=width,
                    color=color,
                    opacity=opacity,
                    cartesian=cartesian,
                    position=s,
                    name=name,
                    label=label,
                )


# ==================================================
def plot_cell_multipole(dialog, multipole, X="Q", size=None, color=None, opacity=None, average=True, name=None):
    """
    Plot cell multipole.

    Args:
        dialog (MultiPieDialog): multipie dialog.
            multipole (str): representative multipole (cartesian) # site/bond (fractional, conventional).
            X (str, optional): type, "Q/G/T/M".
            size (float, optional): size [default: 0.2].
            color (_type_, optional): color [default: Wistia/PiYG/coolwarm/GnBu for Q/G/T/M].
            opacity (float, optional): opacity [default: 1.0].
            average (bool, optional): average at each site ?
            name (str, optional): plot name.
    """
    group = dialog.group
    pvw = dialog._pvw

    if name is None:
        cnt = dialog._set_counter("orbital")
        name = f"orbital{cnt}"

    default = detail["multipole"]
    if size is None:
        size = default["size"]
    if color is None:
        color = default["color"][X]
    if opacity is None:
        opacity = default["opacity"]

    multipoles, sites, mp = group.create_cell_multipole(multipole, X, average)

    if average:
        for no, (v, s, m) in enumerate(zip(multipoles, sites, mp)):
            if v == 0:
                continue
            label = f"O{no+1}: " + f"{m}".replace(" ", "")
            pvw.add_orbital(shape=v, surface=v, size=-size, color=color, opacity=opacity, position=s, name=name, label=label)
    else:
        no = -1
        for vl, s, ml in zip(multipoles, sites, mp):
            for v, m in zip(vl, ml):
                no += 1
                if v == 0:
                    continue
                label = f"O{no+1}: " + f"[{m}]".replace(" ", "")
                pvw.add_orbital(shape=v, surface=v, size=-size, color=color, opacity=opacity, position=s, name=name, label=label)


# ==================================================
def plot_bond_definition(
    dialog,
    bonds,
    wp,
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

    opt = opacity
    for no, b in enumerate(bonds):
        v, c = b[0:3], b[3:6]
        pvw.add_bond(
            position=c,
            direction=v,
            color=color,
            color2=color,
            width=width,
            cartesian=False,
            opacity=opt,
            label=f"b{no+1}",
            name=name,
        )
        acolor = arrow_color_rep if rep and no == 0 else arrow_color
        pvw.add_vector(
            position=c, direction=v, length=-length, color=acolor, width=0.01, cartesian=False, label=f"b{no+1}", name=name
        )


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

    for s, v in zip(site, samb):
        if v > 0:
            c = color_pos
        elif v < 0:
            c = color_neg
        else:
            c = color
            v = zero_size
        pvw.add_site(position=s, size=size_ratio * abs(v), color=c, name=name, label=label)


# ==================================================
def plot_bond_cluster(
    dialog,
    bond,
    samb,
    wp,
    sym=True,
    label=None,
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

    if sym:
        for b, h in zip(bond, samb):
            v, c = b[0:3], b[3:6]
            if abs(h) < CHOP:
                pvw.add_bond(
                    position=c, direction=v, color=color, color2=color, width=width, cartesian=False, name=name, label=label
                )
            else:
                cl = color_neg if h < 0 else color_pos
                width = width_ratio * abs(h)
                pvw.add_bond(position=c, direction=v, color=cl, color2=cl, width=width, cartesian=False, name=name, label=label)
    else:
        for b, h in zip(bond, samb):
            v, c = b[0:3], b[3:6]
            if abs(h) < CHOP:
                pvw.add_bond(
                    position=c,
                    direction=arrow_ratio * v,
                    color=color,
                    color2=color,
                    width=width,
                    cartesian=False,
                    name=name,
                    label=label,
                )
            else:
                if h < 0:
                    v = -v
                cl = color_pos
                width = width_ratio * abs(h)
                pvw.add_vector(
                    position=c, direction=v, length=-arrow_ratio, color=cl, width=width, cartesian=False, name=name, label=label
                )


# ==================================================
def plot_vector_cluster(dialog, site, samb, X="Q", length=None, width=None, color=None, opacity=None, name=None):
    pvw = dialog._pvw

    if name is None:
        cnt = dialog._set_counter("vector")
        name = f"vector{cnt}"

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

    for no, (v, s) in enumerate(zip(samb, site)):
        if np.linalg.norm(v) < CHOP:
            continue
        label = f"V{no+1}:"
        pvw.add_vector(
            direction=v,
            length=-length,
            width=width,
            color=color,
            opacity=opacity,
            cartesian=True,
            position=s,
            name=name,
            label=label,
        )


# ==================================================
def plot_orbital_cluster(dialog, site, samb, X="Q", size=None, color=None, opacity=None, name=None):
    pvw = dialog._pvw

    if name is None:
        cnt = dialog._set_counter("orbital")
        name = f"orbital{cnt}"

    default = detail["multipole"]
    if size is None:
        size = default["size"]
    if color is None:
        color = default["color"][X]
    if opacity is None:
        opacity = default["opacity"]

    for no, (v, s) in enumerate(zip(samb, site)):
        if v == 0:
            continue
        label = f"O{no+1}:"
        pvw.add_orbital(shape=v, surface=v, size=-size, color=color, opacity=opacity, position=s, name=name, label=label)
