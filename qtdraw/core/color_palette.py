"""
color palette : matplotlib CSS colors, mpl_colors = mcolors.CSS4_COLORS, apple colors
"""
from matplotlib import cm
from matplotlib.colors import ListedColormap
import numpy as np
from qtpy.QtGui import QPixmap, QColor, QImage
from qtpy.QtCore import Qt
from gcoreutils.basic_util import apply


# ==================================================
# Apple Crayon Palette, name : (hex, RGB)
apple_colors = {
    "licorice": ("#000000", (0, 0, 0)),
    "lead": ("#212121", (33, 33, 33)),
    "tungsten": ("#424242", (66, 66, 66)),
    "iron": ("#5e5e5e", (94, 94, 94)),
    "steel": ("#797979", (121, 121, 121)),
    "tin": ("#919191", (145, 145, 145)),
    "nickel": ("#929292", (146, 146, 146)),
    "aluminum": ("#a9a9a9", (169, 169, 169)),
    "magnesium": ("#c0c0c0", (192, 192, 192)),
    "silver": ("#d6d6d6", (214, 214, 214)),
    "mercury": ("#ebebeb", (235, 235, 235)),
    "snow": ("#ffffff", (255, 255, 255)),
    #
    "cayenne": ("#941100", (148, 17, 0)),
    "mocha": ("#945200", (148, 82, 0)),
    "aspargus": ("#929000", (146, 144, 0)),
    "fern": ("#4f8f00", (79, 143, 0)),
    "clover": ("#008f00", (0, 143, 0)),
    "moss": ("#009051", (0, 144, 81)),
    "teal": ("#009193", (0, 145, 147)),
    "ocean": ("#005493", (0, 84, 147)),
    "midnight": ("#011993", (1, 25, 147)),
    "eggplant": ("#531b93", (83, 27, 147)),
    "plum": ("#942193", (148, 33, 147)),
    "maroon": ("#941751", (148, 23, 81)),
    #
    "maraschino": ("#ff2600", (255, 38, 0)),
    "tangerine": ("#ff9300", (255, 147, 0)),
    "lemon": ("#fffb00", (255, 251, 0)),
    "lime": ("#8efa00", (142, 250, 0)),
    "spring": ("#00f900", (0, 249, 0)),
    "seam-foam": ("#00fa92", (0, 250, 146)),
    "turquoise": ("#00fdff", (0, 253, 255)),
    "aqua": ("#0096ff", (0, 150, 255)),
    "blueberry": ("#0433ff", (4, 51, 255)),
    "grape": ("#9437ff", (148, 55, 255)),
    "magenta": ("#ff40ff", (255, 64, 255)),
    "strawberry": ("#ff2f92", (255, 47, 146)),
    "salmon": ("#ff7e79", (255, 126, 121)),
    #
    "cantaloupe": ("#ffd479", (255, 212, 121)),
    "banana": ("#fffc79", (255, 252, 121)),
    "honeydew": ("#d4fb79", (212, 251, 121)),
    "flora": ("#73fa79", (115, 250, 121)),
    "spindrift": ("#73fcd6", (115, 252, 214)),
    "ice": ("#73fdff", (115, 253, 255)),
    "sky": ("#76d6ff", (118, 214, 255)),
    "orchid": ("#7a81ff", (122, 129, 255)),
    "lavender": ("#d783ff", (215, 131, 255)),
    "bubblegum": ("#ff85ff", (255, 133, 255)),
    "carnation": ("#ff8ad8", (255, 138, 216)),
}

# ==================================================
# Matplotlib Palette, name : (hex, RGB)
matplotlib_colors = {
    "black": ("#000000", (0, 0, 0)),
    "aliceblue": ("#F0F8FF", (240, 248, 255)),
    "antiquewhite": ("#FAEBD7", (250, 235, 215)),
    "cyan": ("#00FFFF", (0, 255, 255)),
    "aquamarine": ("#7FFFD4", (127, 255, 212)),
    "azure": ("#F0FFFF", (240, 255, 255)),
    "beige": ("#F5F5DC", (245, 245, 220)),
    "bisque": ("#FFE4C4", (255, 228, 196)),
    "blanchedalmond": ("#FFEBCD", (255, 235, 205)),
    "blue": ("#0000FF", (0, 0, 255)),
    "blueviolet": ("#8A2BE2", (138, 43, 226)),
    "brown": ("#A52A2A", (165, 42, 42)),
    "burlywood": ("#DEB887", (222, 184, 135)),
    "cadetblue": ("#5F9EA0", (95, 158, 160)),
    "chartreuse": ("#7FFF00", (127, 255, 0)),
    "chocolate": ("#D2691E", (210, 105, 30)),
    "coral": ("#FF7F50", (255, 127, 80)),
    "cornflowerblue": ("#6495ED", (100, 149, 237)),
    "cornsilk": ("#FFF8DC", (255, 248, 220)),
    "crimson": ("#DC143C", (220, 20, 60)),
    "darkblue": ("#00008B", (0, 0, 139)),
    "darkcyan": ("#008B8B", (0, 139, 139)),
    "darkgoldenrod": ("#B8860B", (184, 134, 11)),
    "darkgrey": ("#A9A9A9", (169, 169, 169)),
    "darkgreen": ("#006400", (0, 100, 0)),
    "darkkhaki": ("#BDB76B", (189, 183, 107)),
    "darkmagenta": ("#8B008B", (139, 0, 139)),
    "darkolivegreen": ("#556B2F", (85, 107, 47)),
    "darkorange": ("#FF8C00", (255, 140, 0)),
    "darkorchid": ("#9932CC", (153, 50, 204)),
    "darkred": ("#8B0000", (139, 0, 0)),
    "darksalmon": ("#E9967A", (233, 150, 122)),
    "darkseagreen": ("#8FBC8F", (143, 188, 143)),
    "darkslateblue": ("#483D8B", (72, 61, 139)),
    "darkslategrey": ("#2F4F4F", (47, 79, 79)),
    "darkturquoise": ("#00CED1", (0, 206, 209)),
    "darkviolet": ("#9400D3", (148, 0, 211)),
    "deeppink": ("#FF1493", (255, 20, 147)),
    "deepskyblue": ("#00BFFF", (0, 191, 255)),
    "dimgrey": ("#696969", (105, 105, 105)),
    "dodgerblue": ("#1E90FF", (30, 144, 255)),
    "firebrick": ("#B22222", (178, 34, 34)),
    "floralwhite": ("#FFFAF0", (255, 250, 240)),
    "forestgreen": ("#228B22", (34, 139, 34)),
    "gainsboro": ("#DCDCDC", (220, 220, 220)),
    "ghostwhite": ("#F8F8FF", (248, 248, 255)),
    "gold": ("#FFD700", (255, 215, 0)),
    "goldenrod": ("#DAA520", (218, 165, 32)),
    "grey": ("#808080", (128, 128, 128)),
    "green": ("#008000", (0, 128, 0)),
    "greenyellow": ("#ADFF2F", (173, 255, 47)),
    "hotpink": ("#FF69B4", (255, 105, 180)),
    "indianred": ("#CD5C5C", (205, 92, 92)),
    "indigo": ("#4B0082", (75, 0, 130)),
    "ivory": ("#FFFFF0", (255, 255, 240)),
    "khaki": ("#F0E68C", (240, 230, 140)),
    "lavenderblush": ("#FFF0F5", (255, 240, 245)),
    "lawngreen": ("#7CFC00", (124, 252, 0)),
    "lemonchiffon": ("#FFFACD", (255, 250, 205)),
    "lightblue": ("#ADD8E6", (173, 216, 230)),
    "lightcoral": ("#F08080", (240, 128, 128)),
    "lightcyan": ("#E0FFFF", (224, 255, 255)),
    "lightgoldenrodyellow": ("#FAFAD2", (250, 250, 210)),
    "lightgrey": ("#D3D3D3", (211, 211, 211)),
    "lightgreen": ("#90EE90", (144, 238, 144)),
    "lightpink": ("#FFB6C1", (255, 182, 193)),
    "lightsalmon": ("#FFA07A", (255, 160, 122)),
    "lightseagreen": ("#20B2AA", (32, 178, 170)),
    "lightskyblue": ("#87CEFA", (135, 206, 250)),
    "lightslategrey": ("#778899", (119, 136, 153)),
    "lightsteelblue": ("#B0C4DE", (176, 196, 222)),
    "lightyellow": ("#FFFFE0", (255, 255, 224)),
    "limegreen": ("#32CD32", (50, 205, 50)),
    "linen": ("#FAF0E6", (250, 240, 230)),
    "mediumaquamarine": ("#66CDAA", (102, 205, 170)),
    "mediumblue": ("#0000CD", (0, 0, 205)),
    "mediumorchid": ("#BA55D3", (186, 85, 211)),
    "mediumpurple": ("#9370DB", (147, 112, 219)),
    "mediumseagreen": ("#3CB371", (60, 179, 113)),
    "mediumslateblue": ("#7B68EE", (123, 104, 238)),
    "mediumspringgreen": ("#00FA9A", (0, 250, 154)),
    "mediumturquoise": ("#48D1CC", (72, 209, 204)),
    "mediumvioletred": ("#C71585", (199, 21, 133)),
    "midnightblue": ("#191970", (25, 25, 112)),
    "mintcream": ("#F5FFFA", (245, 255, 250)),
    "mistyrose": ("#FFE4E1", (255, 228, 225)),
    "moccasin": ("#FFE4B5", (255, 228, 181)),
    "navajowhite": ("#FFDEAD", (255, 222, 173)),
    "navy": ("#000080", (0, 0, 128)),
    "oldlace": ("#FDF5E6", (253, 245, 230)),
    "olive": ("#808000", (128, 128, 0)),
    "olivedrab": ("#6B8E23", (107, 142, 35)),
    "orange": ("#FFA500", (255, 165, 0)),
    "orangered": ("#FF4500", (255, 69, 0)),
    "palegoldenrod": ("#EEE8AA", (238, 232, 170)),
    "palegreen": ("#98FB98", (152, 251, 152)),
    "paleturquoise": ("#AFEEEE", (175, 238, 238)),
    "palevioletred": ("#DB7093", (219, 112, 147)),
    "papayawhip": ("#FFEFD5", (255, 239, 213)),
    "peachpuff": ("#FFDAB9", (255, 218, 185)),
    "peru": ("#CD853F", (205, 133, 63)),
    "pink": ("#FFC0CB", (255, 192, 203)),
    "powderblue": ("#B0E0E6", (176, 224, 230)),
    "purple": ("#800080", (128, 0, 128)),
    "rebeccapurple": ("#663399", (102, 51, 153)),
    "red": ("#FF0000", (255, 0, 0)),
    "rosybrown": ("#BC8F8F", (188, 143, 143)),
    "royalblue": ("#4169E1", (65, 105, 225)),
    "saddlebrown": ("#8B4513", (139, 69, 19)),
    "sandybrown": ("#F4A460", (244, 164, 96)),
    "seagreen": ("#2E8B57", (46, 139, 87)),
    "seashell": ("#FFF5EE", (255, 245, 238)),
    "sienna": ("#A0522D", (160, 82, 45)),
    "skyblue": ("#87CEEB", (135, 206, 235)),
    "slateblue": ("#6A5ACD", (106, 90, 205)),
    "slategrey": ("#708090", (112, 128, 144)),
    "springgreen": ("#00FF7F", (0, 255, 127)),
    "steelblue": ("#4682B4", (70, 130, 180)),
    "tan": ("#D2B48C", (210, 180, 140)),
    "thistle": ("#D8BFD8", (216, 191, 216)),
    "tomato": ("#FF6347", (255, 99, 71)),
    "violet": ("#EE82EE", (238, 130, 238)),
    "wheat": ("#F5DEB3", (245, 222, 179)),
    "white": ("#FFFFFF", (255, 255, 255)),
    "whitesmoke": ("#F5F5F5", (245, 245, 245)),
    "yellow": ("#FFFF00", (255, 255, 0)),
    "yellowgreen": ("#9ACD32", (154, 205, 50)),
}

# ==================================================
# hex-code to color name (matplotlib name is used for the same color code)
hex_colornames = {h[0]: name for name, h in apple_colors.items()} | {h[0]: name for name, h in matplotlib_colors.items()}

# ==================================================
# RGB to color name (matplotlib name is used for the same color code)
rgb_colornames = {h[1]: name for name, h in apple_colors.items()} | {h[1]: name for name, h in matplotlib_colors.items()}

# ==================================================
# all colors, separated by "--- apple" and "--- matplotlib"
all_colors = apple_colors | matplotlib_colors
all_colors_sep = [len(apple_colors)]

# ==================================================
# matplotlib colormap
matplotlib_colormaps = {
    "uniform": ["viridis", "plasma", "inferno", "magma", "cividis"],
    "sequential1": [
        "Greys",
        "Purples",
        "Blues",
        "Greens",
        "Oranges",
        "Reds",
        "YlOrBr",
        "YlOrRd",
        "OrRd",
        "PuRd",
        "RdPu",
        "BuPu",
        "GnBu",
        "PuBu",
        "YlGnBu",
        "PuBuGn",
        "BuGn",
        "YlGn",
    ],
    "sequential2": [
        "binary",
        "gist_yarg",
        "gist_gray",
        "gray",
        "bone",
        "pink*",
        "spring*",
        "summer",
        "autumn",
        "winter",
        "cool",
        "Wistia",
        "hot",
        "afmhot",
        "gist_heat",
        "copper",
    ],
    "diverging": ["PiYG", "PRGn", "BrBG", "PuOr", "RdGy", "RdBu", "RdYlBu", "RdYlGn", "Spectral", "coolwarm", "bwr", "seismic"],
    "cyclic": ["twilight", "twilight_shifted", "hsv"],
    "qualitative": [
        "Pastel1",
        "Pastel2",
        "Paired",
        "Accent",
        "Dark2",
        "Set1",
        "Set2",
        "Set3",
        "tab10",
        "tab20",
        "tab20b",
        "tab20c",
    ],
    "misc": [
        "flag",
        "prism",
        "ocean*",
        "gist_earth",
        "terrain",
        "gist_stern",
        "gnuplot",
        "gnuplot2",
        "CMRmap",
        "cubehelix",
        "brg",
        "gist_rainbow",
        "rainbow",
        "jet",
        "turbo",
        "nipy_spectral",
        "gist_ncar",
    ],
}

# ==================================================
# all colormaps, separated by "--- category"
all_colormaps = sum(matplotlib_colormaps.values(), [])
__nmap = list(map(len, matplotlib_colormaps.values()))
all_colormaps_sep = [sum(__nmap[:g]) + i for i, g in enumerate(range(1, len(__nmap)))]


# ==================================================
def name_sep(color_type):
    lst1 = list(all_colors.keys())
    lst2 = all_colormaps
    lst = {"color": lst1, "colormap": lst2, "color_both": lst1 + lst2}

    nc = len(lst1)
    bothsep = []
    for i in all_colors_sep:
        bothsep.append(i)
    bothsep.append(nc + 1)
    for i in all_colormaps_sep:
        bothsep.append(i + nc + 2)

    sep = {"color": all_colors_sep, "colormap": all_colormaps_sep, "color_both": bothsep}

    return lst[color_type], sep[color_type]


# ==================================================
def _rgb2html(RGB):
    """
    convert RGB color to hex code (#??????).

    Args:
        RGB (tuple): RGB value in decimal number

    Returns:
        str: hex code
    """
    R, G, B = RGB
    color_code = "#{:02x}{:02x}{:02x}".format(R, G, B)
    return color_code.replace("0x", "")


# ==================================================
def _hex2rgb(color_code):
    """
    convert hex (#??????) code to RGB.

    Args:
        color_code (str): hex code

    Returns:
        tuple: R, G, B values
    """
    R = int(color_code[1:3], 16)
    G = int(color_code[3:5], 16)
    B = int(color_code[5:7], 16)
    return R, G, B


# ==================================================
def _cmap2pixmap(cmap, steps=50):
    if cmap not in all_colormaps:
        raise ValueError(f"unknown colormap, {cmap} is given.")

    sm = cm.ScalarMappable(cmap=cmap.strip("*"))
    sm.norm.vmin = 0.0
    sm.norm.vmax = 1.0
    inds = np.linspace(0, 1, steps)
    rgbas = sm.to_rgba(inds)
    rgbas = [QColor(int(r * 255), int(g * 255), int(b * 255), int(a * 255)).rgba() for r, g, b, a in rgbas]
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
        colorbox = colorbox.scaled(aspect_ratio * size, size, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
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

    pixmap = apply(lambda c: _color2pixmap(c, color_type, size, aspect_ratio, steps), names)
    pixmap_dict = {name: value for name, value in zip(names, pixmap)}

    return pixmap_dict, sep


# ==================================================
def custom_colormap(color_list, name="custom"):
    """
    custom colormap.

    Args:
        color_list (list): list of color names.
        name (str, optional): name of the colormap.

    Raises:
        ValueError: raised if color_list contains unknown name.

    Returns:
        ListedColormap: colormap.
    """
    try:
        rgbs = [(all_colors[i][1][0] / 255, all_colors[i][1][1] / 255, all_colors[i][1][2] / 255) for i in color_list]
    except KeyError:
        raise ValueError(f"unknown color name, {color_list} is given.")
    cmap = ListedColormap(rgbs, name)
    return cmap


# ==================================================
def check_color(name):
    """
    check if name is color or colormap.

    Args:
        name (str): color or colormap name.

    Returns:
        bool: True if name is color.
    """
    return name in all_colors.keys()
