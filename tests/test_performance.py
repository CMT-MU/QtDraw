"""
Regression tests for the cost of adding objects (#190).
"""

import pytest

from qtdraw.core import pyvista_widget as pw


# ==================================================
@pytest.fixture
def count_actors(monkeypatch):
    counter = {"n": 0}
    original = pw.PyVistaWidget.actors

    def actors(self):
        counter["n"] += 1
        return original.fget(self)

    monkeypatch.setattr(pw.PyVistaWidget, "actors", property(actors))
    return counter


def row(widget, **values):
    data = dict(zip(widget._data["site"].header, widget._data["site"].column_default))
    data.update(values)
    return data


# ==================================================
def test_check_hide_does_not_read_actors_for_new_rows(widget, count_actors):
    count_actors["n"] = 0
    widget.check_hide(row(widget, name_check=True, label_check=False, name_actor="", label_actor=""))
    widget.check_hide(row(widget, name_check=False, label_check=False, name_actor="", label_actor=""))
    assert count_actors["n"] == 0


# ==================================================
def test_check_hide_reads_actors_once(widget, count_actors):
    widget.add_site(position="[0,0,0]", label="A")
    name = next(iter(widget.actors))
    count_actors["n"] = 0
    name_check, label_check = widget.check_hide(
        row(widget, name_check=False, label_check=False, name_actor=name, label_actor=name)
    )
    assert (name_check, label_check) == (False, False)
    assert count_actors["n"] == 1
    assert not widget.actors[name].GetVisibility()


# ==================================================
def test_adding_sites_does_not_scale_actor_reads(widget, count_actors):
    for i in range(5):
        widget.add_site(position=f"[{i/10},0,0]")
    before = count_actors["n"]
    for i in range(5, 25):
        widget.add_site(position=f"[{i/100},0,0]")
    per_site = (count_actors["n"] - before) / 20
    assert per_site == 0  # was one full actor dictionary per added site.
