from pymatgen.io.cif import CifParser
from pymatgen.analysis.graphs import StructureGraph
from pymatgen.analysis.local_env import MinimumDistanceNN
import numpy as np
from qtdraw.parser.element import element_color
from qtdraw.core.setting import rcParams


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
    color_scheme = rcParams["plotter.color_scheme"]

    parser = CifParser(file)
    structure = parser.get_structures(primitive=False)[0]
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

    sites0 = [
        (
            i.label,
            i.frac_coords.round(digit).tolist(),
            float(list(i.species)[0].atomic_radius),
            element_color[color_scheme][i.species_string],
        )
        for i in graph.structure.sites
    ]
    adjacency = graph.as_dict()["graphs"]["adjacency"]
    bonds0 = []
    for tail_site, ad in zip(sites0, adjacency):
        tail_lbl = tail_site[0]
        tail = np.array(tail_site[1])
        tail_c = tail_site[3]
        for i in ad:
            head_site = sites0[i["id"]]
            head_lbl = head_site[0]
            head = np.array(i["to_jimage"]) + np.array(head_site[1])
            head_c = head_site[3]
            c = str(((tail + head) / 2).tolist())
            v = str((head - tail).tolist())
            b = (tail_lbl, head_lbl, c, v, tail_c, head_c)
            bonds0.append(b)

    sites = {}
    for lbl, pos, r, c in sites0:
        sites[lbl] = sites.get(lbl, []) + [(str(pos), r, c)]

    bonds = {}
    for tl, hl, c, v, tc, hc in bonds0:
        lbl = (tl, hl)
        bonds[lbl] = bonds.get(lbl, []) + [(c, v, tc, hc)]

    return name, lattice, volume, sites, bonds


# ==================================================
def create_qtdraw_dict(qtdraw, name, lattice, volume, sites, bonds):
    """
    create QtDraw file.

    Args:
        name (str): name of model.
        lattice (dict): cell info.
        volume (float): cell volume.
        sites (dict): sites.
        bonds (dict): bonds.
    """
    qtdraw._init_setting(model=name, cell=lattice, axis_type="abc", clip=False)
    qtdraw._remove_all_actor()
    qtdraw._init_all()

    scale = volume ** (1 / 3)
    site_scale = rcParams["plotter.site_scale"]
    bond_scale = rcParams["plotter.bond_scale"]

    # plot sites.
    for lbl, lst in sites.items():
        for pno, (p, size, color) in enumerate(lst):
            label = f"{lbl}_{pno+1}"
            qtdraw.plot_site(p, name=lbl, label=label, color=color, size=site_scale * size * scale)

    # plot bonds.
    for lbl, lst in bonds.items():
        for pno, (c, v, tc, hc) in enumerate(lst):
            lbl1 = lbl[0] + "-" + lbl[1]
            label = lbl1 + "_" + str(pno + 1)
            qtdraw.plot_bond(c, v, color=tc, color2=hc, name=lbl1, label=label, width=bond_scale * scale)

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
