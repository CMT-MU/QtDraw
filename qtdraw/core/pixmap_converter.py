import matplotlib.pyplot as plt
from io import BytesIO
from qtpy.QtGui import QPixmap
from gcoreutils.basic_util import apply
from gcoreutils.convert_util import text_to_sympy, sympy_to_latex


# ==================================================
def _latex2pixmap(latex, size=14, color="black", dpi=300, style="svg", verbose=False):
    if style == "svg":
        size *= 4

    try:
        pixmap = QPixmap()
        fig = plt.figure(figsize=(0.01, 0.01))
        fig.text(0, 0, r"$\displaystyle {}$".format(latex), fontsize=int(0.32 * size), color=color)
        output = BytesIO()
        fig.savefig(output, dpi=dpi, transparent=True, format=style, bbox_inches="tight", pad_inches=0.05)
        plt.close(fig)
        output.seek(0)
        svg = output.read()
        pixmap.loadFromData(svg, style)
        return pixmap
    except RuntimeError:
        if verbose:
            raise RuntimeError(f"latex compile error in {latex}.")
        return None


# ==================================================
def _text2pixmap(text, local=None, check_var=None, rational=False, fill=None, verbose=False):
    ltx = sympy_to_latex(text_to_sympy(text, local, check_var, rational))
    if ltx:
        return latex2pixmap(ltx)
    else:
        return None


# ==================================================
def latex2pixmap(latex, size=14, color="black", dpi=300, style="svg", verbose=False):
    """
    convert latex to pixmap.

    Args:
        latex (str): latex text code.
        size (int, optional): font size.
        color (str, optional): matplotlib color name.
        dpi (int, optional): DPI in creating pixmap.
        style (str, optional): render style, "svg/png/jpg".
        verbose (bool, optional): raise ConversionError, if compile error occurs.

    Returns:
        list or QPixmap: rendered pixmap.

    Notes:
        - if compile error occurs, return None.
        - environment to compile latex is required.
    """
    return apply(lambda ltx: _latex2pixmap(ltx, size, color, dpi, style, verbose), latex)


# ==================================================
def text2pixmap(text, local=None, check_var=None, rational=False, fill=None, verbose=False):
    """
    convert text to pixmap via sympy.

    Args:
        text (str): text to convert.
        local (dict, optional): dict of local variables to use when parsing.
        check_var (list, optional): acceptable variable strings.
        rational (bool, optional): convert float into rational ?
        fill (str): text to fill the empty element.
        verbose (bool, optional): raise ConversionError, if error occurs.

    Returns:
        list or QPixmap: rendered pixmap.

    Notes:
        - if conversion error occurs, return None.
    """
    return apply(lambda t: _text2pixmap(t, local, check_var, rational, fill, verbose), text)
