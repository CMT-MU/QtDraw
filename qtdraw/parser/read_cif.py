from pymatgen.io.cif import CifParser
from pymatgen.analysis.graphs import StructureGraph
from pymatgen.analysis.local_env import MinimumDistanceNN
import numpy as np
from qtdraw.multipie.setting import default_style


# ==================================================
def get_structure(file):
    """
    get structure data.

    Args:
        file (str): filename.

    Returns: tuple.
        - str: name of model.
        - dict: cell info.
        - float: cell volume.
        - dict: sites, {name: [position]}.
        - dict: bonds, {(tail_name,head_name):[(center,vector)]}.
    """
    digit = 6

    parser = CifParser(file)
    structure = parser.get_structures()[0]
    env = MinimumDistanceNN()
    graph = StructureGraph.with_local_env_strategy(structure, env)

    name = graph.structure.composition.reduced_formula

    lat = structure.lattice
    lattice = {
        "a": np.round(lat.a, digit),
        "b": np.round(lat.b, digit),
        "c": np.round(lat.c, digit),
        "alpha": np.round(lat.alpha, digit),
        "beta": np.round(lat.beta, digit),
        "gamma": np.round(lat.gamma, digit),
    }
    volume = lat.volume

    sites0 = [(i.label, i.frac_coords.round(digit).tolist()) for i in graph.structure.sites]
    adjacency = graph.as_dict()["graphs"]["adjacency"]
    bonds0 = []
    for tail_site, ad in zip(sites0, adjacency):
        tail_lbl = tail_site[0]
        tail = np.array(tail_site[1])
        for i in ad:
            head_site = sites0[i["id"]]
            head_lbl = head_site[0]
            head = np.array(i["to_jimage"]) + np.array(head_site[1])
            b = (tail_lbl, head_lbl, str(((tail + head) / 2).tolist()), str((head - tail).tolist()))
            bonds0.append(b)

    sites = {}
    for lbl, pos in sites0:
        sites[lbl] = sites.get(lbl, []) + [str(pos)]

    bonds = {}
    for tl, hl, c, v in bonds0:
        lbl = (tl, hl)
        bonds[lbl] = bonds.get(lbl, []) + [(c, v)]

    return name, lattice, volume, sites, bonds


# ==================================================
def create_qtdraw_dict(qtdraw, name, lattice, volume, sites, bonds, scale=True):
    """
    create QtDraw file.

    Args:
        name (str): name of model.
        lattice (dict): cell info.
        volume (float): cell volume.
        sites (dict): sites.
        bonds (dict): bonds.
        scale (bool, optional): scale size ?
    """
    qtdraw._init_setting(model=name, cell=lattice, axis_type="abc", clip=True)
    qtdraw._remove_all_actor()
    qtdraw._init_all()

    if scale:
        scale = volume ** (1 / 3)
    else:
        scale = 1.0

    site_n = len(default_style["site"])

    # plot sites.
    for no, (lbl, pos) in enumerate(sites.items()):
        prop_no = min(no, site_n - 1)
        color, size, opacity = default_style["site"][prop_no]
        size *= scale
        for pno, p in enumerate(pos):
            label = f"{lbl}_{pno}"
            qtdraw.plot_site(p, name=lbl, label=label, color=color, size=size, opacity=opacity)

    # plot bonds.
    site_no = {lbl: no for no, lbl in enumerate(sites.keys())}

    for lbl, pos in bonds.items():
        t_no = site_no[lbl[0]]
        h_no = site_no[lbl[1]]
        t_prop_no = min(t_no, site_n - 1)
        h_prop_no = min(h_no, site_n - 1)
        _, width, opacity = default_style["bond"][0]
        width *= scale
        c1 = default_style["site"][t_prop_no][0]
        c2 = default_style["site"][h_prop_no][0]
        for pno, (c, v) in enumerate(pos):
            label = lbl[0] + "_" + lbl[1] + "_" + str(pno)
            qtdraw.plot_bond(c, v, color=c1, color2=c2, width=width, opacity=opacity, name=lbl, label=label)

    qtdraw._plot_all_object()
    qtdraw.set_view()


# ==================================================
def plot_cif(qtdraw, filename):
    """
    read and plot CIF file.

    Args:
        filename (str): filename.
    """
    name, lattice, volume, sites, bonds = get_structure(filename)
    create_qtdraw_dict(qtdraw, name, lattice, volume, sites, bonds)
