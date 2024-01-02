"""
color pixmap
"""
import numpy as np
from matplotlib import cm
from gcoreutils.basic_util import apply
from gcoreutils.color_palette import all_colors, all_colormaps, check_color, name_sep
from qtpy.QtGui import QPixmap, QColor, QImage
from qtpy.QtCore import Qt


# ==================================================
def _cmap2pixmap(cmap, steps=50):
    if cmap not in all_colormaps:
        raise ValueError(f"unknown colormap, {cmap} is given.")

    sm = cm.ScalarMappable(cmap=cmap.strip("*"))
    sm.norm.vmin = 0.0
    sm.norm.vmax = 1.0
    inds = np.linspace(0, 1, steps)
    rgbas = sm.to_rgba(inds)
    rgbas = [
        QColor(int(r * 255), int(g * 255), int(b * 255), int(a * 255)).rgba()
        for r, g, b, a in rgbas
    ]
    im = QImage(steps, 1, QImage.Format_Indexed8)
    im.setColorTable(rgbas)
    for i in range(steps):
        im.setPixel(i, 0, i)
    im = im.scaled(100, 100)
    pm = QPixmap.fromImage(im)
    return pm


# ==================================================
def _color2pixmap(c, color_type, size, aspect_ratio=4, steps=50):
    if check_color(c):
        if color_type == "color":
            colorbox = QPixmap(size, size)
        else:
            colorbox = QPixmap(aspect_ratio * size, size)
        colorbox.fill(QColor(all_colors[c][0]))
    else:
        colorbox = _cmap2pixmap(c, steps=steps)
        colorbox = colorbox.scaled(
            aspect_ratio * size, size, Qt.IgnoreAspectRatio, Qt.SmoothTransformation
        )
    return colorbox


# ==================================================
def color2pixmap(color_type, size, aspect_ratio=4, steps=50):
    """
    convert color/colormap to QPixmap.

    Args:
        color_type (str): color type, "color/colormap/color_both".
        size (int): size of pixmap.
        aspect_ratio (int, optional): aspect ratio of pximap.
        steps (int, optional): number of color steps.

    Retruns: tuple
        - dict: pixmap dict {name: pixmap}.
        - list: separator position.
    """
    names, sep = name_sep(color_type)

    pixmap = apply(
        lambda c: _color2pixmap(c, color_type, size, aspect_ratio, steps), names
    )
    pixmap_dict = {name: value for name, value in zip(names, pixmap)}

    return pixmap_dict, sep
