"""
Check an installed QtDraw package (not the source tree).

Run it with the Python of an environment where the package is installed, from a directory outside the source tree:

    python -I tests/install_check.py [--mathjax]

With --mathjax, LaTeX must be drawn by MathJax (the browser of playwright is installed), not as plain text.
"""

import os
import sys
import subprocess
import tempfile
from importlib import metadata
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def check(condition, message):
    if not condition:
        sys.exit(f"install check failed: {message}")
    print(f"ok: {message}")


def main():
    mathjax = "--mathjax" in sys.argv[1:]

    import qtdraw

    package = Path(qtdraw.__file__).resolve().parent
    check("site-packages" in package.parts, f"qtdraw is imported from the installed package ({package})")
    check(metadata.version("qtdraw") == qtdraw.__version__, f"version of the package is {qtdraw.__version__}")
    for file in ["core/qtdraw.png", "mathjax/es5/tex-svg-full.js"]:
        check((package / file).is_file(), f"data file {file} is installed")

    bin = Path(sys.executable).parent
    for script in ["qtdraw", "conv_qtdraw3"]:
        ret = subprocess.run([str(bin / script), "--help"], capture_output=True, text=True)
        check(ret.returncode == 0 and "Usage:" in ret.stdout, f"command {script} runs")

    import numpy as np
    from PySide6.QtCore import QEvent
    from qtdraw import PyVistaWidget, QtDraw, get_qt_application
    from qtdraw.parser.xsf import create_data
    from qtdraw.widget.mathjax import MathJaxSVG
    from qtdraw.widget.qt_event_util import ExceptionHook

    app = get_qt_application()

    with tempfile.TemporaryDirectory() as directory:
        os.chdir(directory)

        converter = MathJaxSVG(cache_dir=Path(directory) / "svg_cache")  # no cached SVG from another installation.
        svg, size = converter.convert("$x^2$")
        if mathjax:
            check(converter.available and "<svg" in svg, "LaTeX is drawn by MathJax")
        converter.close()

        errors = []  # exceptions in Qt slots (e.g. drawing) do not stop the script.

        def hook(kind, value, traceback):
            errors.append(repr(value))
            sys.__excepthook__(kind, value, traceback)

        sys.excepthook = hook
        ExceptionHook.hook = lambda self, *exc: hook(*exc)  # the main window sets its hook (an error dialog).

        widget = PyVistaWidget(off_screen=True)
        for name in [
            "site", "bond", "vector", "orbital", "stream", "line", "plane", "circle", "torus", "ellipsoid",
            "toroid", "box", "polygon", "spline", "spline_t", "text3d", "caption", "text2d",
        ]:  # fmt: skip
            getattr(widget, f"add_{name}")()
        widget.add_site(position="[1/2,0,0]", size=0.2, color="red", name="other")
        widget.add_text3d("$x^2$", position="[0,1/2,0]")
        grid = create_data([5, 5, 5], [0, 0, 0], np.eye(4), True, lambda x, y, z: x + y + z, None)
        widget.add_isosurface(data=("grid", grid), value="[1.5]")
        widget.mp_set_group("D6h")
        widget.render()
        check(not errors, f"objects are drawn without errors {errors}")
        check(all_drawn(widget), "every object has its actor")

        first, second = Path(directory) / "a.qtdw", Path(directory) / "b.qtdw"
        widget.save(str(first))
        widget.clear_data()
        widget.load(str(first))
        widget.render()
        widget.save(str(second))
        check(not errors and all_drawn(widget), f"a saved drawing is drawn again {errors}")
        check(contents(first) == contents(second), "a saved drawing is read without changes")
        widget.close()

        window = QtDraw(filename=str(first))
        app.processEvents()
        window.pyvista_widget.save(str(Path(directory) / "c.qtdw"))
        check(not errors and all_drawn(window.pyvista_widget), f"the main window draws a file {errors}")
        # only the objects: the main window also sets the cell to the crystal of the group, and the camera to its size.
        check(contents(Path(directory) / "c.qtdw")["data"] == contents(first)["data"], "the main window reads a file")
        window.close()
        app.sendPostedEvents(None, QEvent.DeferredDelete)  # widgets deleted later, as the event loop would.
        app.processEvents()
        check(not errors, f"the main window is closed without errors {errors}")


def contents(file):
    """
    Contents of a saved drawing, except the model name (taken from the file name).
    """
    from qtdraw.util.util import read_dict

    data = read_dict(str(file))
    del data["status"]["model"]
    return data


def all_drawn(widget):
    """
    Has every object its actor in the scene?
    """
    from qtdraw.core.pyvista_widget_setting import COLUMN_NAME_ACTOR

    actors = widget.renderer.actors
    names = {
        (kind, row): model.index(row, COLUMN_NAME_ACTOR).data()
        for kind, model in widget._data.items()
        for row in range(model.rowCount())
    }
    missing = [key for key, name in names.items() if name not in actors]
    kinds = {kind for kind, row in names}
    if missing or kinds != set(widget._data):
        print(f"objects without actor: {missing}, types without objects: {set(widget._data) - kinds}")
    return kinds == set(widget._data) and not missing


if __name__ == "__main__":
    main()
