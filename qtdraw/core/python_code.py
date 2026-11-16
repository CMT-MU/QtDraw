# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2021- The QtDraw developers
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""
Python code of a drawing.

This module writes the current state of a drawing (objects, unit cell, range and view, MultiPie group) as Python
code that draws the same with the QtDraw API (#290). The code is made from the state, not from a log of operations.
"""

from qtdraw.core.pyvista_widget_setting import default_status, object_default

SKIPPED_TYPES = ["actor", "check", "hide"]  # columns not given to add_* (actors, dummy columns of check boxes).


# ==================================================
def _is_true(value):
    """
    Value of a check box (a bool, or its text in a table).

    :meta private:
    """
    return value is True or str(value).strip().lower() in ("true", "1")


# ==================================================
def _value(value, column_type):
    """
    Python literal of a cell value.

    Args:
        value (str): value in the table.
        column_type (str): type of the column.

    Returns:
        - (str) -- Python literal.

    :meta private:
    """
    if column_type == "bool":
        return repr(_is_true(value))
    if column_type in ("int", "float"):
        try:
            number = int(value) if column_type == "int" else float(value)
            return repr(number)
        except (TypeError, ValueError):  # e.g. an expression: kept as text.
            pass
    return repr(str(value))


# ==================================================
def object_arguments(object_type, row):
    """
    Keyword arguments of add_* for a row of the data table, only those that differ from the defaults.

    Args:
        object_type (str): object type.
        row (list): row data.

    Returns:
        - (list) -- [(argument, Python literal)].
    """
    columns = object_default[object_type]
    data = dict(zip(columns.keys(), row))
    args = []

    # name and label first (their columns are check boxes of the table).
    for column in ("name", "label"):
        column_type, _, default = columns[column]
        if column_type == "check" and str(data[column]) != str(default):
            args.append((column, repr(str(data[column]))))
    label_given = any(k == "label" for k, _ in args)

    for column, (column_type, _, default) in columns.items():
        if column_type in SKIPPED_TYPES or column in ("name", "label"):
            continue
        value = data[column]
        if column == "name_check":
            if not _is_true(value):
                args.append(("show", "False"))
        elif column == "label_check":
            # with a label, add_* follows the preference ("label", "default_check") of the window that runs the
            # code, which may differ: written in any case.
            if label_given or _is_true(value) != _is_true(default):
                args.append(("show_label", repr(_is_true(value))))
        elif column_type == "bool":  # e.g. cartesian_check: the argument cartesian.
            if _is_true(value) != _is_true(default):
                args.append((column.removesuffix("_check"), repr(_is_true(value))))
        elif str(value) != str(default):
            args.append((column.replace(" ", "_"), _value(value, column_type)))
    return args


# ==================================================
def python_code(widget, in_memory=()):
    """
    Python code that draws the current state of a drawing with the QtDraw API.

    Args:
        widget (PyVistaWidget): drawing.
        in_memory (iterable, optional): names of isosurface data given without a file (not written).

    Returns:
        - (str) -- Python code.

    Note:
        - the objects, the unit cell, the range, repeat and clip, the view settings, the model name and the MultiPie
          group are written; the camera (zoom and rotation), the preferences and the MultiPie dialog are not.
        - the objects drawn by MultiPie are written as add_* of each object.
        - with repeat, only the objects of the home cell are written (repeat makes the others).
    """
    status = widget._status
    lines = ["import sys", "", "from qtdraw import QtDraw", "", "win = QtDraw()"]

    def call(method, *args):
        lines.append(f"win.{method}({', '.join(args)})")

    if status["model"] != default_status["model"]:
        call("set_model", repr(status["model"]))

    # MultiPie group first: it sets the crystal and the unit cell of the group, which are set below.
    if widget._mp_data is not None:
        tag = widget._mp_data.status["group"]["tag"]
        try:
            tag = widget._mp_data.group.info.tag or tag  # its name, e.g. "D6h^1" for "SG:191".
        except Exception:  # not in this MultiPie: the tag.
            pass
        call("mp_set_group", repr(tag))

    # unit cell.
    if status["crystal"]:
        call("set_crystal", repr(status["crystal"]))
    cell = {k: v for k, v in status["cell"].items()}
    if cell != default_status["cell"] or widget._mp_data is not None:
        call("set_unit_cell", repr(cell))
    if list(status["origin"]) != default_status["origin"]:
        call("set_origin", repr(str(list(status["origin"]))))

    # objects.
    # with repeat, the objects of the home cell are written, and set_repeat() at the end repeats them again.
    data = widget.get_data_dict(home_cell=status["repeat"])
    skipped = []
    for object_type in object_default:
        rows = data.get(object_type, [])
        if rows:
            lines += ["", f"# {object_type}."]
        for row in rows:
            args = object_arguments(object_type, row)
            if object_type == "isosurface":
                file = dict(zip(object_default[object_type].keys(), row))["data"]
                if not file or file in in_memory:
                    skipped.append(f"# isosurface '{row[0]}' is not written: its data is not in a file.")
                    continue
            call(f"add_{object_type}", *(f"{k}={v}" for k, v in args))
    lines += skipped and [""] + skipped or []

    # range, repeat and clip.
    view = []
    if list(status["lower"]) != default_status["lower"] or list(status["upper"]) != default_status["upper"]:
        view.append(f"win.set_range({str(list(status['lower']))!r}, {str(list(status['upper']))!r})")
    for key, method in [("repeat", "set_repeat"), ("clip", "set_clip")]:
        if status[key] != default_status[key]:
            view.append(f"win.{method}({status[key]!r})")
    # view.
    for key, method in [
        ("parallel_projection", "set_parallel_projection"),
        ("grid", "set_grid"),
        ("bar", "set_bar"),
        ("axis_type", "set_axis"),
        ("cell_mode", "set_cell"),
    ]:
        if status[key] != default_status[key]:
            view.append(f"win.{method}({status[key]!r})")
    if list(status["view"]) != default_status["view"]:
        view.append(f"win.set_view({list(status['view'])!r})")
    if view:
        lines += ["", "# range and view."] + view

    lines += [
        "",
        'if "ipykernel" not in sys.modules:  # in a script, keep the window open (not needed in Jupyter).',
        "    win.exec()",
        "",
    ]
    return "\n".join(lines)
