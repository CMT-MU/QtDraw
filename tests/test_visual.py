"""
Images of fixed drawings compared with reference images (visual regression).

A drawing is built in a PyVistaWidget, as in QtDraw, and its actors and camera are rendered by an off-screen
pyvista plotter of a fixed size (the off-screen Qt platform does not render with VTK on every system).
Rendering differs between systems and VTK versions, so the reference images are kept per system and VTK
version in tests/data/visual/<system>-vtk<major.minor>/; without them, the tests are skipped.

- QTDRAW_UPDATE_VISUAL=1 writes the reference images of this system (check them before committing).
- QTDRAW_VISUAL_OUTPUT=<dir> receives the image of a failing or skipped test (CI keeps it as an artifact).
"""

import os
import shutil
import sys
from pathlib import Path

import numpy as np
import pytest
import pyvista as pv
import vtk
from PIL import Image

from qtdraw.core.pyvista_widget import PyVistaWidget
from qtdraw.util.util import check_multipie

EXAMPLES = Path(__file__).resolve().parents[1] / "docs" / "src" / "examples"
SYSTEM = f"{sys.platform}-vtk{vtk.vtkVersion.GetVTKMajorVersion()}.{vtk.vtkVersion.GetVTKMinorVersion()}"
REFERENCE = Path(__file__).resolve().parent / "data" / "visual" / SYSTEM
SIZE = (800, 600)
ERROR = 500.0  # pyvista.compare_images error above which images differ (pyvista's own default for tests).
UPDATE = os.environ.get("QTDRAW_UPDATE_VISUAL") == "1"
OUTPUT = os.environ.get("QTDRAW_VISUAL_OUTPUT")


# ==================================================
def open_example(name):
    def build(widget, tmp_path):
        shutil.copy(EXAMPLES / name, tmp_path / name)
        widget.load(str(tmp_path / name))

    return build


def with_view(name, **settings):
    def build(widget, tmp_path):
        open_example(name)(widget, tmp_path)
        for key, value in settings.items():
            getattr(widget, f"set_{key}")(value)

    return build


def repeated(widget, tmp_path):
    open_example("color_pattern.qtdw")(widget, tmp_path)
    widget.set_range("[0,0,0]", "[2,2,1]")
    widget.set_repeat(True)
    widget.set_view()  # the whole repeated drawing.


def tellurium(widget, tmp_path):  # docs/src/examples/mp_Te.ipynb
    widget.mp_set_group("D3^4")
    widget.set_unit_cell({"a": 4.458, "c": 5.925})
    r = 0.2740
    widget.mp_add_site(f"[{r},0,1/3]", size=0.3)
    widget.mp_add_bond(f"[{r},0,1/3];[0,{r},2/3]", width=0.1)
    widget.mp_orbital_samb_list(f"[{r},0,1/3];[0,{r},2/3]", "Q", 2)
    widget.mp_add_orbital_samb("G01", size=1.0)
    widget.set_range([-0.5, -0.5, 0], [0.5, 0.5, 1.0])
    widget.set_repeat(True)
    widget.set_clip(True)
    widget.set_cell("off")
    widget.set_view()


needs_multipie = pytest.mark.skipif(not check_multipie(), reason="MultiPie is not installed.")

SCENES = {
    "sample": open_example("sample.qtdw"),
    "helimag": open_example("helimag.qtdw"),
    "color_pattern": open_example("color_pattern.qtdw"),
    "icon": open_example("icon.qtdw"),
    "si_cif": open_example("Si.cif"),
    "si_xsf_isosurface": open_example("Si.xsf"),
    "sample_parallel_grid": with_view("sample.qtdw", parallel_projection=True, grid=True),
    "sample_axis_full_cell_all": with_view("sample.qtdw", axis="full", cell="all"),
    "sample_view_x": with_view("sample.qtdw", view=[1, 0, 0]),
    "color_pattern_repeated": repeated,
    "tellurium": tellurium,
}
NEEDS_MULTIPIE = {"si_cif", "si_xsf_isosurface", "tellurium"}


def render(widget):
    """
    Image of the actors and the camera of a widget, rendered off screen.
    """
    plotter = pv.Plotter(off_screen=True, window_size=SIZE)
    try:
        plotter.set_background(widget.background_color)
        for name, actor in widget.renderer.actors.items():
            plotter.add_actor(actor, name=name, reset_camera=False)
        plotter.camera_position = widget.camera_position
        plotter.camera.parallel_projection = widget.camera.parallel_projection
        plotter.camera.parallel_scale = widget.camera.parallel_scale
        return plotter.screenshot(None, return_img=True)
    finally:
        plotter.close()


def keep(image, name):
    if OUTPUT:
        Path(OUTPUT, SYSTEM).mkdir(parents=True, exist_ok=True)
        Image.fromarray(image).save(Path(OUTPUT, SYSTEM, f"{name}.png"))


# ==================================================
@pytest.mark.parametrize("name", [pytest.param(name, marks=needs_multipie if name in NEEDS_MULTIPIE else ()) for name in SCENES])
def test_drawing_looks_as_before(qapp, tmp_path, monkeypatch, name):
    monkeypatch.chdir(tmp_path)
    widget = PyVistaWidget(off_screen=True)
    try:
        widget.window_size = SIZE  # 2D texts are placed in pixels of the widget.
        SCENES[name](widget, tmp_path)
        image = render(widget)
    finally:
        widget.close()

    reference = REFERENCE / f"{name}.png"
    if UPDATE:
        reference.parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(image).save(reference)
        return
    if not reference.exists():
        keep(image, name)
        pytest.skip(f"no reference image for {SYSTEM}.")
    error = pv.compare_images(image, np.asarray(Image.open(reference)))
    if error > ERROR:
        keep(image, name)
    assert error <= ERROR, f"{name} differs from {reference} (error {error:.0f} > {ERROR:.0f})."
    assert np.asarray(image).std() > 0  # not an empty image.
