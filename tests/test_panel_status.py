"""
The panel and the View menu show the status set from Python, on the window or on the widget.
"""

import pytest

from gui_helpers import app  # noqa: F401  (fixture)


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


SETTERS = [
    ("set_crystal", ("hexagonal",), {"crystal": "hexagonal", "gamma": "120.00", "volume": "Volume 0.8660"}),
    ("set_origin", ([0.5, 0, 0],), {"origin": "[0.50,0.00,0.00]"}),
    ("set_unit_cell", ({"a": 2.0, "gamma": 100},), {"a": "2.0000", "gamma": "100.00", "volume": "Volume 1.9696"}),
    ("set_range", ([-1, -1, -1], [2, 2, 2]), {"lower": "[-1.00,-1.00,-1.00]", "upper": "[2.00,2.00,2.00]"}),
    ("set_clip", (True,), {"clip": True, "menu_toggle": ["parallel", "clip"]}),
    ("set_repeat", (True,), {"repeat": True, "menu_toggle": ["parallel", "repeat"]}),
    ("set_parallel_projection", (False,), {"parallel": False, "menu_toggle": []}),
    ("set_grid", (True,), {"grid": True, "menu_toggle": ["parallel", "grid"]}),
    ("set_bar", (True,), {"bar": True, "menu_toggle": ["parallel", "bar"]}),
    ("set_axis", ("off",), {"axis": "off", "menu_axis": ["off"]}),
    ("set_cell", ("off",), {"cell": "off", "menu_cell": ["off"]}),
]


# ==================================================
@pytest.mark.parametrize("target", ["window", "widget"])
@pytest.mark.parametrize("name, args, changed", SETTERS, ids=[s[0] for s in SETTERS])
def test_panel_shows_status_set_from_python(app, target, name, args, changed):
    before = panel(app)
    for key, value in changed.items():
        assert before[key] != value  # the test changes the panel.

    obj = app if target == "window" else app.pyvista_widget
    getattr(obj, name)(*args)

    assert panel(app) == before | changed


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
