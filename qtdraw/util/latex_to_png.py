"""
Render LaTeX to backend.

This module provides LaTeX converter to backend.

See for example, https://github.com/ipython/IPython/lib/latextools.py.
"""

from io import BytesIO
from matplotlib import figure
from gcoreutils.color_palette import all_colors


# ==================================================
def latex_to_png(text, wrap=True, color="black", size=12, dpi=120):
    """
    Render a LaTeX string to png via matplotlib.

    Args:
        text (str): raw string containing valid inline LaTeX.
        backend (str, optional): backend for producing png or svg.
        wrap (bool, optional): if true, automatically wrap `s` as a LaTeX equation.
        color (str, optional): color name.
        size (int, optional): fontsize.
        dpi (int, optional): DPI.

    Returns:
        - (pixmap) -- pixmap image.

    Note:
        - None is returned when the backend cannot be used.
    """
    # mpl mathtext doesn't support display math, force inline
    text = text.replace("$$", "$")
    if wrap:
        text = f"$ {text}$"

    color = all_colors[color][0]

    fig = figure.Figure()
    obj = fig.text(0, 0, text, fontsize=size, color=color)

    buffer = BytesIO()
    fig.savefig(buffer, dpi=dpi, format="png", transparent=True, bbox_inches="tight", pad_inches=0.1)

    png = buffer.getvalue()
    return png
