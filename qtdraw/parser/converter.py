"""
Converter for QtDraw ver. 1.

This module contains the converter for version 1 format.
"""

import copy
from qtdraw.core.pyvista_widget_setting import default_status, default_preference
from qtdraw.multipie.plugin_multipie_setting import space_group_list, point_group_list, crystal_list
from qtdraw.multipie.plugin_multipie_setting import default_status as multipie_default
from qtdraw import __version__


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
    setting = dic["setting"]
    camera = {
        "position": [2.495208, 2.99401, 1.497604],
        "viewup": [-0.186248, -0.23281, 0.954521],
        "focal_point": [0.5, 0.5, 0.5],
        "angle": 30.0,
        "clipping_range": [1.68102, 5.450085],
        "distance": 3.346065,
        "scale": 0.866025,
    }
    update_camera = {
        "position": list(setting["camera.position"]),
        "viewup": list(setting["camera.up"]),
        "focal_point": list(setting["camera.focus"]),
    }
    camera.update(update_camera)

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
    Get multipie info.

    Args:
        dic (dict): read multipie info.

    Returns:
        - (dict) -- updated multipie info.
    """
    type_str = {0: "Q", 1: "G", 2: "T", 3: "M"}
    type_str1 = {0: "Q,G", 1: "T,M"}

    multipie = copy.deepcopy(multipie_default)
    multipie["plus"] = {}
    if "multipie" in dic.keys():
        old = dic["multipie"]
        multipie["version"] = old["version"]

        # main panel.
        g_type, crystal, group = old["main"]["group"]
        crystal = crystal_list[crystal]
        if g_type == 0:
            tag = space_group_list[crystal][group]
        else:
            tag = point_group_list[crystal][group]
        if tag.count(" ") > 0:
            tag = tag.split(" ")[1]
        multipie["group"]["group"] = tag

        multipie["group"]["irrep1"] = 0
        multipie["group"]["irrep2"] = 0
        multipie["group"]["irrep"] = 0

        multipie["group"]["vc_wyckoff"] = 0

        # tab1.
        multipie["object"]["site"] = old["tab1"]["site"][0]

        multipie["object"]["bond"] = old["tab1"]["bond"][0]

        vector, v_type = old["tab1"]["vector"]
        multipie["object"]["vector"] = vector
        multipie["object"]["vector_type"] = type_str[v_type]

        orbital, o_type = old["tab1"]["orbital"]
        multipie["object"]["orbital"] = orbital
        multipie["object"]["orbital_type"] = type_str[o_type]

        harmonics, h_type, h_rank, _ = old["tab1"]["harmonics"]
        multipie["object"]["harmonics_type"] = type_str[h_type]
        multipie["object"]["harmonics_rank"] = h_rank
        multipie["object"]["harmonics"] = harmonics

        multipie["object"]["wyckoff"] = old["tab1"]["wyckoff"][0]

        # tab2.
        site = old["tab2"]["site"][0]
        multipie["basis"]["site"] = site

        bond = old["tab2"]["bond"][0]
        multipie["basis"]["bond"] = bond

        vector, v_type, v_samb_type, _, v_lc, v_mod_type, v_mod = old["tab2"]["vector"]
        multipie["basis"]["vector_type"] = type_str[v_type]
        multipie["basis"]["vector"] = vector
        multipie["basis"]["vector_samb_type"] = type_str[v_samb_type]
        multipie["basis"]["vector_lc"] = v_lc
        multipie["basis"]["vector_modulation_type"] = type_str1[v_mod_type]
        multipie["basis"]["vector_modulation"] = v_mod

        orbital, o_type, o_rank, o_samb_type, _, o_lc, o_mod_type, o_mod = old["tab2"]["orbital"]
        multipie["basis"]["orbital_type"] = type_str[o_type]
        multipie["basis"]["orbital_rank"] = o_rank
        multipie["basis"]["orbital"] = orbital
        multipie["basis"]["orbital_samb_type"] = type_str[o_samb_type]
        multipie["basis"]["orbital_lc"] = o_lc
        multipie["basis"]["orbital_modulation_type"] = type_str1[o_mod_type]
        multipie["basis"]["orbital_modulation"] = o_mod

        hopping = old["tab2"]["hopping"][0]
        multipie["basis"]["hopping"] = hopping

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
    widget._data["site"].block_update_widget(True)
    for row in dic["site"]:
        d = dict(zip(old_setting["site"], row))
        widget.add_site(
            0.07 * float(d["size"]), d["color"], d["opacity"], d["position"], d["cell"], d["name"], d["label"], d["space"]
        )
    widget._data["site"].block_update_widget(False)

    widget._data["bond"].block_update_widget(True)
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
    widget._data["bond"].block_update_widget(False)

    widget._data["vector"].block_update_widget(True)
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
    widget._data["vector"].block_update_widget(False)

    widget._data["orbital"].block_update_widget(True)
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
    widget._data["orbital"].block_update_widget(False)

    comp_str = {0: "x", 1: "y", 2: "z", 3: "abs"}
    widget._data["stream"].block_update_widget(True)
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
    widget._data["stream"].block_update_widget(False)

    widget._data["plane"].block_update_widget(True)
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
    widget._data["plane"].block_update_widget(False)

    widget._data["box"].block_update_widget(True)
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
    widget._data["box"].block_update_widget(False)

    widget._data["polygon"].block_update_widget(True)
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
    widget._data["polygon"].block_update_widget(False)

    widget._data["text3d"].block_update_widget(True)
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
    widget._data["text3d"].block_update_widget(False)

    widget._data["spline"].block_update_widget(True)
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
    widget._data["spline"].block_update_widget(False)

    widget._data["spline_t"].block_update_widget(True)
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
    widget._data["spline_t"].block_update_widget(False)

    widget._data["caption"].block_update_widget(True)
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
    widget._data["caption"].block_update_widget(False)

    font_str = {0: "arial", 1: "courier", 2: "times"}
    widget._data["text2d"].block_update_widget(True)
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
    widget._data["text2d"].block_update_widget(False)

    data = widget.get_data_dict()

    return data


# ==================================================
def convert_version2(dic, widget):
    """
    Converter from ver.1 to ver. 2.

    Args:
        dic (dict): ver.1 dict.
        widget (PyVistaWidget): PyVistaWidget.

    Returns:
        - (dict) -- all data dict in ver. 2.
    """
    # all data.
    all_data = {
        "version": __version__,
        "data": get_data(dic, widget),
        "status": get_status(dic),
        "preference": get_preference(dic),
        "camera": get_camera(dic),
    }
    all_data["status"].update({"multipie": get_multipie(dic)})

    return all_data
