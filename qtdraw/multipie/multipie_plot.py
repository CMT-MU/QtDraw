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
    group = dialog.group()
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
    group = dialog.group()
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
    group = dialog.group()
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
                length=length,
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
                    length=length,
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
    group = dialog.group()
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
            pvw.add_orbital(shape=v, surface=v, size=size, color=color, opacity=opacity, position=s, name=name, label=label)
    else:
        no = -1
        for vl, s, ml in zip(multipoles, sites, mp):
            for v, m in zip(vl, ml):
                no += 1
                if v == 0:
                    continue
                label = f"O{no+1}: " + f"[{m}]".replace(" ", "")
                pvw.add_orbital(shape=v, surface=v, size=size, color=color, opacity=opacity, position=s, name=name, label=label)
