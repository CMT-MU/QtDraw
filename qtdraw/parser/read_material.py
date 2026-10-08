"""
Simple parser for CIF, XSF, and VESTA.

This module contains the parser.
"""

import numpy as np

from qtdraw.parser.util_parser import parse_material, draw_site_bond
from qtdraw.parser.xsf import extract_data_xsf


# ==================================================
def parse_draw(filename):
    """
    Parse CIF, XSF, VESTA file without drawing.

    Args:
        filename (str): filename.

    Returns:
        - (dict) -- all data.
        - (dict) -- material info. to draw.
    """
    all_data, site_info, bond_info, symmetrized = parse_material(filename)
    material = {"site": site_info, "bond": bond_info, "symmetrized": symmetrized, "isosurface": None}

    if filename.endswith(".xsf"):
        # determine color_range and value.
        data = np.array(extract_data_xsf(filename)["data"])
        d_max = float(data.max())
        d_min = float(data.min())
        d_max = 1.1 * d_max if d_max > 0.0 else 0.9 * d_max
        d_min = 0.9 * d_min if d_min > 0.0 else 1.1 * d_min
        val = 0.5 * (d_max + d_min)
        material["isosurface"] = {"color_range": [d_min, d_max], "value": [val]}

    return all_data, material


# ==================================================
def draw(widget, filename, all_data, material):
    """
    Draw parsed CIF, XSF, VESTA data.

    Args:
        widget (PyVistaWidget): PyVista widget.
        filename (str): filename.
        all_data (dict): all data.
        material (dict): material info. to draw.
    """
    widget.write_info("* " + str(material["symmetrized"]))

    name = all_data["status"]["model"]
    draw_site_bond(widget, name, material["site"], material["bond"])

    iso = material["isosurface"]
    if iso is not None:
        widget.add_isosurface(data=filename, color="Pastel1", surface="phase", **iso)


# ==================================================
def read_draw(filename, widget):
    """
    Read and draw CIF, XSF, VESTA file.

    Args:
        filename (str): filename.
        widget (PyVistaWidget): PyVista widget.

    Returns:
        - (dict) -- all data.
    """
    all_data, material = parse_draw(filename)
    draw(widget, filename, all_data, material)

    return all_data
