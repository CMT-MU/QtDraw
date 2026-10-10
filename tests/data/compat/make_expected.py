"""
Write expected.json: what a version of QtDraw reads from the drawings in this directory.

Run it with the released version, e.g. from a checkout of `main`:

    git worktree add /tmp/qtdraw-release main
    PYTHONPATH=/tmp/qtdraw-release QT_QPA_PLATFORM=offscreen python tests/data/compat/make_expected.py
"""

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))  # tests/, for compat_helpers.

from qtdraw.widget.qt_event_util import get_qt_application  # noqa: E402

get_qt_application()
import qtdraw  # noqa: E402
from qtdraw.core.pyvista_widget import PyVistaWidget  # noqa: E402
from compat_helpers import contents  # noqa: E402

print("QtDraw:", qtdraw.__file__)
cwd = os.getcwd()
expected = {}
for source in sorted(HERE.glob("*.qtdw")):
    work = Path(tempfile.mkdtemp())
    shutil.copy(source, work / source.name)
    widget = PyVistaWidget(off_screen=True)
    widget.load(str(work / source.name))
    os.chdir(cwd)  # older versions change the current directory when loading.
    expected[source.name] = contents(widget)
    widget.close()
(HERE / "expected.json").write_text(json.dumps(expected, indent=1, sort_keys=True) + "\n")
print("written", len(expected), "drawings")
os._exit(0)
