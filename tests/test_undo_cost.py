"""
Size and time of undo snapshots (#182).
"""

import pickle
import time

from pathlib import Path

from qtdraw.parser.xsf import extract_data_xsf

from gui_helpers import app  # noqa: F401

EXAMPLES = Path(__file__).resolve().parents[1] / "docs" / "src" / "examples"


def test_snapshot_size_and_restore_time(app, capsys):
    pvw = app.pyvista_widget
    for i in range(1000):
        pvw.add_site(position=f"[{(i % 10) / 10},{(i // 10 % 10) / 10},{(i // 100) / 10}]")
    t = time.time()
    snap = pvw.document_snapshot()
    t_snap = time.time() - t
    size = len(pickle.dumps(snap["doc"]))
    t = time.time()
    pvw.restore_document(snap)
    t_restore = time.time() - t
    with capsys.disabled():
        print(f"\n1000 sites: snapshot {t_snap * 1000:.0f} ms, {size / 1024:.0f} KiB, restore {t_restore:.1f} s")
    assert size < 2 * 1024 * 1024  # 50 steps stay well below 100 MiB.


def test_replaced_grids_are_counted_once(app, capsys):
    pvw = app.pyvista_widget
    grid = extract_data_xsf(str(EXAMPLES / "Si.xsf"))
    for i in range(3):
        pvw.add_isosurface(data=("g", grid), value=[0.01])  # replaces the data under the same name.
        app._modified_timer.stop()
        app._settle()
    grids = {id(s["grids"]["g"]): s["grids"]["g"] for s in app._history._snapshots if "g" in s["grids"]}
    size = sum(len(pickle.dumps(g)) for g in grids.values())
    with capsys.disabled():
        print(f"\n3 replaced grids: {len(grids)} kept, {size / 1024 / 1024:.1f} MiB")
    assert len(grids) == 3  # one copy per replacement, shared by later snapshots.
