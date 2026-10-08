"""
Execute QtDraw.
"""

import click
from qtdraw.core.qtdraw_app import QtDraw
from qtdraw.scripts.cli_util import resolve_file


# ================================================== execute QtDraw
@click.command()
@click.argument("filename", required=False)
def cmd(filename):
    """
    Execute QtDraw.

        FILENAME : file to open (.qtdw, .cif, .vesta, .xsf), ".qtdw" can be omitted.
    """
    if filename is None:
        QtDraw().exec()
    else:
        QtDraw(filename=resolve_file(filename)).exec()
