"""
Utility for parsing material files.

This module contains utilities for parsing.
"""

import numpy as np
import copy
from pymatgen.core import Structure
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
from pymatgen.analysis.graphs import StructureGraph
from pymatgen.analysis.local_env import MinimumDistanceNN
from pymatgen.io.cif import CifParser
from qtdraw.core.pyvista_widget_setting import DIGIT, default_preference, default_status
from qtdraw.parser.element import element_color
from qtdraw.core.pyvista_widget_setting import widget_detail as detail
from qtdraw.parser.vesta import parse_vesta, create_structure_vesta
from qtdraw.parser.data_group import _data_no_space_group
from qtdraw import __version__


# ==================================================
def get_model_cell(graph):
    """
    Get model and cell.

    Args:
        graph (StructureGraph): pymatgen StructureGraph object.

    Returns:
        - (str) -- name of model.
        - (dict) -- unit-cell info.
    """
    name = graph.structure.composition.reduced_formula

    lat = graph.structure.lattice
    cell = {
        "a": np.round(lat.a, DIGIT),
        "b": np.round(lat.b, DIGIT),
        "c": np.round(lat.c, DIGIT),
        "alpha": np.round(lat.alpha, DIGIT),
        "beta": np.round(lat.beta, DIGIT),
        "gamma": np.round(lat.gamma, DIGIT),
    }

    return name, cell


# ==================================================
def get_site_info(graph):
    """
    Get site information.

    Args:
        graph (StructureGraph): pymatgen StructureGraph object.

    Returns:
        - (list) -- site_info. (name, label, element, frac_coords, radius).
    """
    structure = graph.structure
    eq_sites = structure.equivalent_sites

    # grouping equivalent sites.
    MIN_RADIUS = 0.25

    site_info = []

    element0 = ""
    group_index = 0
    for group in eq_sites:
        group_index += 1
        for site_index, site in enumerate(group):
            element = site.species.elements[0].symbol
            if element != element0:
                element0 = element
                group_index = 0
            symbols = ''.join([el.symbol for el in site.species.elements])
            name = f"{symbols}{group_index+1}"
            label = f"{name}_{site_index+1}"
            frac_coords = site.frac_coords

            radius = 0.0
            for el, occu in site.species.items():
                r = el.atomic_radius or MIN_RADIUS
                radius += occu * r

            site_info.append((
                name,
                label,
                element,
                frac_coords.round(DIGIT),
                round(radius,DIGIT-2)
            ))

    return site_info


# ==================================================
def get_bond_info(graph, site_info):
    """
    Get bond information.

    Args:
        graph (StructureGraph): pymatgen StructureGraph object.
        site_info (list): site info.

    Returns:
        - (list) -- bond_info. (name, label, center, vector, tail_element, head_element).
    """
    adjacency = graph.as_dict()["graphs"]["adjacency"]

    dbonds = {}
    for tail, tail_adjacency in zip(site_info, adjacency):
        t_name, _, t_element, t_pos, _ = tail
        for head_info in tail_adjacency:
            h_name, _, h_element, h_pos, _ = site_info[head_info["id"]]
            h_pos = np.array(head_info["to_jimage"]) + h_pos
            center = ((t_pos + h_pos) / 2).round(DIGIT)
            vector = (h_pos - t_pos).round(DIGIT)
            key = t_name + "-" + h_name
            dbonds[key] = dbonds.get(key, []) + [(center, vector, t_element, h_element)]

    bond_info = []
    for name, v in dbonds.items():
        for no, (center, vector, t_element, h_element) in enumerate(v):
            label = name + "_" + str(no + 1)
            bond_info.append((name, label, center, vector, t_element, h_element))

    return bond_info


# ==================================================
def draw_site_bond(widget, name, site_info, bond_info):
    """
    Draw site and bond.

    Args:
        widget (PyVistaWidget): widget.
        name (str): name of model.
        site_info (list): site info.
        bond_info (list): bond info.
    """
    site_scale = detail["site_scale"]
    bond_scale = detail["bond_scale"]
    color_scheme = widget._preference["general"]["color_scheme"]
    default_color = "silver"

    # draw sites.
    widget._data["site"].block_update_widget(True)
    for name, label, element, frac_coords, radius in site_info:
        color = element_color[color_scheme].get(element, default_color)
        widget.add_site(position=str(frac_coords.tolist()), name=name, label=label, color=color, size=site_scale * radius)
    widget._data["site"].block_update_widget(False)

    # draw bonds.
    widget._data["bond"].block_update_widget(True)
    for name, label, center, vector, tail_element, head_element in bond_info:
        tail_color = element_color[color_scheme].get(tail_element, default_color)
        head_color = element_color[color_scheme].get(head_element, default_color)
        widget.add_bond(
            position=str(center.tolist()),
            direction=str(vector.tolist()),
            color=tail_color,
            color2=head_color,
            name=name,
            label=label,
            width=bond_scale,
        )
    widget._data["bond"].block_update_widget(False)


# ==================================================
def parse_material(filename):
    """
    Parse material file.

    Args:
        filename (str): filename.

    Returns:
        - (dict) -- data for PyVistaWidget.
        - (list) -- site info. to draw.
        - (list) -- bond info. to draw.
        - (Structure) -- symmetrized structure.
    """
    if filename.endswith(".vesta"):
        vesta_dict = parse_vesta(filename)
        structure = create_structure_vesta(vesta_dict)
    elif filename.endswith(".cif"):
        parser = CifParser(filename)
        structure = parser.parse_structures(primitive=False, symmetrized=False)[0]
    elif filename.endswith(".xsf"):
        structure = Structure.from_file(filename)
        sga = SpacegroupAnalyzer(structure)
        structure = sga.get_refined_structure()
    else:
        structure = Structure.from_file(filename)

    sga = SpacegroupAnalyzer(structure)
    symmetrized = sga.get_symmetrized_structure()
    sg_no = sga.get_space_group_number()
    env = MinimumDistanceNN()
    graph = StructureGraph.from_local_env_strategy(symmetrized, env)

    name, cell = get_model_cell(graph)
    crystal = sga.get_crystal_system()

    group_name = _data_no_space_group[sg_no]
    multipie = {"group": {"group": group_name}}

    status = copy.deepcopy(default_status)
    status.update({"model": name, "crystal": crystal, "cell": cell, "clip": False, "multipie": multipie})
    preference = copy.deepcopy(default_preference)
    preference["axis"]["label"] = "[a,b,c]"
    preference["label"]["default_check"] = False
    all_data = {"version": __version__, "status": status, "preference": preference}

    site_info = get_site_info(graph)
    bond_info = get_bond_info(graph, site_info)

    return all_data, site_info, bond_info, symmetrized
