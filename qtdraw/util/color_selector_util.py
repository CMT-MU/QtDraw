"""
Color selector widget.

This module provides color selector widget.
"""

import numpy as np
from matplotlib import cm
from PySide6.QtGui import QPixmap, QColor, QImage
from PySide6.QtCore import Qt
from gcoreutils.basic_util import apply
from gcoreutils.color_palette import all_colors, all_colormaps, check_color, name_sep


# ==================================================
def _colormap2pixmap(colormap, step=50):
    """
    Convert colormap to pixmap.

    Args:
        colormap (str): colormap.
        step (int, optional): division of colorbar gradation.

    Returns:
        - (QPixmap) -- color pixmap.
    """
    if colormap not in all_colormaps:
        raise ValueError(f"unknown colormap, {colormap} is given.")

    sm = cm.ScalarMappable(cmap=colormap.strip("*"))
    sm.norm.vmin = 0.0
    sm.norm.vmax = 1.0
    inds = np.linspace(0, 1, step)
    rgbas = sm.to_rgba(inds)
    rgbas = [QColor(int(r * 255), int(g * 255), int(b * 255), int(a * 255)).rgba() for r, g, b, a in rgbas]
    im = QImage(step, 1, QImage.Format_Indexed8)
    im.setColorTable(rgbas)
    for i in range(step):
        im.setPixel(i, 0, i)
    im = im.scaled(100, 100)
    pm = QPixmap.fromImage(im)
    return pm


# ==================================================
def _color2pixmap(color, color_type, size, aspect_ratio=4, step=50):
    """
    Convert color/colormap to pixmap.

    Args:
        color (str): color or colormap.
        color_type (str): color type, "color/colormap/color_both".
        size (int): vertical size (pixel).
        aspect_ratio (int, optional): aspect ratio of pximap (width/height).
        step (int, optional): division of colorbar gradation.

    Returns:
        - (QPixmap) -- color pixmap.
    """
    if check_color(color):
        if color_type == "color":
            colorbox = QPixmap(size, size)
        else:
            colorbox = QPixmap(aspect_ratio * size, size)
        colorbox.fill(QColor(all_colors[color][0]))
    else:
        colorbox = _colormap2pixmap(color, step=step)
        colorbox = colorbox.scaled(aspect_ratio * size, size, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
    return colorbox


# ==================================================
def color2pixmap(color_type, size, aspect_ratio=4, step=50):
    """
    Convert color/colormap to QPixmap.

    Args:
        color_type (str): color type, "color/colormap/color_both".
        size (int): size of pixmap.
        aspect_ratio (int, optional): aspect ratio of pximap (width/height).
        steps (int, optional): division of colorbar gradation.

    Retruns:
        - (dict) -- pixmap dict {name: pixmap}.
        - (list) -- separator position.
    """
    names, sep = name_sep(color_type)

    pixmap = apply(lambda c: _color2pixmap(c, color_type, size, aspect_ratio, step), names)
    pixmap_dict = {name: value for name, value in zip(names, pixmap)}

    return pixmap_dict, sep
