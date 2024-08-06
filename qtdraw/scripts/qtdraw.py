"""
Execute QtDraw.
"""

import click
from pathlib import Path
from qtdraw.core.qtdraw_app import QtDraw


# ================================================== execute QtDraw
@click.command()
@click.argument("filename", nargs=-1)
def cmd(filename):
    """
    execute QtDraw.

        filename : `.qtdw` file without extension.
    """
    n = len(filename)
    if n < 1:
        QtDraw().exec()
        exit()
    elif n > 1:
        exit()

    filename = Path(filename[0]).resolve()
    QtDraw(filename=filename).exec()
