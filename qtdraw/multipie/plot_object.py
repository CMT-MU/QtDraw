from qtdraw.multipie.setting import rcParams
from gcoreutils.nsarray import NSArray
from multipie.model.material_model import MaterialModel


# ==================================================
def check_get_site(txt):
    """
    check and get site.

    Args:
        txt (str): site.

    Returns:
        NSArray: site or None if invalid.
    """
    try:
        site = NSArray(txt)
        if site.style != "vector":
            return None
    except Exception:
        return None

    return site


# ==================================================
def check_get_bond(txt):
    """
    check and get bond.

    Args:
        txt (str): bond.

    Returns:
        NSArray: bond or None if invalid.
    """
    try:
        bond = NSArray(txt)
        if bond.style not in ["bond", "bond_th", "bond_sv"]:
            return None
    except Exception:
        return None

    return bond


# ==================================================
def check_get_site_bond(txt):
    """
    check and get site (bond center) from site_bond.

    Args:
        txt (str): site_bond.

    Returns:
        NSArray: site (bond center) or None if invalid.
    """
    try:
        site = NSArray(txt)
        if site.style not in ["vector", "bond", "bond_th", "bond_sv"]:
            return None
        if site.style != "vector":
            site = site.convert_bond("bond")[1]
    except Exception:
        return None

    return site


# ==================================================
def plot_equivalent_site(qtdraw, site, n_pset):
    """
    plot equivalent sites.

    Args:
        qtdraw (QtDraw): QtDraw.
        site (NSArray): equivalent sites (including plus_set).
        n_pset (int): no. of plus set.
    """
    name0 = qtdraw._get_name("site")
    name0 = f"S{int(name0[1:])+1}"
    qtdraw._close_dialog()
    color = rcParams["site_color"]
    primitive_num = len(site) // n_pset

    for no, (s, mp) in enumerate(site.items()):
        mp = MaterialModel._mapping_str(mp)
        idx = no % primitive_num
        pset = no // primitive_num
        name = name0
        if n_pset > 1:
            name += f"({pset+1})"
        label = f"s{idx+1}:{mp}"
        qtdraw.plot_site(s, color=color, name=name, label=label, show_lbl=rcParams["show_label"])
    qtdraw._plot_all_object()


# ==================================================
def plot_equivalent_bond(qtdraw, bond, nondirectional, n_pset):
    """
    plot equivalent bonds.

    Args:
        qtdraw (QtDraw): QtDraw.
        bond (NSArray): equivalent bonds (including plus_set).
        nondirectional (bool): nondirectional ?
        n_pset (int): no. of plus set.
    """
    name0 = qtdraw._get_name("bond")
    name0 = f"B{int(name0[1:])+1}"
    qtdraw._close_dialog()
    color1 = rcParams["bond_color1"]
    if nondirectional:
        color2 = color1
    else:
        color2 = rcParams["bond_color2"]
    primitive_num = len(bond) // n_pset

    for no, (b, mp) in enumerate(bond.items()):
        b = NSArray(b)
        v, c = b.convert_bond("bond")
        mp = MaterialModel._mapping_str(mp)
        idx = no % primitive_num
        pset = no // primitive_num
        name = name0
        if n_pset > 1:
            name += f"({pset+1})"
        label = f"b{idx+1}:{mp}"
        qtdraw.plot_bond(c, v, color=color1, color2=color2, name=name, label=label, show_lbl=rcParams["show_label"])
    qtdraw._plot_all_object()


# ==================================================
def plot_vector_equivalent_site(qtdraw, site, vector, head, n_pset):
    """
    plot vectors at equivalent sites.

    Args:
        qtdraw (QtDraw): QtDraw.
        site (NSArray): equivalent sites (including plus_set).
        vector (NSArray): vector.
        head (str): multipole type.
        n_pset (int): no. of plus set.
    """
    name0 = qtdraw._get_name("vector")
    name0 = f"V{int(name0[3:])+1}"
    qtdraw._close_dialog()
    color = rcParams["vector_color_" + head]
    primitive_num = len(site) // n_pset

    for no, s in enumerate(site):
        idx = no % primitive_num
        pset = no // primitive_num
        name = name0
        if n_pset > 1:
            name += f"({pset+1})"
        label = f"v{idx+1}"
        qtdraw.plot_vector(s, vector, color=color, name=name, label=label, show_lbl=rcParams["show_label"])
    qtdraw._plot_all_object()


# ==================================================
def plot_orbital_equivalent_site(qtdraw, site, orbital, head, n_pset):
    """
    plot orbitals at equivalent sites.

    Args:
        qtdraw (QtDraw): QtDraw.
        site (NSArray): equivalent sites (including plus_set).
        orbital (str): orbital.
        head (str): multipole type.
        n_pset (int): no. of plus set.
    """
    name0 = qtdraw._get_name("orbital")
    name0 = f"O{int(name0[3:])+1}"
    qtdraw._close_dialog()
    color = rcParams["orbital_color_" + head]
    primitive_num = len(site) // n_pset

    for no, s in enumerate(site):
        idx = no % primitive_num
        pset = no // primitive_num
        name = name0
        if n_pset > 1:
            name += f"({pset+1})"
        label = f"o{idx+1}"
        qtdraw.plot_orbital(s, orbital, size=0.3, color=color, name=name, label=label, show_lbl=rcParams["show_label"])
    qtdraw._plot_all_object()
