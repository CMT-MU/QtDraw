"""
Example for QtDraw (load from file).
"""

from qtdraw.qt_draw import QtDraw

d = __file__[: __file__.rfind("/")]

QtDraw(filename=d + "icon.qtdw").show()
QtDraw(filename=d + "color_pattern.qtdw").show()
