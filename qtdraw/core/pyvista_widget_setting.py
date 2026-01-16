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
        "size": 12,  # pixel
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
        "color": "black",
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
    "sphere_color": "white",
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
COLOR_WIDGET = ["color", "colormap", "color_both"]
COMBO_WIDGET = ["combo"]
EDITOR_WIDGET = ["int", "float", "list_int", "list_float", "math"]
CUSTOM_WIDGET = COLOR_WIDGET + COMBO_WIDGET + EDITOR_WIDGET

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
        "name": ("check", {}, "untitled"),
        "name_check": ("bool", {}, True),
        "name_actor": ("actor", {}, ""),
        "label": ("check", {}, "label"),
        "label_check": ("bool", {}, False),
        "label_actor": ("actor", {}, ""),
        "margin": ("int", {"min": 0, "max": "*"}, "3"),
        "position": ("list_float", {"shape": (3,), "var": [""], "digit": 4}, "[0,0,0]"),
        "cell": ("list_int", {"shape": (3,)}, "[0,0,0]"),
        "size": ("float", {"min": 0.0, "max": "*", "digit": 3}, "0.1"),
        "color": ("color", {}, "darkseagreen"),
        "opacity": ("float", {"min": 0.0, "max": 1.0, "digit": 2}, "1.0"),
    },
    "bond": {
        "name": ("check", {}, "untitled"),
        "name_check": ("bool", {}, True),
        "name_actor": ("actor", {}, ""),
        "label": ("check", {}, "label"),
        "label_check": ("bool", {}, False),
        "label_actor": ("actor", {}, ""),
        "margin": ("int", {"min": 0, "max": "*"}, "3"),
        "position": ("list_float", {"shape": (3,), "var": [""], "digit": 4}, "[0,0,0]"),
        "cell": ("list_int", {"shape": (3,)}, "[0,0,0]"),
        "direction": ("list_float", {"shape": (3,), "var": [""], "digit": 4}, "[0,0,1]"),
        "width": ("float", {"min": 0.0, "max": "*", "digit": 3}, "0.02"),
        "color": ("color", {}, "silver"),
        "color2": ("color", {}, "silver"),
        "cartesian": ("check", {}, ""),
        "cartesian_check": ("bool", {}, False),
        "opacity": ("float", {"min": 0.0, "max": 1.0, "digit": 2}, "1.0"),
    },
    "vector": {
        "name": ("check", {}, "untitled"),
        "name_check": ("bool", {}, True),
        "name_actor": ("actor", {}, ""),
        "label": ("check", {}, "label"),
        "label_check": ("bool", {}, False),
        "label_actor": ("actor", {}, ""),
        "margin": ("int", {"min": 0, "max": "*"}, "3"),
        "position": ("list_float", {"shape": (3,), "var": [""], "digit": 4}, "[0,0,0]"),
        "cell": ("list_int", {"shape": (3,)}, "[0,0,0]"),
        "direction": ("list_float", {"shape": (3,), "var": [""], "digit": 4}, "[0,0,1]"),
        "length": ("float", {"digit": 4}, "1.0"),
        "width": ("float", {"min": 0.0, "max": "*", "digit": 3}, "0.02"),
        "offset": ("float", {"min": "*", "max": "*", "digit": 3}, "-0.43"),
        "color": ("color", {}, "orange"),
        "cartesian": ("check", {}, ""),
        "cartesian_check": ("bool", {}, True),
        "shaft R": ("float", {"min": 0.0, "max": "*", "digit": 3}, "1.0"),
        "tip R": ("float", {"min": 0.0, "max": "*", "digit": 3}, "2.0"),
        "tip length": ("float", {"min": 0.0, "max": "*", "digit": 3}, "0.25"),
        "opacity": ("float", {"min": 0.0, "max": 1.0, "digit": 2}, "1.0"),
    },
    "orbital": {
        "name": ("check", {}, "untitled"),
        "name_check": ("bool", {}, True),
        "name_actor": ("actor", {}, ""),
        "label": ("check", {}, "label"),
        "label_check": ("bool", {}, False),
        "label_actor": ("actor", {}, ""),
        "margin": ("int", {"min": 0, "max": "*"}, "3"),
        "position": ("list_float", {"shape": (3,), "var": [""], "digit": 4}, "[0,0,0]"),
        "cell": ("list_int", {"shape": (3,)}, "[0,0,0]"),
        "shape": ("math", {"var": ["x", "y", "z", "r"]}, "3z**2-r**2"),
        "surface": ("math", {"var": ["x", "y", "z", "r"]}, "3z**2-r**2"),
        "size": ("float", {"min": "*", "max": "*", "digit": 3}, "0.5"),
        "range": ("list_int", {"shape": (2, 2)}, "[[0,180],[0,360]]"),
        "color": ("color_both", {}, "Wistia"),
        "opacity": ("float", {"min": 0.0, "max": 1.0, "digit": 2}, "1.0"),
    },
    "stream": {
        "name": ("check", {}, "untitled"),
        "name_check": ("bool", {}, True),
        "name_actor": ("actor", {}, ""),
        "label": ("check", {}, "label"),
        "label_check": ("bool", {}, False),
        "label_actor": ("actor", {}, ""),
        "margin": ("int", {"min": 0, "max": "*"}, "3"),
        "position": ("list_float", {"shape": (3,), "var": [""], "digit": 4}, "[0,0,0]"),
        "cell": ("list_int", {"shape": (3,)}, "[0,0,0]"),
        "shape": ("math", {"var": ["x", "y", "z", "r"]}, "1"),
        "vector": ("math", {"shape": (3,), "var": ["x", "y", "z", "r"]}, "[x,y,z]"),
        "size": ("float", {"min": 0.0, "max": "*", "digit": 3}, "0.5"),
        "range": ("list_int", {"shape": (2, 2)}, "[[0,180],[0,360]]"),
        "division": ("list_int", {"shape": (2,)}, "[9,18]"),
        "length": ("float", {"min": 0.0, "max": "*", "digit": 3}, "0.1"),
        "width": ("float", {"min": 0.0, "max": "*", "digit": 3}, "0.01"),
        "offset": ("float", {"min": "*", "max": "*", "digit": 3}, "-0.43"),
        "abs_scale": ("check", {}, ""),
        "abs_scale_check": ("bool", {}, False),
        "color": ("color_both", {}, "coolwarm"),
        "component": ("combo", ["x", "y", "z", "abs"], "abs"),
        "shaft R": ("float", {"min": 0.0, "max": "*", "digit": 3}, "1.0"),
        "tip R": ("float", {"min": 0.0, "max": "*", "digit": 3}, "2.0"),
        "tip length": ("float", {"min": 0.0, "max": "*", "digit": 3}, "0.25"),
        "opacity": ("float", {"min": 0.0, "max": 1.0, "digit": 2}, "1.0"),
    },
    "line": {
        "name": ("check", {}, "untitled"),
        "name_check": ("bool", {}, True),
        "name_actor": ("actor", {}, ""),
        "label": ("check", {}, "label"),
        "label_check": ("bool", {}, False),
        "label_actor": ("actor", {}, ""),
        "margin": ("int", {"min": 0, "max": "*"}, "3"),
        "position": ("list_float", {"shape": (3,), "var": [""], "digit": 4}, "[0,0,0]"),
        "cell": ("[list_int]", {"shape": (3,)}, "[0,0,0]"),
        "direction": ("list_float", {"shape": (3,), "var": [""], "digit": 3}, "[0,0,1]"),
        "width": ("float", {"min": 0.0, "max": "*", "digit": 3}, "0.02"),
        "arrow1": ("check", {}, ""),
        "arrow1_check": ("bool", {}, False),
        "arrow2": ("check", {}, ""),
        "arrow2_check": ("bool", {}, False),
        "tip R": ("float", {"min": 0.0, "max": "*", "digit": 3}, "2.0"),
        "tip length": ("float", {"min": 0.0, "max": "*", "digit": 3}, "0.1"),
        "color": ("color", {}, "strawberry"),
        "cartesian": ("check", {}, ""),
        "cartesian_check": ("bool", {}, False),
        "opacity": ("float", {"min": 0.0, "max": 1.0, "digit": 2}, "1.0"),
    },
    "plane": {
        "name": ("check", {}, "untitled"),
        "name_check": ("bool", {}, True),
        "name_actor": ("actor", {}, ""),
        "label": ("check", {}, "label"),
        "label_check": ("bool", {}, False),
        "label_actor": ("actor", {}, ""),
        "margin": ("int", {"min": 0, "max": "*"}, "3"),
        "position": ("list_float", {"shape": (3,), "var": [""], "digit": 4}, "[0,0,0]"),
        "cell": ("list_int", {"shape": (3,)}, "[0,0,0]"),
        "normal": ("list_float", {"shape": (3,), "var": [""], "digit": 3}, "[0,0,1]"),
        "x_size": ("float", {"min": 0.0, "max": "*", "digit": 3}, "1.0"),
        "y_size": ("float", {"min": 0.0, "max": "*", "digit": 3}, "1.0"),
        "color": ("color", {}, "sky"),
        "width": ("float", {"min": 0.0, "max": "*", "digit": 3}, "2.0"),
        "grid": ("check", {}, ""),
        "grid_check": ("bool", {}, False),
        "grid_color": ("color", {}, "black"),
        "cartesian": ("check", {}, ""),
        "cartesian_check": ("bool", {}, True),
        "opacity": ("float", {"min": 0.0, "max": 1.0, "digit": 2}, "1.0"),
    },
    "circle": {
        "name": ("check", {}, "untitled"),
        "name_check": ("bool", {}, True),
        "name_actor": ("actor", {}, ""),
        "label": ("check", {}, "label"),
        "label_check": ("bool", {}, False),
        "label_actor": ("actor", {}, ""),
        "margin": ("int", {"min": 0, "max": "*"}, "3"),
        "position": ("list_float", {"shape": (3,), "var": [""], "digit": 4}, "[0,0,0]"),
        "cell": ("list_int", {"shape": (3,)}, "[0,0,0]"),
        "normal": ("list_float", {"shape": (3,), "var": [""], "digit": 3}, "[0,0,1]"),
        "size": ("float", {"min": 0.0, "max": "*", "digit": 3}, "0.5"),
        "color": ("color", {}, "salmon"),
        "width": ("float", {"min": 0.0, "max": "*", "digit": 3}, "2.0"),
        "edge": ("check", {}, ""),
        "edge_check": ("bool", {}, True),
        "edge_color": ("color", {}, "black"),
        "cartesian": ("check", {}, ""),
        "cartesian_check": ("bool", {}, True),
        "opacity": ("float", {"min": 0.0, "max": 1.0, "digit": 2}, "1.0"),
    },
    "torus": {
        "name": ("check", {}, "untitled"),
        "name_check": ("bool", {}, True),
        "name_actor": ("actor", {}, ""),
        "label": ("check", {}, "label"),
        "label_check": ("bool", {}, False),
        "label_actor": ("actor", {}, ""),
        "margin": ("int", {"min": 0, "max": "*"}, "3"),
        "position": ("list_float", {"shape": (3,), "var": [""], "digit": 4}, "[0,0,0]"),
        "cell": ("list_int", {"shape": (3,)}, "[0,0,0]"),
        "normal": ("list_float", {"shape": (3,), "var": [""], "digit": 3}, "[0,0,1]"),
        "size": ("float", {"min": 0.0, "max": "*", "digit": 3}, "0.5"),
        "width": ("float", {"min": 0.0, "max": "*", "digit": 3}, "0.15"),
        "color": ("color", {}, "cantaloupe"),
        "cartesian": ("check", {}, ""),
        "cartesian_check": ("bool", {}, True),
        "opacity": ("float", {"min": 0.0, "max": 1.0, "digit": 2}, "1.0"),
    },
    "ellipsoid": {
        "name": ("check", {}, "untitled"),
        "name_check": ("bool", {}, True),
        "name_actor": ("actor", {}, ""),
        "label": ("check", {}, "label"),
        "label_check": ("bool", {}, False),
        "label_actor": ("actor", {}, ""),
        "margin": ("int", {"min": 0, "max": "*"}, "3"),
        "position": ("list_float", {"shape": (3,), "var": [""], "digit": 4}, "[0,0,0]"),
        "cell": ("list_int", {"shape": (3,)}, "[0,0,0]"),
        "normal": ("list_float", {"shape": (3,), "var": [""], "digit": 4}, "[0,0,1]"),
        "x_size": ("float", {"min": 0.0, "max": "*", "digit": 3}, "0.5"),
        "y_size": ("float", {"min": 0.0, "max": "*", "digit": 3}, "0.4"),
        "z_size": ("float", {"min": 0.0, "max": "*", "digit": 3}, "0.3"),
        "color": ("color", {}, "cornflowerblue"),
        "cartesian": ("check", {}, ""),
        "cartesian_check": ("bool", {}, True),
        "opacity": ("float", {"min": 0.0, "max": 1.0, "digit": 2}, "1.0"),
    },
    "toroid": {
        "name": ("check", {}, "untitled"),
        "name_check": ("bool", {}, True),
        "name_actor": ("actor", {}, ""),
        "label": ("check", {}, "label"),
        "label_check": ("bool", {}, False),
        "label_actor": ("actor", {}, ""),
        "margin": ("int", {"min": 0, "max": "*"}, "3"),
        "position": ("list_float", {"shape": (3,), "var": [""], "digit": 4}, "[0,0,0]"),
        "cell": ("list_int", {"shape": (3,)}, "[0,0,0]"),
        "normal": ("list_float", {"shape": (3,), "var": [""], "digit": 4}, "[0,0,1]"),
        "size": ("float", {"min": 0.0, "max": "*", "digit": 3}, "0.5"),
        "width": ("float", {"min": 0.0, "max": "*", "digit": 3}, "0.15"),
        "x_scale": ("float", {"min": 0.0, "max": "*", "digit": 3}, "1.0"),
        "y_scale": ("float", {"min": 0.0, "max": "*", "digit": 3}, "1.0"),
        "z_scale": ("float", {"min": 0.0, "max": "*", "digit": 3}, "1.0"),
        "ring_shape": ("float", {"min": 0.0, "max": "*", "digit": 3}, "0.3"),
        "tube_shape": ("float", {"min": 0.0, "max": "*", "digit": 3}, "0.3"),
        "color": ("color", {}, "tan"),
        "cartesian": ("check", {}, ""),
        "cartesian_check": ("bool", {}, True),
        "opacity": ("float", {"min": 0.0, "max": 1.0, "digit": 2}, "1.0"),
    },
    "box": {
        "name": ("check", {}, "untitled"),
        "name_check": ("bool", {}, True),
        "name_actor": ("actor", {}, ""),
        "label": ("check", {}, "label"),
        "label_check": ("bool", {}, False),
        "label_actor": ("actor", {}, ""),
        "margin": ("int", {"min": 0, "max": "*"}, "3"),
        "position": ("list_float", {"shape": (3,), "var": [""], "digit": 4}, "[0,0,0]"),
        "cell": ("list_int", {"shape": (3,)}, "[0,0,0]"),
        "a1": ("list_float", {"shape": (3,), "var": [""], "digit": 4}, "[1,0,0]"),
        "a2": ("list_float", {"shape": (3,), "var": [""], "digit": 4}, "[0,1,0]"),
        "a3": ("list_float", {"shape": (3,), "var": [""], "digit": 4}, "[0,0,1]"),
        "width": ("float", {"min": 0.0, "max": "*", "digit": 3}, "2.0"),
        "edge": ("check", {}, ""),
        "edge_check": ("bool", {}, True),
        "edge_color": ("color", {}, "black"),
        "wireframe": ("check", {}, ""),
        "wireframe_check": ("bool", {}, False),
        "color": ("color", {}, "yellowgreen"),
        "cartesian": ("check", {}, ""),
        "cartesian_check": ("bool", {}, False),
        "opacity": ("float", {"min": 0.0, "max": 1.0, "digit": 2}, "1.0"),
    },
    "polygon": {
        "name": ("check", {}, "untitled"),
        "name_check": ("bool", {}, True),
        "name_actor": ("actor", {}, ""),
        "label": ("check", {}, "label"),
        "label_check": ("bool", {}, False),
        "label_actor": ("actor", {}, ""),
        "margin": ("int", {"min": 0, "max": "*"}, "3"),
        "position": ("list_float", {"shape": (3,), "var": [""], "digit": 4}, "[0,0,0]"),
        "cell": ("list_int", {"shape": (3,)}, "[0,0,0]"),
        "point": (
            "list_float",
            {"shape": (3, 0), "var": [""], "digit": 4},
            "[[0,0,0],[0.8,0,0],[0,0.6,0],[0,0,0.4],[0.6,0.6,0]]",
        ),
        "connectivity": ("list_int", {"shape": (0, 0)}, "[[0,1,4,2],[0,1,3],[1,4,3],[2,0,3],[2,3,4]]"),
        "width": ("float", {"min": 0.0, "max": "*", "digit": 3}, "2.0"),
        "edge": ("check", {}, ""),
        "edge_check": ("bool", {}, True),
        "edge_color": ("color", {}, "black"),
        "wireframe": ("check", {}, ""),
        "wireframe_check": ("bool", {}, False),
        "color": ("color", {}, "aluminum"),
        "cartesian": ("check", {}, ""),
        "cartesian_check": ("bool", {}, False),
        "opacity": ("float", {"min": 0.0, "max": 1.0, "digit": 2}, "1.0"),
    },
    "spline": {
        "name": ("check", {}, "untitled"),
        "name_check": ("bool", {}, True),
        "name_actor": ("actor", {}, ""),
        "label": ("check", {}, "label"),
        "label_check": ("bool", {}, False),
        "label_actor": ("actor", {}, ""),
        "margin": ("int", {"min": 0, "max": "*"}, "3"),
        "position": ("list_float", {"shape": (3,), "var": [""], "digit": 4}, "[0,0,0]"),
        "cell": ("list_int", {"shape": (3,)}, "[0,0,0]"),
        "point": ("list_float", {"shape": (3, 0), "var": [""], "digit": 4}, "[[0,0,0],[1,0,1],[0,1,2]]"),
        "width": ("float", {"min": 0.0, "max": "*", "digit": 3}, "0.01"),
        "n_interp": ("int", {"min": 0, "max": "*"}, "500"),
        "closed": ("check", {}, ""),
        "closed_check": ("bool", {}, False),
        "natural": ("check", {}, ""),
        "natural_check": ("bool", {}, True),
        "arrow1": ("check", {}, ""),
        "arrow1_check": ("bool", {}, False),
        "arrow2": ("check", {}, ""),
        "arrow2_check": ("bool", {}, False),
        "tip R": ("float", {"min": 0.0, "max": "*", "digit": 3}, "2.0"),
        "tip length": ("float", {"min": 0.0, "max": "*", "digit": 3}, "0.1"),
        "color": ("color", {}, "banana"),
        "cartesian": ("check", {}, ""),
        "cartesian_check": ("bool", {}, True),
        "opacity": ("float", {"min": 0.0, "max": 1.0, "digit": 2}, "1.0"),
    },
    "spline_t": {
        "name": ("check", {}, "untitled"),
        "name_check": ("bool", {}, True),
        "name_actor": ("actor", {}, ""),
        "label": ("check", {}, "label"),
        "label_check": ("bool", {}, False),
        "label_actor": ("actor", {}, ""),
        "margin": ("int", {"min": 0, "max": "*"}, "3"),
        "position": ("list_float", {"shape": (3,), "var": [""], "digit": 4}, "[0,0,0]"),
        "cell": ("list_int", {"shape": (3,)}, "[0,0,0]"),
        "point": ("math", {"shape": (3,), "var": ["t"]}, "[cos(2 pi t), sin(2 pi t), t/2]"),
        "t_range": ("list_float", {"shape": (3,), "var": [""], "digit": 4}, "[0,1,0.05]"),
        "width": ("float", {"min": 0.0, "max": "*", "digit": 3}, "0.01"),
        "n_interp": ("int", {"min": 0, "max": "*"}, "500"),
        "closed": ("check", {}, ""),
        "closed_check": ("bool", {}, False),
        "natural": ("check", {}, ""),
        "natural_check": ("bool", {}, True),
        "arrow1": ("check", {}, ""),
        "arrow1_check": ("bool", {}, False),
        "arrow2": ("check", {}, ""),
        "arrow2_check": ("bool", {}, False),
        "tip R": ("float", {"min": 0.0, "max": "*", "digit": 3}, "2.0"),
        "tip length": ("float", {"min": 0.0, "max": "*", "digit": 3}, "0.1"),
        "color": ("color", {}, "crimson"),
        "cartesian": ("check", {}, ""),
        "cartesian_check": ("bool", {}, True),
        "opacity": ("float", {"min": 0.0, "max": 1.0, "digit": 2}, "1.0"),
    },
    "text3d": {
        "name": ("check", {}, "untitled"),
        "name_check": ("bool", {}, True),
        "name_actor": ("actor", {}, ""),
        "label": ("check", {}, "label"),
        "label_check": ("bool", {}, False),
        "label_actor": ("actor", {}, ""),
        "margin": ("int", {"min": 0, "max": "*"}, "3"),
        "position": ("list_float", {"shape": (3,), "var": [""], "digit": 4}, "[0,0,0]"),
        "cell": ("list_int", {"shape": (3,)}, "[0,0,0]"),
        "text": ("str", {}, "text"),
        "size": ("float", {"min": 0.0, "max": "*", "digit": 3}, "0.3"),
        "view": ("list_float", {"shape": (3,), "var": [""], "digit": 4}, "[0,0,1]"),
        "depth": ("float", {"min": "*", "max": "*", "digit": 3}, "0.2"),
        "offset": ("float", {"min": "*", "max": "*", "digit": 3}, "[0,0,0]"),
        "color": ("color", {}, "iron"),
        "opacity": ("float", {"min": 0.0, "max": 1.0, "digit": 2}, "1.0"),
    },
    "isosurface": {
        "name": ("check", {}, "untitled"),
        "name_check": ("bool", {}, True),
        "name_actor": ("actor", {}, ""),
        "label": ("check", {}, "label"),
        "label_check": ("bool", {}, False),
        "label_actor": ("actor", {}, ""),
        "margin": ("int", {"min": 0, "max": "*"}, "3"),
        "position": ("list_float", {"shape": (3,), "var": [""], "digit": 4}, "[0,0,0]"),
        "cell": ("list_int", {"shape": (3,)}, "[0,0,0]"),
        "data": ("str", {}, ""),
        "value": ("list_float", {"shape": (0,), "var": [""], "digit": 4}, "[0.5]"),
        "surface": ("str", {}, ""),
        "color": ("color_both", {}, "white"),
        "color_range": ("list_float", {"shape": (2,), "var": [""], "digit": 3}, "[0,1]"),
        "opacity": ("float", {"min": 0.0, "max": 1.0, "digit": 2}, "0.8"),
    },
    "caption": {
        "name": ("check", {}, "untitled"),
        "name_check": ("bool", {}, True),
        "name_actor": ("actor", {}, ""),
        "label": ("hide", {}, ""),  # dummy.
        "label_check": ("hide", {}, ""),  # dummy.
        "label_actor": ("hide", {}, ""),  # dummy.
        "margin": ("int", {"min": 0, "max": "*"}, "3"),
        "position": ("list_float", {"shape": (3, 0), "var": [""], "digit": 4}, "[[0,0,0],[1,0,0],[1,1,0]]"),
        "cell": ("list_int", {"shape": (3,)}, "[0,0,0]"),
        "caption": ("str", {}, "[A,B,C]"),
        "size": ("int", {"min": 0, "max": "*"}, "18"),
        "bold": ("check", {}, ""),
        "bold_check": ("bool", {}, True),
        "color": ("color", {}, "black"),
    },
    "text2d": {
        "name": ("check", {}, "untitled"),
        "name_check": ("bool", {}, True),
        "name_actor": ("actor", {}, ""),
        "label": ("hide", {}, ""),  # dummy.
        "label_check": ("hide", {}, ""),  # dummy.
        "label_actor": ("hide", {}, ""),  # dummy.
        "margin": ("hide", {}, ""),  # dummy.
        "position": ("list_float", {"shape": (3,), "var": [""], "digit": 4}, "[0.02,0.95,0]"),  # z-comp. dummy.
        "cell": ("hide", {}, "[0,0,0]"),  # dummy.
        "caption": ("str", {}, "text"),
        "size": ("int", {"min": 0, "max": "*"}, "8"),
        "color": ("color", {}, "black"),
        "font": ("combo", ["arial", "times", "courier"], "arial"),
    },
}
