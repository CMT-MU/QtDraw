"""
Simple parser for CIF, XSF, and VESTA.

This module contains the parser.
"""

from qtdraw.parser.util import parse_material, draw_site_bond


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
        pos = site_info[0][3]
        widget.add_isosurface(data=filename, position=pos, color="Pastel1", surface="phase")

    return all_data
