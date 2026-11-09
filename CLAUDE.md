# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

QtDraw is a 3D drawing tool for molecules and crystals, built on PyVista/pyvistaqt (VTK) and PySide6. Crystallographic symmetry comes from [MultiPie](https://github.com/CMT-MU/MultiPie), which is a required dependency. Python >= 3.12.

## Branch workflow

- `main` is the default and release branch. Feature and fix branches start from `develop`, and their PRs target `develop` (`gh pr create --base develop`).
- After a PR merges, delete its branch (`gh pr merge --delete-branch`), pull `develop` and run the tests on it.
- The maintainer opens and merges the `develop` → `main` PR by hand. Never delete `develop`, so GitHub's "Automatically delete head branches" stays off.

## Commands

```bash
pip install -e ".[dev]"                      # black, pytest, pytest-qt, pytest-xdist, jupyter-book
playwright install chromium                  # MathJax rendering of LaTeX uses a headless Chromium
pytest -n auto                               # all tests (testpaths = tests), in parallel
pytest tests/test_undo.py::test_name -v      # one test
black --line-length 130 qtdraw tests         # formatting (line length set in pyproject.toml)
qtdraw [file]                                # run the app (.qtdw, or .cif / .vesta / .xsf)
make -C docs build                           # documentation (Jupyter Book); `upload` publishes to gh-pages
```

- `tests/conftest.py` sets `QT_QPA_PLATFORM=offscreen` and keeps QSettings and the MathJax SVG cache in temporary directories. Its autouse fixture **fails any test that leaves a window open**, because a leftover window crashes later off-screen tests on Linux/Mesa (#197). Close what a test opens.
- GUI tests check that the side panel matches the document after each test. Mark a test `@pytest.mark.panel_not_checked(reason)` only when it leaves the panel out of date on purpose (see `tests/gui_helpers.py`).
- Visual regression (`tests/test_visual.py`) compares against reference images in `tests/data/visual/<system>-vtk<version>/`. Without references for the current system the test is skipped. `QTDRAW_UPDATE_VISUAL=1` writes them (check them before committing), `QTDRAW_VISUAL_OUTPUT=<dir>` saves the images of failures, and `QTDRAW_VISUAL_REQUIRE=1` fails instead of skipping.
- File compatibility (`tests/test_file_compat.py`) checks old `.qtdw` files in `tests/data/compat/` against `expected.json`, which `make_expected.py` writes from the *released* version (see its docstring).
- `others/tests/` holds older manual and interactive scripts. pytest does not collect them.
- CI (`.github/workflows/test.yml`) runs on Ubuntu, macOS and Windows, plus a job pinned to the minimum PySide6/pyvista/pyvistaqt versions. Those minimums must stay in sync with `pyproject.toml`. It also installs the built wheel and sdist and runs `tests/install_check.py`. `release.yml` publishes to PyPI when a GitHub release is published. The tag must be `v` + `__version__` in `qtdraw/core/qtdraw_info.py`.

## Architecture

- **`core/pyvista_widget.py` — `PyVistaWidget(QtInteractor)`** is the drawing engine and the document. It can be used without the GUI (`PyVistaWidget(off_screen=True)`, or from Jupyter). Public methods `add_site`, `add_bond`, `add_vector`, … `add_isosurface`, `add_caption`, `add_text2d` add rows. `load`/`save` read and write `.qtdw` files. `mp_*` methods draw from MultiPie group data.
- **Data model.** Each object type has one `GroupModel` (`widget/group_model.py`, a two-level `QStandardItemModel`) in `self._data[object_type]`. Its columns, types, validation options and defaults come from `object_default` in `core/pyvista_widget_setting.py`. The first columns (name/check/actor, label/check/actor, margin, position, cell) are shared by all types; their indices are the `COLUMN_*` constants. Cell values are strings (e.g. `"[0,0,0]"`) and are parsed when plotted. **To add an object type or field**, edit `object_default`, add an `add_<type>` method and a `plot_data_<type>` method, and add the mesh builder in `util/basic_object.py`.
- **Rendering flow.** `GroupModel.dataModified` → `PyVistaWidget.plot_data` → `plot_data_<type>`, through a per-type `PlotSignal`. Actors are named from the model row. Bulk changes go through `_batch_render()` or the `@_batched` decorator, so that the scene renders once instead of once per object.
- **Table editing.** `widget/tab_group_view.py` / `group_view.py` / `delegate.py` / `validator.py` provide the per-type tables (opened with the `e` key) on top of the same models.
- **`core/qtdraw_app.py` — `QtDraw(Window)`** is the main window. It holds a `PyVistaWidget` and adds the menus, the side panel (unit cell, view, MultiPie tabs from `multipie/tab_*.py`), recent files, and unsaved-change checks. **Undo/redo** stores whole-document snapshots (`PyVistaWidget.document_snapshot()` / `restore_document()`) in `core/undo_history.py`. Changes are recorded after a short settle timer (`_settle`), and `_flush()` records pending edits before undo, save, load and close.
- **File format.** A `.qtdw` file is a Python dict literal, read with `ast.literal_eval` (`util/util.read_dict`), never `eval`/`exec`. Older versions are converted on load by `parser/converter.py`. The `conv_qtdraw3` CLI converts version-1 files. Isosurface grid data can live in separate files whose paths are relative to the drawing's directory. Material files (`.cif`, `.vesta`, `.xsf`) are read by `parser/read_material.py` (pymatgen) and its siblings.
- **LaTeX.** `widget/mathjax.py` renders labels to SVG with the bundled MathJax (`qtdraw/mathjax/`, Apache-2.0) in Playwright's Chromium, and caches the results on disk.
- **MultiPie integration** lives in `qtdraw/multipie/`. `multipie_group_list.py` is generated by `others/tools/create_group_list.py`; do not edit it by hand. `util/util.check_multipie()` reports whether MultiPie is usable, and the app degrades when it is not.
- `qtdraw/__init__.py` imports `QtDraw`, `PyVistaWidget` and the others lazily, so that `import qtdraw` does not load Qt.

## Conventions

- Source files start with the MPL-2.0 SPDX header (versions up to 3.2.0 were MIT).
- Docstrings use the Google style and feed the Sphinx/Jupyter Book API pages. Internal methods are marked `:meta private:`.
- Default document status, user preferences and widget details are `default_status`, `default_preference` and `widget_detail` in `pyvista_widget_setting.py`.
