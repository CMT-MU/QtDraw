import numpy as np
import sympy as sp
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
        NSArray: site (bond center), or None if invalid.
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
def create_combined(group, pg, site_bond, rank, head, ret_bond=False):
    """
    create SAMB.

    Args:
        group (Group): space/point group.
        pg (PointGroup): associated point group.
        site_bond (str): site or bond.
        rank (str): harmonics rank.
        head (str): harmonics type.
        ret_bond (bool, optional): return bond ?

    Returns:
        tuple:
            - dict: cluster SAMB.
            - NSArray: site or bond.
            - dict: combined SAMB.
    """
    t_rev = {"Q": "Q", "G": "G", "T": "Q", "M": "G"}

    if site_bond.style == "vector":
        c_samb, site = group.site_cluster_samb(site_bond)
    else:
        c_samb, bond = group.bond_cluster_samb(site_bond)
        if ret_bond:
            site = bond
        else:
            site = bond.convert_bond("bond")[1]

    x_tag = pg.harmonics.key_list().select(rank=int(rank), head=t_rev[head])
    if head in ["T", "M"]:
        x_tag = [tag.reverse_t_type() for tag in x_tag]
    y_tag = list(c_samb.keys())

    z_samb_all = group.z_samb(x_tag, y_tag)
    z_samb = {"Q": [], "G": [], "T": [], "M": []}
    for tag, c in z_samb_all.items():
        tag_str = combined_format(tag)
        z_samb[tag[0].head].append((tag_str, c))
    for k in z_samb.keys():
        z_samb[k] = list(sorted(z_samb[k], key=lambda i: i[0]))

    return c_samb, site, z_samb


# ==================================================
def create_samb_object(z_samb, site, c_samb, z_head, irrep, pg, v, t_odd):
    """
    create SAMB object.

    Args:
        z_samb (dict): combined SAMB.
        site (NSArray): site.
        c_samb (dict): cluster SAMB.
        z_head (str): multipole type.
        irrep (int): irrep. index.
        pg (PointGroup): point group.
        v (NSArray): vector variable.
        t_odd (bool): magnetic bond ?

    Returns:
        _type_: _description_
    """
    obj = NSArray.zeros(len(site), "vector")
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
    check form of linear combination.

    Args:
        z_samb (dict): combined SAMB.
        form (str): expression of linear combination.
        head (str): multipole type.

    Returns:
        tuple:
            - str: expression of linear combination (lower case).
            - set: used variables.
            - bool: magnetic bond ?
    """
    irrep_num = {i: len(z_samb[i]) for i in ["Q", "G", "T", "M"]}
    var_e = set([f"q{i+1:02d}" for i in range(irrep_num["Q"])] + [f"g{i+1:02d}" for i in range(irrep_num["G"])])
    var_m = set([f"t{i+1:02d}" for i in range(irrep_num["T"])] + [f"m{i+1:02d}" for i in range(irrep_num["M"])])

    form = form.lower()
    form_variable = set(NSArray(form).variable())

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
    create formatted combined SAMB.

    Args:
        tag_list (tuple): (Z,X,Y) tag.

    Returns:
        str: formatted combined SAMB.
    """
    z_tag, x_tag, y_tag = tag_list
    t1 = (",".join(str(x_tag).split(",")[:-1]) + ")").replace("h", "a")
    t2 = ",".join(str(y_tag).split(",")[:-1]) + ")"
    tag = f"{z_tag} = {t1} x {t2}"

    return tag


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


# ==================================================
def plot_site_cluster(qtdraw, site, obj, label, pset):
    """
    plot site cluster SAMB.

    Args:
        qtdraw (QtDraw): QtDraw.
        site (NSArray): equivalent sites.
        obj (NSArray): SAMB weight.
        label (str): label.
        pset (NSArray): plus set.
    """
    color = []
    for w in obj:
        if w > 0:
            c = "salmon"
        elif w < 0:
            c = "aqua"
        else:
            c = "silver"
        color.append(c)

    obj /= np.abs(obj).max()

    qtdraw._close_dialog()
    name = "Z_" + qtdraw._get_name("site")
    for p in pset:
        for s, w, cl in zip(site, obj, color):
            s = (s + p).shift()
            if cl == "silver":
                w = 1
            qtdraw.plot_site(
                s,
                size=abs(w),
                color=cl,
                name=name,
                label=label,
                show_lbl=rcParams["show_label"],
            )
    qtdraw._plot_all_object()


# ==================================================
def plot_bond_cluster(qtdraw, bond, obj, label, pset, z_head):
    """
    plot bond cluster SAMB.

    Args:
        qtdraw (QtDraw): QtDraw.
        bond (NSArray): equivalent bonds.
        obj (NSArray): SAMB weight.
        label (str): label.
        pset (NSArray): plus set.
        z_head (str): multipole type.
    """
    color = []
    if z_head == "Q":
        for w in obj:
            if w > 0:
                c = "salmon"
            elif w < 0:
                c = "aqua"
            else:
                c = "silver"
            color.append(c)
    else:
        for w in obj:
            if w == 0:
                c = "silver"
            else:
                c = "salmon"
            color.append(c)

    obj /= np.abs(obj).max()

    qtdraw._close_dialog()
    name = "Z_" + qtdraw._get_name("bond")
    if z_head == "Q":
        for p in pset:
            for s, w, cl in zip(bond, obj, color):
                v, c = s.convert_bond("bond")
                c = (c + p).shift()
                if cl == "silver":
                    w = 1
                qtdraw.plot_bond(
                    c,
                    v,
                    color=cl,
                    color2=cl,
                    width=abs(w),
                    name=name,
                    label=label,
                    show_lbl=rcParams["show_label"],
                )
    else:
        for p in pset:
            for s, w, cl in zip(bond, obj, color):
                v, c = s.convert_bond("bond")
                c = (c + p).shift()
                if cl == "silver":
                    w = 1
                    qtdraw.plot_bond(
                        c,
                        v,
                        color=cl,
                        color2=cl,
                        width=abs(w),
                        name=name,
                        label=label,
                        show_lbl=rcParams["show_label"],
                    )
                else:
                    v = v.transform(qtdraw._A)
                    if w < 0:
                        v = -v
                    norm = v.norm() * 0.7
                    qtdraw.plot_vector(
                        c,
                        v,
                        color=cl,
                        width=abs(w),
                        length=norm,
                        offset=-0.5,
                        name=name,
                        label=label,
                        show_lbl=rcParams["show_label"],
                    )

    qtdraw._plot_all_object()


# ==================================================
def plot_vector_cluster(qtdraw, site, obj, label, pset, head, v):
    """
    plot vector cluster SAMB.

    Args:
        qtdraw (QtDraw): QtDraw.
        site (NSArray): equivalent sites.
        obj (NSArray): SAMB weight.
        label (str): label.
        pset (NSArray): plus set.
        head (str): multipole type.
        v (NSArray): vector variable.
    """
    rep = {v[0]: sp.Matrix([1, 0, 0]), v[1]: sp.Matrix([0, 1, 0]), v[2]: sp.Matrix([0, 0, 1])}
    color = rcParams["vector_color_" + head]
    qtdraw._close_dialog()
    name = "Z_" + qtdraw._get_name("vector")

    for p in pset:
        for s, c in zip(site, obj):
            s = (s + p).shift()
            if c != 0:
                c = str(c.subs(rep).T[:])
                c = NSArray(c)
                d = c.norm()
                qtdraw.plot_vector(s, c, length=d, color=color, name=name, label=label, show_lbl=rcParams["show_label"])

    qtdraw._plot_all_object()


# ==================================================
def plot_orbital_cluster(qtdraw, site, obj, label, pset, head):
    """
    plot orbital cluster SAMB.

    Args:
        qtdraw (QtDraw): QtDraw.
        site (NSArray): equivalent sites.
        obj (NSArray): SAMB weight.
        label (str): label.
        pset (NSArray): plus set.
        head (str): multipole type.
    """
    color = rcParams["orbital_color_" + head]
    qtdraw._close_dialog()
    name = "Z_" + qtdraw._get_name("orbital")

    for p in pset:
        for s, orb in zip(site, obj):
            s = (s + p).shift()
            qtdraw.plot_orbital(
                s,
                orb,
                size=0.6,
                scale=False,
                color=color,
                name=name,
                label=label,
                show_lbl=rcParams["show_label"],
            )

    qtdraw._plot_all_object()
