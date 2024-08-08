"""
Convert QtDraw to version 2.
"""

import click
from pathlib import Path
from qtdraw.core.pyvista_widget import convert_qtdraw_v2


# ================================================== execute converter
@click.command()
@click.argument("filename", nargs=-1)
def cmd(filename):
    """
    Convert QtDraw to version 2.

        filename : `.qtdw` file.
    """
    n = len(filename)
    if n != 1:
        exit()

    filename = Path(filename[0]).resolve()
    convert_qtdraw_v2(filename)
