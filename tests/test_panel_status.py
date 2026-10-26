"""
The panel and the View menu show the status set from Python, on the window or on the widget.

Every test using the app fixture also checks at the end that the panel shows the status (gui_helpers.panel_out_of_date).
"""

import copy

import pytest

from gui_helpers import app  # noqa: F401  (fixture)
from qtdraw.core.pyvista_widget import PyVistaWidget
from qtdraw.core.pyvista_widget_setting import default_status
from qtdraw.core.qtdraw_app import QtDraw


def panel(app):
    """
    Values shown in the panel and the View menu.
    """
    checked = lambda actions: [value for value, act in actions.items() if act.isChecked()]
    return {
        "crystal": app.uc_combo_crystal.currentText(),
        "origin": app.uc_edit_origin.text(),
        "a": app.uc_edit_a.text(),
        "gamma": app.uc_edit_gamma.text(),
        "volume": app.uc_label_volume.text(),
        "lower": app.view_edit_lower.text(),
        "upper": app.view_edit_upper.text(),
        "view": [app.view_combo_a.currentText(), app.view_combo_b.currentText(), app.view_combo_c.currentText()],
        "clip": app.view_button_clip.isChecked(),
        "repeat": app.view_button_repeat.isChecked(),
        "parallel": app.view_button_parallel.isChecked(),
        "grid": app.view_button_grid.isChecked(),
        "bar": app.view_button_bar.isChecked(),
        "axis": app.view_combo_axis.currentText(),
        "cell": app.view_combo_cell.currentText(),
        "menu_toggle": checked(app.action_toggle),
        "menu_axis": checked(app.action_axis),
        "menu_cell": checked(app.action_cell),
    }


# setters changing the status shown in the panel: (name, args, values shown after the call).
SETTERS = [
    ("set_crystal", ("hexagonal",), {"crystal": "hexagonal", "gamma": "120.00", "volume": "Volume 0.8660"}),
    ("set_origin", ([0.5, 0, 0],), {"origin": "[0.50,0.00,0.00]"}),
    ("set_unit_cell", ({"a": 2.0, "gamma": 100},), {"a": "2.0000", "gamma": "100.00", "volume": "Volume 1.9696"}),
    ("set_range", ([-1, -1, -1], [2, 2, 2]), {"lower": "[-1.00,-1.00,-1.00]", "upper": "[2.00,2.00,2.00]"}),
    ("set_view", ([1, 1, 0],), {"view": ["1", "1", "0"]}),
    ("set_clip", (True,), {"clip": True, "menu_toggle": ["parallel", "clip"]}),
    ("set_repeat", (True,), {"repeat": True, "menu_toggle": ["parallel", "repeat"]}),
    ("set_parallel_projection", (False,), {"parallel": False, "menu_toggle": []}),
    ("set_grid", (True,), {"grid": True, "menu_toggle": ["parallel", "grid"]}),
    ("set_bar", (True,), {"bar": True, "menu_toggle": ["parallel", "bar"]}),
    ("set_axis", ("off",), {"axis": "off", "menu_axis": ["off"]}),
    ("set_cell", ("off",), {"cell": "off", "menu_cell": ["off"]}),
    (
        "set_property",
        ({"crystal": "cubic", "clip": True},),
        {"crystal": "cubic", "clip": True, "menu_toggle": ["parallel", "clip"]},
    ),
]

# setters of the window and the widget not changing the status shown in the panel, with the reason.
NOT_STATUS = {
    "set_model": "model name, shown in the window title",
    "set_view_index": "shows the view index in the panel",
    "set_additional_status": "values derived from the status, set by the setters",
    "set_camera_info": "camera, not in the status",
    "set_nonrepeat": "converts the objects, the status is not changed",
    "set_theme": "PyVista theme, not in the status",
    "set_light": "light of the preference",
    "set_latex": "LaTeX setting of the preference",
    "set_actor": "object data",
    "set_common_row_data": "object data",
    "set_isosurface_data": "object data",
}

# status shown in the panel.
SHOWN = [key for key in default_status if key != "model"]


def cases(classes):
    return [
        pytest.param(target, name, args, changed, id=f"{name}-{target}")
        for name, args, changed in SETTERS
        for target, cls in classes
        if hasattr(cls, name)
    ]


# ==================================================
@pytest.mark.parametrize("target, name, args, changed", cases([("window", QtDraw), ("widget", PyVistaWidget)]))
def test_panel_shows_status_set_from_python(app, target, name, args, changed):
    before = panel(app)
    for key, value in changed.items():
        assert before[key] != value  # the test changes the panel.

    obj = app if target == "window" else app.pyvista_widget
    getattr(obj, name)(*args)

    assert panel(app) == before | changed


# ==================================================
@pytest.mark.parametrize("target, name, args, changed", cases([("widget", PyVistaWidget)]))
def test_status_change_is_notified(widget, target, name, args, changed):
    shown = lambda: copy.deepcopy({key: widget._status[key] for key in SHOWN})
    notified = []
    widget.status_changed.connect(lambda: notified.append(shown()))
    widget.camera_view.connect(lambda view: notified.append(shown()))
    before = shown()

    getattr(widget, name)(*args)

    assert shown() != before  # the test changes the status.
    assert notified and notified[-1] == shown()  # a panel following the notifications shows the final status.


# ==================================================
def test_every_setter_is_checked():
    setters = {name for cls in (QtDraw, PyVistaWidget) for name in vars(cls) if name.startswith("set_")}
    checked = {name for name, _, _ in SETTERS}
    assert setters - checked - NOT_STATUS.keys() == set(), "add a case to SETTERS, or the reason to NOT_STATUS"
    assert (checked | NOT_STATUS.keys()) - setters == set(), "remove the setters that no longer exist"
    assert checked & NOT_STATUS.keys() == set()


# ==================================================
def test_shown_without_applying_again(app, monkeypatch):
    pvw = app.pyvista_widget
    calls = []
    for name in ["set_crystal", "set_unit_cell", "set_origin", "set_range", "set_clip", "set_repeat", "set_bar"]:
        original = getattr(pvw, name)
        monkeypatch.setattr(pvw, name, lambda *a, f=original, n=name, **k: (calls.append(n), f(*a, **k))[1])

    pvw.set_crystal("cubic")
    pvw.set_bar(True)
    assert calls == ["set_crystal", "set_unit_cell", "set_bar"]  # the panel does not set them again.
