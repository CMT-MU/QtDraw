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
    original = {name: widget.actors[name].prop.edge_color for name in names}
    for name in names:
        widget.select_actor(name)
    assert all(widget.actors[name].prop.show_edges for name in names)

    count_actors["n"] = 0
    widget.deselect_actor_all()
    assert count_actors["n"] == 1
    assert not any(widget.actors[name].prop.show_edges for name in names)
    assert all(widget.actors[name].prop.edge_color == original[name] for name in names)
    assert widget._selected_actor == {}


# ==================================================
def test_site_sphere_is_created_once_per_size(widget, monkeypatch, request):
    import numpy as np
    from qtdraw.core.pyvista_widget_setting import COLUMN_NAME_ACTOR
    from qtdraw.util.basic_object import create_sphere

    calls = []

    def spy(*args, **kwargs):
        calls.append((args, kwargs))
        return create_sphere(*args, **kwargs)

    monkeypatch.setattr(pw, "create_sphere", spy)
    pw._site_sphere.cache_clear()
    request.addfinalizer(pw._site_sphere.cache_clear)  # the cache is shared by all widgets.
    widget.set_crystal("hexagonal")
    widget.set_unit_cell({"a": 2.0, "c": 3.0})
    assert not np.allclose(widget.A_matrix, np.eye(4))  # positions are transformed.

    sites = [("[0,0,0]", 0.1), ("[1/2,0,0]", 0.1), ("[0,1/2,1/4]", 0.2)]
    for position, size in sites:
        widget.add_site(position=position, size=size)
    assert len(calls) == 2  # one sphere per size.

    def mesh(i):
        return widget.actors[widget._data["site"].tolist()[i][COLUMN_NAME_ACTOR]].mapper.dataset

    # each site is the sphere of its size, translated to its position.
    for i, (position, size) in enumerate(sites):
        expected = create_sphere(radius=size)
        shift = pw.convert_str_vector(vector=position, A=widget.A_matrix)
        assert np.allclose(mesh(i).points, expected.points + shift)
        assert np.array_equal(mesh(i).faces, expected.faces)

    # changing one site does not change other sites or the cached sphere.
    cached = pw._site_sphere(0.1).points.copy()
    other = mesh(1).points.copy()
    mesh(0).points *= 2
    assert np.array_equal(pw._site_sphere(0.1).points, cached)
    assert np.array_equal(mesh(1).points, other)
    widget.add_site(position="[0,0,1/2]", size=0.1)
    assert np.allclose(mesh(3).points, create_sphere(radius=0.1).points + pw.convert_str_vector("[0,0,1/2]", A=widget.A_matrix))


# ==================================================
@pytest.fixture
def count_renderer_actors(monkeypatch):
    import pyvista

    counter = {"n": 0}
    original = pyvista.Renderer.actors

    def actors(self):
        counter["n"] += 1
        return original.fget(self)

    monkeypatch.setattr(pyvista.Renderer, "actors", property(actors))
    return counter


# ==================================================
@pytest.mark.parametrize("n", [4, 16])
def test_clear_reads_actors_independent_of_rows(widget, count_renderer_actors, n):
    widget.add_bond()
    add_sites(widget, n)
    count_renderer_actors["n"] = 0
    widget.clear_data()
    assert count_renderer_actors["n"] <= 8  # not once or more per object.


# ==================================================
def test_clear_removes_object_and_label_actors_only(widget):
    others = set(widget.renderer.actors)  # axes, cell, etc.
    add_sites(widget, 4)
    widget.add_caption()
    widget.add_text2d()
    widget.add_bond()
    assert set(widget.renderer.actors) - others  # objects and labels are drawn.

    widget.clear_data()

    assert set(widget.renderer.actors) == others
    assert widget._actor_object_type == {}


# ==================================================
def test_clear_removes_suffixed_actors_but_not_similar_names(widget):
    import pyvista

    from qtdraw.core.pyvista_widget_setting import COLUMN_NAME_ACTOR

    widget.add_site(name="A")
    name = widget._data["site"].tolist()[0][COLUMN_NAME_ACTOR]
    child = widget.add_mesh(pyvista.Sphere(), name=f"{name}-extra")  # removed with name, as remove_actor(name).
    similar = widget.add_mesh(pyvista.Sphere(), name=f"{name}ish")  # another actor.

    widget.clear_data()

    actors = widget.renderer.actors
    assert f"{name}-extra" not in actors and child not in actors.values()
    assert actors[f"{name}ish"] is similar
    assert all(model.tolist() == [] for model in widget._data.values())


# ==================================================
def test_clear_failure_resets_flags(widget, monkeypatch):
    add_sites(widget, 2)
    model = widget._data["site"]

    def fail():
        raise RuntimeError("broken")

    with monkeypatch.context() as m, pytest.raises(RuntimeError):
        m.setattr(model, "clear_data", fail)
        widget.clear_data()
    assert not widget._block_remove_actor and not widget._block_remove_isosurface

    widget.clear_data()  # works again.
    widget.add_site(name="B")
    others = set(widget.renderer.actors)
    widget.add_site(name="C")
    model.remove_row(model.index(1, 0))  # removal of one row removes its actor again.
    assert set(widget.renderer.actors) == others


# ==================================================
def test_clear_does_not_remove_actors_by_name(widget, monkeypatch):
    import pyvista

    add_sites(widget, 4)
    widget.add_bond()
    by_name = []
    original = pyvista.Renderer.remove_actor

    def remove_actor(self, actor, *args, **kwargs):
        if isinstance(actor, str):  # reads all actors for each call (in any pyvista version).
            by_name.append(actor)
        return original(self, actor, *args, **kwargs)

    monkeypatch.setattr(pyvista.Renderer, "remove_actor", remove_actor)
    widget.clear_data()
    assert by_name == []
