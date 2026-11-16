# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2021- The QtDraw developers
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""
Several rows selected in the data table are removed at once (#262), also by the Delete key, and by Backspace on
macOS (#258).
"""

import pytest
from PySide6.QtCore import QItemSelection, QItemSelectionModel, Qt
from PySide6.QtTest import QTest

import qtdraw.widget.group_view as group_view
from gui_helpers import app  # noqa: F401  (fixture)
from qtdraw.core.pyvista_widget_setting import COLUMN_NAME, COLUMN_POSITION


# ==================================================
def table(widget):
    return widget._tab_group_view.view["site"]


def sites(widget):
    return sorted((row[COLUMN_NAME], row[COLUMN_POSITION]) for row in widget.get_data_dict().get("site", []))


def select(view, *rows):
    """
    Select rows, each a top-level row or (top-level row, row of an object in it).
    """
    model = view.model()
    view.clear_selection()
    for row in rows:
        index = model.index(row[1], 0, model.index(row[0], 0)) if isinstance(row, tuple) else model.index(row, 0)
        if index.parent().isValid():
            view.expand(index.parent())
        view.selectionModel().select(QItemSelection(index, index), QItemSelectionModel.Select | QItemSelectionModel.Rows)


@pytest.fixture
def drawing(widget):
    widget.add_site(name="A", position="[0,0,0]")
    widget.add_site(name="B", position="[1,0,0]")  # group B of three objects.
    widget.add_site(name="B", position="[2,0,0]")
    widget.add_site(name="B", position="[3,0,0]")
    widget.add_site(name="C", position="[4,0,0]")  # group C of two objects.
    widget.add_site(name="C", position="[5,0,0]")
    widget.add_site(name="D", position="[6,0,0]")
    return widget


# ==================================================
@pytest.mark.parametrize(
    "rows, left",
    [
        ([0, 3], ["[1,0,0]", "[2,0,0]", "[3,0,0]", "[4,0,0]", "[5,0,0]"]),  # two single objects.
        ([(1, 0), (1, 2)], ["[0,0,0]", "[2,0,0]", "[4,0,0]", "[5,0,0]", "[6,0,0]"]),  # objects in a group.
        ([(2, 1)], ["[0,0,0]", "[1,0,0]", "[2,0,0]", "[3,0,0]", "[4,0,0]", "[6,0,0]"]),  # a group of two: one left.
        ([(2, 0), (2, 1)], ["[0,0,0]", "[1,0,0]", "[2,0,0]", "[3,0,0]", "[6,0,0]"]),  # all objects: the group.
        ([1, (1, 1)], ["[0,0,0]", "[4,0,0]", "[5,0,0]", "[6,0,0]"]),  # a group and an object in it.
        ([0, (1, 1), (2, 0), 3], ["[1,0,0]", "[3,0,0]", "[5,0,0]"]),  # mixed.
    ],
)
def test_delete_key_removes_selected_rows(drawing, rows, left):
    view = table(drawing)
    select(view, *rows)
    QTest.keyClick(view, Qt.Key_Delete)
    assert [p for _, p in sites(drawing)] == left
    assert not view.selectionModel().selectedRows()


# ==================================================
def test_menu_removes_selected_rows(drawing):
    view = table(drawing)
    select(view, 0, 3)
    view.remove_row()  # "remove" in the menu.
    assert [n for n, _ in sites(drawing)] == ["B", "B", "B", "C", "C"]


# ==================================================
def test_group_left_with_one_object_keeps_its_name(drawing):
    view = table(drawing)
    select(view, (2, 0))
    QTest.keyClick(view, Qt.Key_Delete)
    assert ("C", "[5,0,0]") in sites(drawing) and ("C", "[4,0,0]") not in sites(drawing)
    assert view.model().rowCount(view.model().index(2, 0)) == 0  # a single row now.


# ==================================================
def test_delete_key_without_selection_does_nothing(drawing):
    view = table(drawing)
    before = sites(drawing)
    view.clear_selection()
    QTest.keyClick(view, Qt.Key_Delete)
    assert sites(drawing) == before


# ==================================================
@pytest.mark.parametrize("platform, removed", [("darwin", True), ("linux", False), ("win32", False)])
def test_backspace_removes_only_on_macos(drawing, monkeypatch, platform, removed):
    monkeypatch.setattr(group_view.sys, "platform", platform)
    view = table(drawing)
    select(view, 0)
    QTest.keyClick(view, Qt.Key_Backspace)
    assert (("A", "[0,0,0]") not in sites(drawing)) == removed


# ==================================================
def test_several_selected_rows_are_highlighted(drawing):
    view = table(drawing)
    select(view, 0, 3)
    assert len(drawing._selected_actor) == 2  # both objects, not only the first.
    select(view, 1)  # a group of three objects.
    assert len(drawing._selected_actor) == 3


# ==================================================
def test_menu_names_the_number_of_rows(drawing, monkeypatch):
    shown = []
    monkeypatch.setattr(group_view.QMenu, "popup", lambda menu, *a: shown.append([a.text() for a in menu.actions()]))
    view = table(drawing)
    select(view, 0, 3)
    view.context_menu(view.visualRect(view.model().index(0, 0)).center())
    assert "remove 2 rows" in shown[-1]


# ==================================================
def test_removal_of_several_rows_is_one_undo_step(app):
    w = app.pyvista_widget
    for name, x in [("A", 0), ("B", 1), ("B", 2), ("C", 3)]:
        w.add_site(name=name, position=f"[{x},0,0]")
    app._modified_timer.stop()
    app._settle()
    before = sites(w)

    view = table(w)
    select(view, 0, (1, 0), 2)
    QTest.keyClick(view, Qt.Key_Delete)
    app._modified_timer.stop()
    app._settle()
    assert sites(w) == [("B", "[2,0,0]")]

    app.undo()  # all of them come back at once.
    assert sites(w) == before
