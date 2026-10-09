"""
Undo history.

This module provides a list of document snapshots with a current position, for undo and redo.
"""


# ==================================================
class UndoHistory:
    # ==================================================
    def __init__(self, limit=50):
        """
        Undo history.

        Args:
            limit (int, optional): maximum number of undo steps.
        """
        self._limit = limit
        self._snapshots = []
        self._position = -1

    # ==================================================
    def reset(self, snapshot):
        """
        Start a new history.

        Args:
            snapshot (Any): first snapshot.
        """
        self._snapshots = [snapshot]
        self._position = 0

    # ==================================================
    def clear(self):
        """
        Empty the history.
        """
        self._snapshots = []
        self._position = -1

    # ==================================================
    def current(self):
        """
        Snapshot at the current position.

        Returns:
            - (Any) -- snapshot, None if the history is empty.
        """
        return self._snapshots[self._position] if self._snapshots else None

    # ==================================================
    def record(self, snapshot, same=None):
        """
        Record a snapshot after the current position.

        Args:
            snapshot (Any): snapshot.
            same (function, optional): same(a, b) -> bool, default is ==.

        Returns:
            - (bool) -- recorded ? (False if it is the same as the current snapshot)

        Note:
            - the snapshots after the current position (redo) are dropped.
        """
        if same is None:
            same = lambda a, b: a == b
        if self._snapshots and same(snapshot, self.current()):
            return False
        del self._snapshots[self._position + 1 :]
        self._snapshots.append(snapshot)
        del self._snapshots[: max(0, len(self._snapshots) - (self._limit + 1))]
        self._position = len(self._snapshots) - 1
        return True

    # ==================================================
    def map(self, func):
        """
        Replace every snapshot by func(snapshot), keeping the position.

        Args:
            func (function): func(snapshot) -> snapshot.
        """
        self._snapshots = [func(snapshot) for snapshot in self._snapshots]

    # ==================================================
    def can_undo(self):
        """
        Undo possible ?
        """
        return self._position > 0

    # ==================================================
    def can_redo(self):
        """
        Redo possible ?
        """
        return 0 <= self._position < len(self._snapshots) - 1

    # ==================================================
    def peek_undo(self):
        """
        Snapshot that undo restores (no move), None if not possible.
        """
        return self._snapshots[self._position - 1] if self.can_undo() else None

    # ==================================================
    def peek_redo(self):
        """
        Snapshot that redo restores (no move), None if not possible.
        """
        return self._snapshots[self._position + 1] if self.can_redo() else None

    # ==================================================
    def commit_undo(self):
        """
        Move the position back by one (after a successful restore).
        """
        if self.can_undo():
            self._position -= 1

    # ==================================================
    def commit_redo(self):
        """
        Move the position forward by one (after a successful restore).
        """
        if self.can_redo():
            self._position += 1
