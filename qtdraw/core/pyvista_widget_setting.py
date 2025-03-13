"""
Default setting for pyvista widget.
"""

# ==================================================
#
# current status.
#
# ==================================================
default_status = {
    # model.
    "model": "untitled",
    # unit cell.
    "origin": [0.0, 0.0, 0.0],
    "cell": {"a": 1.0, "b": 1.0, "c": 1.0, "alpha": 90.0, "beta": 90.0, "gamma": 90.0},
    "crystal": "",  # ""/triclinic/monoclinic/orthorhombic/tetragonal/trigonal/hexagonal/cubic.
    # view.
    "clip": False,
    "repeat": False,
    "lower": [0.0, 0.0, 0.0],
    "upper": [1.0, 1.0, 1.0],
    "view": [6, 5, 1],  # indices of [a1,a2,a3] unit vectors.
    "parallel_projection": True,
    "grid": False,
    "bar": False,
    "axis_type": "on",  # on/axis/off/full.
    "cell_mode": "single",  # single/all/off.
}

# ==================================================
#
# preference panel.
#
# ==================================================
default_preference = {
    "general": {
        "style": "fusion",  # "fusion/macos/windows"
        "font": "Osaka",  # "Monaco/Osaka/Arial/Times New Roman/Helvetica Neue"
        "size": 11,  # pixel
        "color_scheme": "Jmol",  # "VESTA/Jmol"
    },
    "light": {
        "type": "lightkit",  # "lightkit/3 lights/ver1"
        "intensity": 0.5,
        "pbr": False,
        "metallic": 0.0,
        "roughness": 0.4,
        "color": "white",
    },
    "label": {
        "font": "arial",  # "courier/times/arial"
        "size": 18,
        "bold": False,
        "italic": False,
        "color": "licorice",
        "default_check": False,
    },
    "cell": {
        "line_width": 2.0,
        "color": "black",
        "opacity": 1.0,
    },
    "axis": {
        "size": 20,
        "bold": True,
        "italic": False,
        "label": "[a,b,c]",  # [x,y,z], [a,b,c], [a*,b*,c*]
    },
    "latex": {"color": "black", "size": 10, "dpi": 120},
}

# ==================================================
#
# widget detail setting.
#
# ==================================================
widget_detail = {
    # pyvistaqt interactor.
    "theme": "document",  # "document/dark/paraview"
    "multi_samples": 8,
    "line_smoothing": True,
    "point_smoothing": True,
    "polygon_smoothing": True,
    "auto_update": 5.0,
    "anti_aliasing": True,  # if some problem, use False.
    "minimum_window_size": [200, 100],  # [width,height].
    "data_edit_key": "e",
    "prevent_key": ["b", "C", "f", "i", "p", "q", "r", "v", "s", "w"],
    "smooth_shading": True,
    # general.
    "extension": ".qtdw",
    "ext_material": [".vesta", ".cif", ".xsf"],
    "log_level": "error",  # debug/info/warning/error/critical.
    "default_view": [6, 5, 1],
    "image_file": [".png", ".bmp", ".tif", ".tiff"],
    "vector_file": [".svg", ".eps", ".ps", ".pdf"],
    # axis.
    "scale": 1.4,
    "pickable": True,
    "viewport": [0.0, 0.0, 0.12, 0.16],
    "shaft_color": ["crimson", "forestgreen", "royalblue"],
    "sphere_color": "snow",
    "shaft_radius": 0.05,
    "tip_radius": 0.1,
    "tip_length": 0.4,
    "tip_resolution": 60,
    "sphere_radius": 0.14,
    # plot.
    "theta_phi_range": [[0, 180], [0, 360]],
    "theta_phi_resolution": [90, 180],
    "theta_phi_division": [9, 18],
    "bond_resolution": 90,
    "circle_resolution": 90,
    "shaft_resolution": 60,
    "tip_resolution": 60,
    "text_normal": [0, 0, 1],
    "spline_t_range": [0, 1, 0.05],
    "label_color": ["black", "black", "black"],
    # spotlight.
    "spotlight_color": "pink",
    # cif and vesta.
    "site_scale": 0.3,
    "bond_scale": 0.08,
    # scalar bar.
    "bar_vertical": True,
    "bar_width": 0.05,
    "bar_height": 0.3,
    "bar_x": 0.05,
    "bar_y": 0.65,
    "bar_size": 14,
    "bar_format": " %5.2f",
}

# ==================================================
#
# internal use.
#
# ==================================================
CHOP = 1e-6
DIGIT = 6
HIDE_TYPE = ["actor", "bool", "hide"]
CUSTOM_WIDGET = ["color", "colormap", "color_both", "combo", "int", "float", "sympy_float", "ilist", "list", "sympy"]
COLOR_WIDGET = ["color", "colormap", "color_both"]
COMBO_WIDGET = ["combo"]
EDITOR_WIDGET = ["int", "float", "sympy_float", "ilist", "list", "sympy"]

COLUMN_NAME = 0
COLUMN_NAME_CHECK = 1
COLUMN_NAME_ACTOR = 2
COLUMN_LABEL = 3
COLUMN_LABEL_CHECK = 4
COLUMN_LABEL_ACTOR = 5
COLUMN_LABEL_MARGIN = 6
COLUMN_POSITION = 7
COLUMN_CELL = 8
COLUMN_ISOSURFACE_FILE = 9

# ==================================================
#
# each object: { name : (default value, type, options) }.
#   use check/bool in pair.
#
# ==================================================
object_default = {
    "site": {  # header: (type, option, default).
        "name": ("check", None, "untitled"),
        "name_check": ("bool", None, True),
        "name_actor": ("actor", None, ""),
        "label": ("check", None, "label"),
        "label_check": ("bool", None, False),
        "label_actor": ("actor", None, ""),
        "margin": ("int", (0, "*"), "3"),
        "position": ("list", ((3,), [""], 4), "[0,0,0]"),
        "cell": ("ilist", (3,), "[0,0,0]"),
        "size": ("float", (0.0, "*", 3), "0.1"),
        "color": ("color", None, "darkseagreen"),
        "opacity": ("float", (0.0, 1.0, 2), "1.0"),
    },
    "bond": {
        "name": ("check", None, "untitled"),
        "name_check": ("bool", None, True),
        "name_actor": ("actor", None, ""),
        "label": ("check", None, "label"),
        "label_check": ("bool", None, False),
        "label_actor": ("actor", None, ""),
        "margin": ("int", (0, "*"), "3"),
        "position": ("list", ((3,), [""], 4), "[0,0,0]"),
        "cell": ("ilist", (3,), "[0,0,0]"),
        "direction": ("list", ((3,), [""], 4), "[0,0,1]"),
        "width": ("float", (0.0, "*", 3), "0.02"),
        "color": ("color", None, "silver"),
        "color2": ("color", None, "silver"),
        "cartesian": ("check", None, ""),
        "cartesian_check": ("bool", None, False),
        "opacity": ("float", (0.0, 1.0, 2), "1.0"),
    },
    "vector": {
        "name": ("check", None, "untitled"),
        "name_check": ("bool", None, True),
        "name_actor": ("actor", None, ""),
        "label": ("check", None, "label"),
        "label_check": ("bool", None, False),
        "label_actor": ("actor", None, ""),
        "margin": ("int", (0, "*"), "3"),
        "position": ("list", ((3,), [""], 4), "[0,0,0]"),
        "cell": ("ilist", (3,), "[0,0,0]"),
        "direction": ("list", ((3,), [""], 4), "[0,0,1]"),
        "length": ("sympy_float", 4, "1.0"),
        "width": ("float", (0.0, "*", 3), "0.02"),
        "offset": ("float", ("*", "*", 3), "-0.43"),
        "color": ("color", None, "orange"),
        "cartesian": ("check", None, ""),
        "cartesian_check": ("bool", None, True),
        "shaft R": ("float", (0.0, "*", 3), "1.0"),
        "tip R": ("float", (0.0, "*", 3), "2.0"),
        "tip length": ("float", (0.0, "*", 3), "0.25"),
        "opacity": ("float", (0.0, 1.0, 2), "1.0"),
    },
    "orbital": {
        "name": ("check", None, "untitled"),
        "name_check": ("bool", None, True),
        "name_actor": ("actor", None, ""),
        "label": ("check", None, "label"),
        "label_check": ("bool", None, False),
        "label_actor": ("actor", None, ""),
        "margin": ("int", (0, "*"), "3"),
        "position": ("list", ((3,), [""], 4), "[0,0,0]"),
        "cell": ("ilist", (3,), "[0,0,0]"),
        "shape": ("sympy", ["x", "y", "z", "r"], "3z**2-r**2"),
        "surface": ("sympy", ["x", "y", "z", "r"], ""),
        "size": ("float", ("*", "*", 3), "0.5"),
        "range": ("ilist", (2, 2), "[[0,180],[0,360]]"),
        "color": ("color_both", None, "Wistia"),
        "opacity": ("float", (0.0, 1.0, 2), "1.0"),
    },
    "stream": {
        "name": ("check", None, "untitled"),
        "name_check": ("bool", None, True),
        "name_actor": ("actor", None, ""),
        "label": ("check", None, "label"),
        "label_check": ("bool", None, False),
        "label_actor": ("actor", None, ""),
        "margin": ("int", (0, "*"), "3"),
        "position": ("list", ((3,), [""], 4), "[0,0,0]"),
        "cell": ("ilist", (3,), "[0,0,0]"),
        "shape": ("sympy", ["x", "y", "z", "r"], "1"),
        "vector": ("list", ((3,), ["x", "y", "z", "r"], None), "[x,y,z]"),
        "size": ("float", (0.0, "*", 3), "0.5"),
        "range": ("ilist", (2, 2), "[[0,180],[0,360]]"),
        "division": ("ilist", (2,), "[9,18]"),
        "length": ("float", (0.0, "*", 3), "0.1"),
        "width": ("float", (0.0, "*", 3), "0.01"),
        "offset": ("float", ("*", "*", 3), "-0.43"),
        "abs_scale": ("check", None, ""),
        "abs_scale_check": ("bool", None, False),
        "color": ("color_both", None, "coolwarm"),
        "component": ("combo", ["x", "y", "z", "abs"], "abs"),
        "shaft R": ("float", (0.0, "*", 3), "1.0"),
        "tip R": ("float", (0.0, "*", 3), "2.0"),
        "tip length": ("float", (0.0, "*", 3), "0.25"),
        "opacity": ("float", (0.0, 1.0, 2), "1.0"),
    },
    "line": {
        "name": ("check", None, "untitled"),
        "name_check": ("bool", None, True),
        "name_actor": ("actor", None, ""),
        "label": ("check", None, "label"),
        "label_check": ("bool", None, False),
        "label_actor": ("actor", None, ""),
        "margin": ("int", (0, "*"), "3"),
        "position": ("list", ((3,), [""], 4), "[0,0,0]"),
        "cell": ("[ilist]", (3,), "[0,0,0]"),
        "direction": ("list", ((3,), [""], 3), "[0,0,1]"),
        "width": ("float", (0.0, "*", 3), "0.02"),
        "arrow1": ("check", None, ""),
        "arrow1_check": ("bool", None, False),
        "arrow2": ("check", None, ""),
        "arrow2_check": ("bool", None, False),
        "tip R": ("float", (0.0, "*", 3), "2.0"),
        "tip length": ("float", (0.0, "*", 3), "0.1"),
        "color": ("color", None, "strawberry"),
        "cartesian": ("check", None, ""),
        "cartesian_check": ("bool", None, False),
        "opacity": ("float", (0.0, 1.0, 2), "1.0"),
    },
    "plane": {
        "name": ("check", None, "untitled"),
        "name_check": ("bool", None, True),
        "name_actor": ("actor", None, ""),
        "label": ("check", None, "label"),
        "label_check": ("bool", None, False),
        "label_actor": ("actor", None, ""),
        "margin": ("int", (0, "*"), "3"),
        "position": ("list", ((3,), [""], 4), "[0,0,0]"),
        "cell": ("ilist", (3,), "[0,0,0]"),
        "normal": ("list", ((3,), [""], 3), "[0,0,1]"),
        "x_size": ("float", (0.0, "*", 3), "1.0"),
        "y_size": ("float", (0.0, "*", 3), "1.0"),
        "color": ("color", None, "sky"),
        "width": ("float", (0.0, "*", 3), "2.0"),
        "grid": ("check", None, ""),
        "grid_check": ("bool", None, False),
        "grid_color": ("color", None, "black"),
        "cartesian": ("check", None, ""),
        "cartesian_check": ("bool", None, True),
        "opacity": ("float", (0.0, 1.0, 2), "1.0"),
    },
    "circle": {
        "name": ("check", None, "untitled"),
        "name_check": ("bool", None, True),
        "name_actor": ("actor", None, ""),
        "label": ("check", None, "label"),
        "label_check": ("bool", None, False),
        "label_actor": ("actor", None, ""),
        "margin": ("int", (0, "*"), "3"),
        "position": ("list", ((3,), [""], 4), "[0,0,0]"),
        "cell": ("ilist", (3,), "[0,0,0]"),
        "normal": ("list", ((3,), [""], 3), "[0,0,1]"),
        "size": ("float", (0.0, "*", 3), "0.5"),
        "color": ("color", None, "salmon"),
        "width": ("float", (0.0, "*", 3), "2.0"),
        "edge": ("check", None, ""),
        "edge_check": ("bool", None, True),
        "edge_color": ("color", None, "black"),
        "cartesian": ("check", None, ""),
        "cartesian_check": ("bool", None, True),
        "opacity": ("float", (0.0, 1.0, 2), "1.0"),
    },
    "torus": {
        "name": ("check", None, "untitled"),
        "name_check": ("bool", None, True),
        "name_actor": ("actor", None, ""),
        "label": ("check", None, "label"),
        "label_check": ("bool", None, False),
        "label_actor": ("actor", None, ""),
        "margin": ("int", (0, "*"), "3"),
        "position": ("list", ((3,), [""], 4), "[0,0,0]"),
        "cell": ("ilist", (3,), "[0,0,0]"),
        "normal": ("list", ((3,), [""], 3), "[0,0,1]"),
        "size": ("float", (0.0, "*", 3), "0.5"),
        "width": ("float", (0.0, "*", 3), "0.15"),
        "color": ("color", None, "cantaloupe"),
        "cartesian": ("check", None, ""),
        "cartesian_check": ("bool", None, True),
        "opacity": ("float", (0.0, 1.0, 2), "1.0"),
    },
    "ellipsoid": {
        "name": ("check", None, "untitled"),
        "name_check": ("bool", None, True),
        "name_actor": ("actor", None, ""),
        "label": ("check", None, "label"),
        "label_check": ("bool", None, False),
        "label_actor": ("actor", None, ""),
        "margin": ("int", (0, "*"), "3"),
        "position": ("list", ((3,), [""], 4), "[0,0,0]"),
        "cell": ("ilist", (3,), "[0,0,0]"),
        "normal": ("list", ((3,), [""], 4), "[0,0,1]"),
        "x_size": ("float", (0.0, "*", 3), "0.5"),
        "y_size": ("float", (0.0, "*", 3), "0.4"),
        "z_size": ("float", (0.0, "*", 3), "0.3"),
        "color": ("color", None, "cornflowerblue"),
        "cartesian": ("check", None, ""),
        "cartesian_check": ("bool", None, True),
        "opacity": ("float", (0.0, 1.0, 2), "1.0"),
    },
    "toroid": {
        "name": ("check", None, "untitled"),
        "name_check": ("bool", None, True),
        "name_actor": ("actor", None, ""),
        "label": ("check", None, "label"),
        "label_check": ("bool", None, False),
        "label_actor": ("actor", None, ""),
        "margin": ("int", (0, "*"), "3"),
        "position": ("list", ((3,), [""], 4), "[0,0,0]"),
        "cell": ("ilist", (3,), "[0,0,0]"),
        "normal": ("list", ((3,), [""], 4), "[0,0,1]"),
        "size": ("float", (0.0, "*", 3), "0.5"),
        "width": ("float", (0.0, "*", 3), "0.15"),
        "x_scale": ("float", (0.0, "*", 3), "1.0"),
        "y_scale": ("float", (0.0, "*", 3), "1.0"),
        "z_scale": ("float", (0.0, "*", 3), "1.0"),
        "ring_shape": ("float", (0.0, "*", 3), "0.3"),
        "tube_shape": ("float", (0.0, "*", 3), "0.3"),
        "color": ("color", None, "tan"),
        "cartesian": ("check", None, ""),
        "cartesian_check": ("bool", None, True),
        "opacity": ("float", (0.0, 1.0, 2), "1.0"),
    },
    "box": {
        "name": ("check", None, "untitled"),
        "name_check": ("bool", None, True),
        "name_actor": ("actor", None, ""),
        "label": ("check", None, "label"),
        "label_check": ("bool", None, False),
        "label_actor": ("actor", None, ""),
        "margin": ("int", (0, "*"), "3"),
        "position": ("list", ((3,), [""], 4), "[0,0,0]"),
        "cell": ("ilist", (3,), "[0,0,0]"),
        "a1": ("list", ((3,), [""], 4), "[1,0,0]"),
        "a2": ("list", ((3,), [""], 4), "[0,1,0]"),
        "a3": ("list", ((3,), [""], 4), "[0,0,1]"),
        "width": ("float", (0.0, "*", 3), "2.0"),
        "edge": ("check", None, ""),
        "edge_check": ("bool", None, True),
        "edge_color": ("color", None, "black"),
        "wireframe": ("check", None, ""),
        "wireframe_check": ("bool", None, False),
        "color": ("color", None, "yellowgreen"),
        "cartesian": ("check", None, ""),
        "cartesian_check": ("bool", None, False),
        "opacity": ("float", (0.0, 1.0, 2), "1.0"),
    },
    "polygon": {
        "name": ("check", None, "untitled"),
        "name_check": ("bool", None, True),
        "name_actor": ("actor", None, ""),
        "label": ("check", None, "label"),
        "label_check": ("bool", None, False),
        "label_actor": ("actor", None, ""),
        "margin": ("int", (0, "*"), "3"),
        "position": ("list", ((3,), [""], 4), "[0,0,0]"),
        "cell": ("ilist", (3,), "[0,0,0]"),
        "point": (
            "list",
            ((3, 0), [""], 4),
            "[[0,0,0],[0.8,0,0],[0,0.6,0],[0,0,0.4],[0.6,0.6,0]]",
        ),
        "connectivity": ("ilist", (0, 0), "[[0,1,4,2],[0,1,3],[1,4,3],[2,0,3],[2,3,4]]"),
        "width": ("float", (0.0, "*", 3), "2.0"),
        "edge": ("check", None, ""),
        "edge_check": ("bool", None, True),
        "edge_color": ("color", None, "black"),
        "wireframe": ("check", None, ""),
        "wireframe_check": ("bool", None, False),
        "color": ("color", None, "aluminum"),
        "cartesian": ("check", None, ""),
        "cartesian_check": ("bool", None, False),
        "opacity": ("float", (0.0, 1.0, 2), "1.0"),
    },
    "spline": {
        "name": ("check", None, "untitled"),
        "name_check": ("bool", None, True),
        "name_actor": ("actor", None, ""),
        "label": ("check", None, "label"),
        "label_check": ("bool", None, False),
        "label_actor": ("actor", None, ""),
        "margin": ("int", (0, "*"), "3"),
        "position": ("list", ((3,), [""], 4), "[0,0,0]"),
        "cell": ("ilist", (3,), "[0,0,0]"),
        "point": ("list", ((3, 0), [""], 4), "[[0,0,0],[1,0,1],[0,1,2]]"),
        "width": ("float", (0.0, "*", 3), "0.01"),
        "n_interp": ("int", (0, "*"), "500"),
        "closed": ("check", None, ""),
        "closed_check": ("bool", None, False),
        "natural": ("check", None, ""),
        "natural_check": ("bool", None, True),
        "arrow1": ("check", None, ""),
        "arrow1_check": ("bool", None, False),
        "arrow2": ("check", None, ""),
        "arrow2_check": ("bool", None, False),
        "tip R": ("float", (0.0, "*", 3), "2.0"),
        "tip length": ("float", (0.0, "*", 3), "0.1"),
        "color": ("color", None, "banana"),
        "cartesian": ("check", None, ""),
        "cartesian_check": ("bool", None, True),
        "opacity": ("float", (0.0, 1.0, 2), "1.0"),
    },
    "spline_t": {
        "name": ("check", None, "untitled"),
        "name_check": ("bool", None, True),
        "name_actor": ("actor", None, ""),
        "label": ("check", None, "label"),
        "label_check": ("bool", None, False),
        "label_actor": ("actor", None, ""),
        "margin": ("int", (0, "*"), "3"),
        "position": ("list", ((3,), [""], 4), "[0,0,0]"),
        "cell": ("ilist", (3,), "[0,0,0]"),
        "point": ("list", ((3,), ["t"], None), "[cos(2 pi t), sin(2 pi t), t/2]"),
        "t_range": ("list", ((3,), [""], 4), "[0,1,0.05]"),
        "width": ("float", (0.0, "*", 3), "0.01"),
        "n_interp": ("int", (0, "*"), "500"),
        "closed": ("check", None, ""),
        "closed_check": ("bool", None, False),
        "natural": ("check", None, ""),
        "natural_check": ("bool", None, True),
        "arrow1": ("check", None, ""),
        "arrow1_check": ("bool", None, False),
        "arrow2": ("check", None, ""),
        "arrow2_check": ("bool", None, False),
        "tip R": ("float", (0.0, "*", 3), "2.0"),
        "tip length": ("float", (0.0, "*", 3), "0.1"),
        "color": ("color", None, "crimson"),
        "cartesian": ("check", None, ""),
        "cartesian_check": ("bool", None, True),
        "opacity": ("float", (0.0, 1.0, 2), "1.0"),
    },
    "text3d": {
        "name": ("check", None, "untitled"),
        "name_check": ("bool", None, True),
        "name_actor": ("actor", None, ""),
        "label": ("check", None, "label"),
        "label_check": ("bool", None, False),
        "label_actor": ("actor", None, ""),
        "margin": ("int", (0, "*"), "3"),
        "position": ("list", ((3,), [""], 4), "[0,0,0]"),
        "cell": ("ilist", (3,), "[0,0,0]"),
        "text": ("str", None, "text"),
        "size": ("float", (0.0, "*", 3), "0.3"),
        "view": ("list", ((3,), [""], 4), "[0,0,1]"),
        "depth": ("float", ("*", "*", 3), "0.2"),
        "offset": ("float", ("*", "*", 3), "[0,0,0]"),
        "color": ("color", None, "iron"),
        "opacity": ("float", (0.0, 1.0, 2), "1.0"),
    },
    "isosurface": {
        "name": ("check", None, "untitled"),
        "name_check": ("bool", None, True),
        "name_actor": ("actor", None, ""),
        "label": ("check", None, "label"),
        "label_check": ("bool", None, False),
        "label_actor": ("actor", None, ""),
        "margin": ("int", (0, "*"), "3"),
        "position": ("list", ((3,), [""], 4), "[0,0,0]"),
        "cell": ("ilist", (3,), "[0,0,0]"),
        "data": ("str", None, ""),
        "value": ("list", ((0,), [""], 4), "[0.5]"),
        "surface": ("str", None, ""),
        "color": ("color_both", None, "white"),
        "color_range": ("list", ((2,), [""], 3), "[0,1]"),
        "opacity": ("float", (0.0, 1.0, 2), "0.8"),
    },
    "caption": {
        "name": ("check", None, "untitled"),
        "name_check": ("bool", None, True),
        "name_actor": ("actor", None, ""),
        "label": ("hide", None, ""),  # dummy.
        "label_check": ("hide", None, ""),  # dummy.
        "label_actor": ("hide", None, ""),  # dummy.
        "margin": ("int", (0, "*"), "3"),
        "position": ("list", ((3, 0), [""], 4), "[[0,0,0],[1,0,0],[1,1,0]]"),
        "cell": ("ilist", (3,), "[0,0,0]"),
        "caption": ("str", None, "[A,B,C]"),
        "size": ("int", (0, "*"), "18"),
        "bold": ("check", None, ""),
        "bold_check": ("bool", None, True),
        "color": ("color", None, "licorice"),
    },
    "text2d": {
        "name": ("check", None, "untitled"),
        "name_check": ("bool", None, True),
        "name_actor": ("actor", None, ""),
        "label": ("hide", None, ""),  # dummy.
        "label_check": ("hide", None, ""),  # dummy.
        "label_actor": ("hide", None, ""),  # dummy.
        "margin": ("hide", None, ""),  # dummy.
        "position": ("list", ((3,), [""], 4), "[0.02,0.95,0]"),  # z-comp. dummy.
        "cell": ("hide", None, "[0,0,0]"),  # dummy.
        "caption": ("str", None, "text"),
        "size": ("int", (0, "*"), "8"),
        "color": ("color", None, "licorice"),
        "font": ("combo", ["arial", "times", "courier"], "arial"),
    },
}
