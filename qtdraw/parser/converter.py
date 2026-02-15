"""
Converter for QtDraw ver. 1.

This module contains the converter for version 1 format.
"""

import copy

from qtdraw.core.pyvista_widget_setting import default_status, default_preference
from qtdraw.core.qtdraw_info import __version__

from qtdraw.multipie.multipie_setting import default_status as multipie_status


# ==================================================
def to_bool(b):
    """
    Convert from string to bool.

    Args:
        b (str): string of bool.

    Returns:
        - (bool) -- converted value.
    """
    if type(b) == str:
        return b == "True"
    else:
        return b


# old setting keyword (text -> text2d).
# ==================================================
old_setting = {
    "site": ["name", "ON", "label", "cell", "position", "size", "color", "opacity", "space", "D", "AD", "AL"],
    "bond": [
        "name",
        "ON",
        "label",
        "cell",
        "position",
        "vector",
        "width",
        "color",
        "color2",
        "opacity",
        "space",
        "D",
        "AD",
        "AL",
    ],
    "vector": [
        "name",
        "ON",
        "label",
        "cell",
        "position",
        "vector",
        "length",
        "width",
        "offset",
        "color",
        "opacity",
        "space",
        "D",
        "AD",
        "AL",
    ],
    "orbital": [
        "name",
        "ON",
        "label",
        "cell",
        "position",
        "shape",
        "surface",
        "size",
        "scale",
        "theta0",
        "theta1",
        "phi0",
        "phi1",
        "color",
        "opacity",
        "space",
        "D",
        "AD",
        "AL",
    ],
    "stream": [
        "name",
        "ON",
        "label",
        "cell",
        "position",
        "shape",
        "vector",
        "size",
        "v_size",
        "width",
        "scale",
        "theta",
        "phi",
        "theta0",
        "theta1",
        "phi0",
        "phi1",
        "color",
        "component",
        "opacity",
        "space",
        "D",
        "AD",
        "AL",
    ],
    "plane": ["name", "ON", "label", "cell", "position", "normal", "x", "y", "color", "opacity", "space", "D", "AD", "AL"],
    "box": [
        "name",
        "ON",
        "label",
        "cell",
        "position",
        "a1",
        "a2",
        "a3",
        "edge",
        "wireframe",
        "width",
        "color",
        "opacity",
        "space",
        "D",
        "AD",
        "AL",
    ],
    "polygon": [
        "name",
        "ON",
        "label",
        "cell",
        "position",
        "point",
        "connection",
        "edge",
        "wireframe",
        "width",
        "color",
        "opacity",
        "space",
        "D",
        "AD",
        "AL",
    ],
    "text3d": [
        "name",
        "ON",
        "label",
        "cell",
        "position",
        "text",
        "size",
        "depth",
        "normal",
        "offset",
        "color",
        "opacity",
        "space",
        "D",
        "AD",
        "AL",
    ],
    "spline": [
        "name",
        "ON",
        "label",
        "cell",
        "position",
        "point",
        "width",
        "n_interp",
        "closed",
        "natural",
        "color",
        "opacity",
        "space",
        "D",
        "AD",
        "AL",
    ],
    "spline_t": [
        "name",
        "ON",
        "label",
        "cell",
        "position",
        "expression",
        "t_range",
        "width",
        "n_interp",
        "closed",
        "natural",
        "color",
        "opacity",
        "space",
        "D",
        "AD",
        "AL",
    ],
    "caption": ["name", "cell", "position", "caption", "space", "size", "bold", "color", "D", "AD"],
    "text": ["name", "position", "relative", "caption", "size", "color", "font", "D", "AD"],
}


# ==================================================
def get_status(dic):
    """
    Get update status.

    Args:
        dic (dict): read status.

    Returns:
        - (dict) -- updated status.
    """
    axis_type = {0: "on", 1: "axis", 2: "off"}
    cell_mode = {0: "single", 1: "all", 2: "off"}
    setting = dic["setting"]

    status = copy.deepcopy(default_status)
    update_status = {
        "model": setting["model"],
        "origin": setting["origin"],
        "cell": setting["cell"],
        "crystal": setting["crystal"],
        "clip": setting["clip"],
        "repeat": setting["repeat"],
        "lower": setting["view_range"][0],
        "upper": setting["view_range"][1],
        "view": setting["view"],
        "axis_type": axis_type[setting["axis_mode"]],
        "cell_mode": cell_mode[setting["cell_mode"]],
    }
    status.update(update_status)

    return status


# ==================================================
def get_camera(dic):
    """
    Get camera info.

    Args:
        dic (dict): read camera info.

    Returns:
        - (dict) -- updated camera info.
    """
    camera = {
        "position": [-2.0497042434983572, -1.6247535362486305, 0.07504929275027392],
        "focal_point": [0.5, 0.5, 0.5],
        "viewup": [0.0, 0.0, 0.1],
        "angle": 30.0,
        "scale": 8660254037844386,
        "clipping_range": [1.7962230464194453, 5.305068101988363],
    }
    if "camera" in dic["setting"].keys():
        camera.update(dic["setting"]["camera"])

    if "distance" in camera.keys():
        del camera["distance"]

    return camera


# ==================================================
def get_preference(dic):
    """
    Get update preference.

    Args:
        dic (dict): read preference.

    Returns:
        - (dict) -- updated preference.
    """
    pref = dic["preference"]
    preference = copy.deepcopy(default_preference)
    amode = {"xyz": "[x,y,z]", "abc": "[a,b,c]", "abc*": "[a*,b*,c*]"}
    update_preference = {
        "light": {
            "type": "ver1",
            "intensity": pref["light.intensity"],
            "pbr": pref["light.pbr"],
            "metallic": pref["light.metallic"],
            "roughness": pref["light.roughness"],
        },
        "label": {
            "font": pref["label.font"],
            "size": pref["label.size"],
            "bold": pref["label.bold"],
            "italic": pref["label.italic"],
            "color": pref["label.color"],
        },
        "cell": {"line_width": pref["cell.width"], "color": pref["cell.color"], "opacity": pref["cell.opacity"]},
        "axis": {
            "size": pref["axis.size"],
            "bold": pref["axis.bold"],
            "italic": pref["axis.italic"],
            "label": amode[pref["axis.type"]],
        },
    }
    for key, value in update_preference.items():
        preference[key].update(value)

    return preference


# ==================================================
def get_multipie(dic):
    """
    Get multipie info. (v2->v3)

    Args:
        dic (dict): read multipie info.

    Returns:
        - (dict) -- updated multipie info.
    """
    old = dic["multipie"]
    if len(old) == 0:
        return {}
    multipie = copy.deepcopy(multipie_status)

    if "group" in old.keys():
        multipie["group"]["tag"] = old["group"]["group"]

    if "object" in old.keys():
        for k in ["site", "bond", "vector_type", "vector", "orbital_type", "orbital"]:
            if k in old["object"].keys():
                multipie["object"][k] = old["object"][k]

    if "basis" in old.keys():
        for k in ["site", "bond", "vector_type", "vector", "orbital_type", "orbital_rank", "orbital"]:
            if k in old["basis"].keys():
                multipie["basis"][k] = old["basis"][k]

    multipie["version"] = "2.0.0"

    return multipie


# ==================================================
def get_data(dic, widget):
    """
    Get updated data.

    Args:
        dic (dict): read data.
        widget (PyVistaWidget): PyVistaWidget.

    Returns:
        - (dict) -- updated data.
    """
    for row in dic["site"]:
        d = dict(zip(old_setting["site"], row))
        widget.add_site(
            0.07 * float(d["size"]), d["color"], d["opacity"], d["position"], d["cell"], d["name"], d["label"], d["space"]
        )

    for row in dic["bond"]:
        d = dict(zip(old_setting["bond"], row))
        widget.add_bond(
            d["vector"],
            0.018 * float(d["width"]),
            d["color"],
            d["color2"],
            False,
            d["opacity"],
            d["position"],
            d["cell"],
            d["name"],
            d["label"],
            d["space"],
        )

    for row in dic["vector"]:
        d = dict(zip(old_setting["vector"], row))
        widget.add_vector(
            d["vector"],
            d["length"],
            0.02 * float(d["width"]),
            d["offset"],
            d["color"],
            True,
            None,
            None,
            None,
            d["opacity"],
            d["position"],
            d["cell"],
            d["name"],
            d["label"],
            d["space"],
        )

    for row in dic["orbital"]:
        d = dict(zip(old_setting["orbital"], row))
        size = -0.3 * abs(float(d["size"])) if d["scale"] else 0.3 * abs(float(d["size"]))
        widget.add_orbital(
            d["shape"],
            d["surface"],
            size,
            [[d["theta0"], d["theta1"]], [d["phi0"], d["phi1"]]],
            d["color"],
            d["opacity"],
            d["position"],
            d["cell"],
            d["name"],
            d["label"],
            d["space"],
        )

    comp_str = {0: "x", 1: "y", 2: "z", 3: "abs"}
    for row in dic["stream"]:
        d = dict(zip(old_setting["stream"], row))
        size = -float(d["size"]) if d["scale"] else float(d["size"])
        widget.add_stream(
            d["shape"],
            d["vector"],
            size,
            [[d["theta0"], d["theta1"]], [d["phi0"], d["phi1"]]],
            [d["theta"], d["phi"]],
            d["v_size"],
            0.004 * float(d["width"]),
            None,
            to_bool(d["scale"]),
            d["color"],
            comp_str[d["component"]],
            None,
            None,
            None,
            d["opacity"],
            d["position"],
            d["cell"],
            d["name"],
            d["label"],
            d["space"],
        )

    for row in dic["plane"]:
        d = dict(zip(old_setting["plane"], row))
        widget.add_plane(
            d["normal"],
            d["x"],
            d["y"],
            d["color"],
            None,
            None,
            None,
            False,
            d["opacity"],
            d["position"],
            d["cell"],
            d["name"],
            d["label"],
            d["space"],
        )

    for row in dic["box"]:
        d = dict(zip(old_setting["box"], row))
        widget.add_box(
            d["a1"],
            d["a2"],
            d["a3"],
            d["width"],
            None,
            None,
            to_bool(d["wireframe"]),
            d["color"],
            False,
            d["opacity"],
            d["position"],
            d["cell"],
            d["name"],
            d["label"],
            d["space"],
        )

    for row in dic["polygon"]:
        d = dict(zip(old_setting["polygon"], row))
        widget.add_polygon(
            d["point"],
            d["connection"],
            d["width"],
            to_bool(d["edge"]),
            None,
            to_bool(d["wireframe"]),
            d["color"],
            False,
            d["opacity"],
            d["position"],
            d["cell"],
            d["name"],
            d["label"],
            d["space"],
        )

    for row in dic["text3d"]:
        d = dict(zip(old_setting["text3d"], row))
        widget.add_text3d(
            d["text"],
            0.04 * float(d["size"]),
            d["normal"],
            0.3 * float(d["depth"]),
            d["offset"],
            d["color"],
            d["opacity"],
            d["position"],
            d["cell"],
            d["name"],
            d["label"],
            d["space"],
        )

    for row in dic["spline"]:
        d = dict(zip(old_setting["spline"], row))
        widget.add_spline(
            d["point"],
            0.01 * float(d["width"]),
            d["n_interp"],
            to_bool(d["closed"]),
            to_bool(d["natural"]),
            None,
            None,
            None,
            None,
            d["color"],
            False,
            d["opacity"],
            d["position"],
            d["cell"],
            d["name"],
            d["label"],
            d["space"],
        )

    for row in dic["spline_t"]:
        d = dict(zip(old_setting["spline_t"], row))
        widget.add_spline_t(
            d["expression"],
            d["t_range"],
            0.01 * float(d["width"]),
            d["n_interp"],
            to_bool(d["closed"]),
            to_bool(d["natural"]),
            None,
            None,
            None,
            None,
            d["color"],
            False,
            d["opacity"],
            d["position"],
            d["cell"],
            d["name"],
            d["label"],
            d["space"],
        )

    for row in dic["caption"]:
        d = dict(zip(old_setting["caption"], row))
        caption = "[" + ",".join(d["caption"]) + "]"
        widget.add_caption(
            caption,
            d["size"],
            to_bool(d["bold"]),
            d["color"],
            d["position"],
            d["cell"],
            d["name"],
            d["space"],
        )

    font_str = {0: "arial", 1: "courier", 2: "times"}
    for row in dic["text"]:
        d = dict(zip(old_setting["text"], row))
        widget.add_text2d(
            d["caption"],
            d["size"],
            d["color"],
            font_str[d["font"]],
            d["position"] + [0],
            d["name"],
        )

    data = widget.get_data_dict()

    return data


# ==================================================
def convert_version3(dic, ver, widget):
    """
    Converter from ver.1/2 to ver. 3.

    Args:
        dic (dict): ver.1/2 dict.
        ver (int): major version.
        widget (PyVistaWidget): PyVistaWidget.

    Returns:
        - (dict) -- all data dict in ver. 3.
    """
    all_data = {}
    if ver < 2:  # v1 -> v3.
        # all data.
        all_data = {
            "version": __version__,
            "data": get_data(dic, widget),
            "status": get_status(dic),
            "preference": get_preference(dic),
            "camera": get_camera(dic),
        }
    elif ver < 3:  # v2 -> v3.
        all_data = dic
        if "multipie" in dic["status"].keys():
            all_data["status"]["multipie"] = get_multipie(dic["status"])
    else:
        all_data = dic

    return all_data
