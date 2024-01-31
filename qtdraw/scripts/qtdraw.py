"""
execute QtDraw.
"""
import click
from qtdraw.qt_draw import QtDraw
import os


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
        QtDraw().show()
        exit()
    elif n > 1:
        exit()

    filename = os.path.abspath(filename[0])
    QtDraw(filename=filename).show()
