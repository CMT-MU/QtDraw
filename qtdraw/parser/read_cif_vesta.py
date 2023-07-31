import numpy as np
from pymatgen.io.cif import CifParser
from pymatgen.analysis.graphs import StructureGraph
from pymatgen.analysis.local_env import MinimumDistanceNN
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
from pymatgen.core.periodic_table import Element
from qtdraw.parser.element import element_color
from qtdraw.core.setting import rcParams
from qtdraw.parser.vesta import parse_vesta, create_vesta_graph

color_scheme = rcParams["plotter.color_scheme"]
digit = 6


# ==================================================
def get_graph(file):
    """
    get symmetrized structure graph.

    Args:
        file (str): file name.

    Returns:
        StructureGraph: pymatgen StructureGraph object.
    """
    parser = CifParser(file)
    structure = parser.get_structures(primitive=False, symmetrized=False)[0]
    sga = SpacegroupAnalyzer(structure)
    symmetrized = sga.get_symmetrized_structure()
    env = MinimumDistanceNN()
    graph = StructureGraph.with_local_env_strategy(symmetrized, env)

    return graph


# ==================================================
def get_model_cell(graph):
    """
    get model and cell.

    Args:
        graph (StructureGraph): pymatgen StructureGraph object.

    Returns: tuple.
        - str: name of model.
        - dict: unit-cell info.
        - float: unit-cell volume.
    """
    name = graph.structure.composition.reduced_formula

    lat = graph.structure.lattice
    cell = {
        "a": np.round(lat.a, digit),
        "b": np.round(lat.b, digit),
        "c": np.round(lat.c, digit),
        "alpha": np.round(lat.alpha, digit),
        "beta": np.round(lat.beta, digit),
        "gamma": np.round(lat.gamma, digit),
    }
    volume = lat.volume

    return name, cell, volume


# ==================================================
def get_site_info(graph):
    """
    get site information.

    Args:
        graph (StructureGraph): pymatgen StructureGraph object.

    Returns:
        list: site_info. (name, label, element, frac_coords, radius, color).
    """
    structure = graph.structure
    eq_sites = structure.equivalent_sites

    # grouping equivalent sites.
    dsites = {}
    for es in eq_sites:
        el = es[0].specie
        if type(el) != type(Element):
            el = str(el).replace("0+", "")
        else:
            el = el.symbol
        dsites[el] = dsites.get(el, []) + [es]

    site_info = []
    for name, v in dsites.items():
        for el_no, sl in enumerate(v):
            el_name = name + str(el_no + 1)
            for s_no, s in enumerate(sl):
                s_name = el_name + "_" + str(s_no + 1)
                frac_coords = s.frac_coords.round(digit)
                if name in element_color[color_scheme].keys():
                    radius = float(s.specie.atomic_radius)
                    color = element_color[color_scheme][name]
                else:
                    radius = 1.0
                    color = "silver"
                site_info.append((el_name, s_name, name, frac_coords, radius, color))

    return site_info


# ==================================================
def get_bond_info(graph, site_info):
    """
    get bond information.

    Args:
        graph (StructureGraph): pymatgen StructureGraph object.
        site_info (list): site info.

    Returns:
        list: bond_info. (name, label, center, vector, tail_color, head_color).
    """
    adjacency = graph.as_dict()["graphs"]["adjacency"]

    dbonds = {}
    for tail, tail_adjacency in zip(site_info, adjacency):
        t_name, _, _, t_pos, _, t_c = tail
        for head_info in tail_adjacency:
            h_name, _, _, h_pos, _, h_c = site_info[head_info["id"]]
            h_pos = np.array(head_info["to_jimage"]) + h_pos
            center = ((t_pos + h_pos) / 2).round(digit)
            vector = (h_pos - t_pos).round(digit)
            key = t_name + "-" + h_name
            dbonds[key] = dbonds.get(key, []) + [(center, vector, t_c, h_c)]

    bond_info = []
    for name, v in dbonds.items():
        for no, (center, vector, t_c, h_c) in enumerate(v):
            label = name + "_" + str(no + 1)
            bond_info.append((name, label, center, vector, t_c, h_c))

    return bond_info


# ==================================================
def plot_site_bond(qtdraw, name, cell, volume, site_info, bond_info):
    """
    plot site and bond.

    Args:
        name (str): name of model.
        cell (dict): unit-cell info.
        volume (float): unit-cell volume.
        site_info (list): site info.
        bond_info (list): bond info.
    """
    qtdraw._init_setting(model=name, cell=cell, axis_type="abc", clip=False)
    qtdraw._remove_all_actor()
    qtdraw._init_all()

    scale = volume ** (1 / 3)
    site_scale = rcParams["plotter.site_scale"]
    bond_scale = rcParams["plotter.bond_scale"]

    # plot sites.
    for name, label, _, frac_coords, radius, color in site_info:
        qtdraw.plot_site(str(frac_coords.tolist()), name=name, label=label, color=color, size=site_scale * radius * scale)

    # plot bonds.
    for name, label, center, vector, tail_color, head_color in bond_info:
        qtdraw.plot_bond(
            str(center.tolist()),
            str(vector.tolist()),
            color=tail_color,
            color2=head_color,
            name=name,
            label=label,
            width=bond_scale * scale,
        )

    qtdraw._plot_all_object()
    qtdraw.set_view()


# ==================================================
def plot_cif(qtdraw, filename):
    """
    read and plot CIF file.

    Args:
        filename (str): filename.
    """
    graph = get_graph(filename)
    name, cell, volume = get_model_cell(graph)
    site_info = get_site_info(graph)
    bond_info = get_bond_info(graph, site_info)
    plot_site_bond(qtdraw, name, cell, volume, site_info, bond_info)


# ==================================================
def plot_vesta(qtdraw, filename):
    """
    read and plot VESTA file.

    Args:
        filename (str): filename.
    """
    vesta_dict = parse_vesta(filename)
    graph = create_vesta_graph(vesta_dict)

    name, cell, volume = get_model_cell(graph)
    site_info = get_site_info(graph)
    bond_info = get_bond_info(graph, site_info)
    plot_site_bond(qtdraw, name, cell, volume, site_info, bond_info)
