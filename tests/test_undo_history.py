"""
Tests for the undo history (#182).
"""

from qtdraw.core.undo_history import UndoHistory


def test_record_undo_redo():
    h = UndoHistory()
    h.reset("a")
    assert not h.can_undo() and not h.can_redo()
    assert h.record("b") and h.record("c")
    assert h.current() == "c" and h.can_undo()
    assert h.peek_undo() == "b" and h.current() == "c"  # peek does not move.
    h.commit_undo()
    assert h.current() == "b" and h.can_redo() and h.peek_redo() == "c"
    h.commit_redo()
    assert h.current() == "c" and not h.can_redo()


def test_same_snapshot_is_not_recorded():
    h = UndoHistory()
    h.reset("a")
    assert not h.record("a")
    assert not h.can_undo()


def test_record_after_undo_drops_redo_tail():
    h = UndoHistory()
    h.reset("a")
    h.record("b")
    h.record("c")
    h.commit_undo()  # at "b".
    assert not h.record("b")  # unchanged after undo: redo is kept.
    assert h.can_redo()
    assert h.record("d")
    assert not h.can_redo() and h.current() == "d" and h.peek_undo() == "b"


def test_limit_drops_oldest():
    h = UndoHistory(limit=3)
    h.reset(0)
    for i in range(1, 6):
        h.record(i)
    steps = 0
    while h.can_undo():
        h.commit_undo()
        steps += 1
    assert steps == 3 and h.current() == 2


def test_custom_equality():
    h = UndoHistory()
    h.reset({"x": 1})
    assert not h.record({"x": 1}, same=lambda a, b: a["x"] == b["x"])


def test_clear():
    h = UndoHistory()
    h.reset("a")
    h.record("b")
    h.clear()
    assert h.current() is None and not h.can_undo() and not h.can_redo()
    assert h.record("c")  # recording after clear starts a new history.
    assert h.current() == "c" and not h.can_undo()
