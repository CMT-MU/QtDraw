"""
Simple parser for CIF, XSF, and VESTA.

This module contains the parser.
"""

import numpy as np
from qtdraw.parser.util import parse_material, draw_site_bond
from qtdraw.parser.xsf import extract_data_xsf


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
    all_data, site_info, bond_info, symmetrized = parse_material(filename)
    widget.write_info("* " + str(symmetrized))

    name = all_data["status"]["model"]
    draw_site_bond(widget, name, site_info, bond_info)

    if filename.endswith(".xsf"):
        # determine color_range and value.
        data = np.array(extract_data_xsf(filename)["data"])
        d_max = float(data.max())
        d_min = float(data.min())
        d_max = 1.1 * d_max if d_max > 0.0 else 0.9 * d_max
        d_min = 0.9 * d_min if d_min > 0.0 else 1.1 * d_min
        val = 0.5 * (d_max + d_min)
        widget.add_isosurface(data=filename, color="Pastel1", surface="phase", color_range=[d_min, d_max], value=[val])

    return all_data
