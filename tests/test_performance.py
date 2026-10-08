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
def test_check_hide_hides_existing_name_and_label(widget, count_actors):
    from qtdraw.core.pyvista_widget_setting import COLUMN_NAME_ACTOR, COLUMN_LABEL_ACTOR

    widget.add_site(position="[0,0,0]", name="A", label="a")
    model = widget._data["site"]
    model.setData(model.index(0, 0).siblingAtColumn(model.header.index("label_check")), "True")
    stored = model.tolist()[0]
    name, label = stored[COLUMN_NAME_ACTOR], stored[COLUMN_LABEL_ACTOR]
    assert name and label and name != label
    assert widget.actors[name].GetVisibility() and widget.actors[label].GetVisibility()

    count_actors["n"] = 0
    result = widget.check_hide(row(widget, name_check=False, label_check=True, name_actor=name, label_actor=label))
    assert result == (False, False) and count_actors["n"] == 1
    assert not widget.actors[name].GetVisibility()
    assert not widget.actors[label].GetVisibility()


# ==================================================
def test_check_hide_without_label_and_removed_actor(widget, count_actors):
    # caption/text2d have no label: only the name actor is checked.
    count_actors["n"] = 0
    assert widget.check_hide(row(widget, name_check=True, name_actor="", label_actor="x"), no_label=True) == (True, True)
    assert count_actors["n"] == 0
    # an actor name that is no longer in the renderer is ignored.
    assert widget.check_hide(row(widget, name_check=False, name_actor="removed-actor", label_actor="")) == (False, False)
    assert count_actors["n"] == 1


# ==================================================
def test_adding_sites_does_not_scale_actor_reads(widget, count_actors):
    for i in range(5):
        widget.add_site(position=f"[{i/10},0,0]")
    before = count_actors["n"]
    for i in range(5, 25):
        widget.add_site(position=f"[{i/100},0,0]")
    per_site = (count_actors["n"] - before) / 20
    assert per_site == 0  # was one full actor dictionary per added site.


# ==================================================
def add_sites(widget, n):
    # half of the sites are outside the default range [0,1]^3.
    for i in range(n):
        widget.add_site(position=f"[{2 * i / n},0,0]", label=f"s{i}")
    model = widget._data["site"]
    col = model.header.index("label_check")
    for r in range(n):
        model.setData(model.index(r, col), "True")


def visible(widget):
    from qtdraw.core.pyvista_widget_setting import COLUMN_NAME_ACTOR, COLUMN_LABEL_ACTOR

    rows = widget._data["site"].tolist()
    return [
        (widget.actors[r[COLUMN_NAME_ACTOR]].GetVisibility(), widget.actors[r[COLUMN_LABEL_ACTOR]].GetVisibility()) for r in rows
    ]


# ==================================================
@pytest.mark.parametrize("n", [4, 16])
def test_clip_reads_actors_once(widget, count_actors, n):
    add_sites(widget, n)
    assert all(v == (True, True) for v in visible(widget))

    count_actors["n"] = 0
    widget.set_clip(True)
    assert count_actors["n"] == 1  # independent of the number of objects.
    shown = visible(widget)
    assert shown[: n // 2 + 1] == [(True, True)] * (n // 2 + 1)  # x <= 1 is inside.
    assert shown[n // 2 + 1 :] == [(False, False)] * (n - n // 2 - 1)

    count_actors["n"] = 0
    widget.set_clip(False)
    assert count_actors["n"] == 1
    assert all(v == (True, True) for v in visible(widget))


# ==================================================
@pytest.mark.parametrize("n", [4, 16])
def test_deselect_all_reads_actors_once(widget, count_actors, n):
    from qtdraw.core.pyvista_widget_setting import COLUMN_NAME_ACTOR

    add_sites(widget, n)
    names = [r[COLUMN_NAME_ACTOR] for r in widget._data["site"].tolist()]
    for name in names:
        widget.select_actor(name)
    assert all(widget.actors[name].prop.show_edges for name in names)

    count_actors["n"] = 0
    widget.deselect_actor_all()
    assert count_actors["n"] == 1
    assert not any(widget.actors[name].prop.show_edges for name in names)
    assert widget._selected_actor == {}


# ==================================================
def test_site_sphere_is_created_once_per_size(widget, monkeypatch):
    calls = []
    original = pw.create_sphere

    def spy(*args, **kwargs):
        calls.append((args, kwargs))
        return original(*args, **kwargs)

    monkeypatch.setattr(pw, "create_sphere", spy)
    pw._site_sphere.cache_clear()

    widget.add_site(position="[0,0,0]", size=0.1)
    widget.add_site(position="[1/2,0,0]", size=0.1)
    widget.add_site(position="[0,1/2,0]", size=0.2)
    assert len(calls) == 2  # one sphere per size.

    from qtdraw.core.pyvista_widget_setting import COLUMN_NAME_ACTOR

    meshes = [widget.actors[r[COLUMN_NAME_ACTOR]].mapper.dataset for r in widget._data["site"].tolist()]
    centers = [m.center for m in meshes]
    assert centers[0] != centers[1] != centers[2]  # each site is translated separately.
    assert meshes[0].n_points == meshes[1].n_points == meshes[2].n_points
    assert pw._site_sphere(0.1).center == pytest.approx((0, 0, 0))  # cached sphere is not moved.
