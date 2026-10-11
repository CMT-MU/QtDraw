"""
Images of fixed drawings compared with reference images (visual regression).

A drawing is built in a PyVistaWidget, as in QtDraw, and its actors and camera are rendered by an off-screen
pyvista plotter of a fixed size (the off-screen Qt platform does not render with VTK on every system).
Rendering differs between systems and VTK versions, so the reference images are kept per system and VTK
version in tests/data/visual/<system>-vtk<major.minor>/; without them, the tests are skipped.

- QTDRAW_UPDATE_VISUAL=1 writes the reference images of this system (check them before committing).
- QTDRAW_VISUAL_OUTPUT=<dir> receives the image of a failing or skipped test, with the reference and their difference
  for a failing one (CI keeps them as an artifact).
- QTDRAW_VISUAL_REQUIRE=1 fails, instead of skipping, without reference images (CI with pinned versions).
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
from qtdraw.core.pyvista_widget_setting import widget_detail
from qtdraw.util.util import check_multipie

EXAMPLES = Path(__file__).resolve().parents[1] / "docs" / "src" / "examples"
SYSTEM = f"{sys.platform}-vtk{vtk.vtkVersion.GetVTKMajorVersion()}.{vtk.vtkVersion.GetVTKMinorVersion()}"
REFERENCE = Path(__file__).resolve().parent / "data" / "visual" / SYSTEM
SIZE = (800, 600)
ERROR = 500.0  # pyvista.compare_images error above which images differ (pyvista's own default for tests).
UPDATE = os.environ.get("QTDRAW_UPDATE_VISUAL") == "1"
REQUIRE = os.environ.get("QTDRAW_VISUAL_REQUIRE") == "1"
OUTPUT = os.path.abspath(os.environ["QTDRAW_VISUAL_OUTPUT"]) if os.environ.get("QTDRAW_VISUAL_OUTPUT") else None


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
LARGER_ERROR = {"sample_parallel_grid": 1000.0}  # many grid labels: text rendering differs a little between machines.


def render(widget):
    """
    Image of the actors and the camera of a widget, rendered off screen.
    """
    plotter = pv.Plotter(off_screen=True, window_size=SIZE)
    try:
        plotter.set_background(widget.background_color)
        if widget_detail["anti_aliasing"]:
            plotter.enable_anti_aliasing()
        plotter.remove_all_lights()
        for light in widget.renderer.lights:
            plotter.add_light(light.copy())
        for name, actor in widget.renderer.actors.items():
            plotter.add_actor(actor, name=name, reset_camera=False)
        plotter.camera_position = widget.camera_position
        plotter.camera.parallel_projection = widget.camera.parallel_projection
        plotter.camera.parallel_scale = widget.camera.parallel_scale
        return plotter.screenshot(None, return_img=True)
    finally:
        plotter.close()


def on_background(image, background):
    """
    RGB image as seen on the background color (an RGBA image is composited with its alpha).
    """
    image = np.asarray(image).astype(float)
    color = np.asarray(pv.Color(background).float_rgb) * 255
    if image.shape[-1] == 4:
        alpha = image[..., 3:] / 255
        return image[..., :3] * alpha + color * (1 - alpha)
    return image


def drawn_fraction(image, background):
    """
    Fraction of the pixels that differ from the background color.
    """
    color = np.asarray(pv.Color(background).float_rgb) * 255
    return float(np.any(np.abs(on_background(image, background) - color) > 8, axis=-1).mean())


def keep(image, name, background, reference=None):
    if OUTPUT:
        directory = Path(OUTPUT, SYSTEM)
        directory.mkdir(parents=True, exist_ok=True)
        Image.fromarray(image).save(directory / f"{name}.png")
        if reference is not None:
            Image.fromarray(reference).save(directory / f"{name}-reference.png")
            difference = np.abs(on_background(image, background) - on_background(reference, background))
            Image.fromarray(np.round(difference).astype(np.uint8)).save(directory / f"{name}-difference.png")


# ==================================================
@pytest.mark.parametrize("name", [pytest.param(name, marks=needs_multipie if name in NEEDS_MULTIPIE else ()) for name in SCENES])
def test_drawing_looks_as_before(qapp, tmp_path, monkeypatch, name):
    monkeypatch.chdir(tmp_path)
    widget = PyVistaWidget(off_screen=True)
    try:
        widget.window_size = SIZE  # 2D texts are placed in pixels of the widget.
        SCENES[name](widget, tmp_path)
        image = render(widget)
        background = widget.background_color
    finally:
        widget.close()
    if drawn_fraction(image, background) <= 0.01:  # also before an update.
        keep(image, name, background)
        pytest.fail(f"{name} is (almost) empty.")

    reference = REFERENCE / f"{name}.png"
    if UPDATE:
        reference.parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(image).save(reference)
        return
    if not reference.exists():
        keep(image, name, background)
        if REQUIRE:
            pytest.fail(f"no reference image for {SYSTEM}.")
        pytest.skip(f"no reference image for {SYSTEM}.")
    expected = np.asarray(Image.open(reference))
    error = pv.compare_images(image, expected)
    limit = LARGER_ERROR.get(name, ERROR)
    print(f"{name}: error {error:.0f} (limit {limit:.0f})")
    if error > limit:
        keep(image, name, background, expected)
    assert error <= limit, f"{name} differs from {reference} (error {error:.0f} > {limit:.0f})."


def test_drawn_fraction_ignores_transparent_pixels():
    image = np.zeros((10, 10, 4), dtype=np.uint8)  # black, but fully transparent.
    assert drawn_fraction(image, "white") == 0.0
    image[:5, :, 3] = 255  # the upper half is drawn in black.
    assert drawn_fraction(image, "white") == 0.5
    assert drawn_fraction(np.full((10, 10, 3), 255, dtype=np.uint8), "white") == 0.0
