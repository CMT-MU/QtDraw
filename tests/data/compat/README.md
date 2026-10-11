# Drawings saved by older versions of QtDraw

Used by `tests/test_file_compat.py`. The files were taken from the history of this repository:

| file | version | commit | path |
|---|---|---|---|
| `v0_9_6_color_pattern.qtdw`, `v0_9_6_icon.qtdw` | 0.9.6 | c48310a | `docs/src/examples/` |
| `v1_1_0_sample_ver1.qtdw` | 1.1.0 | d1cc24e | `docs/src/examples/sample_ver1.qtdw` |
| `v2_0_0_*.qtdw` | 2.0.0 | b5c0095 | `docs/src/examples/` |
| `v2_3_0_*.qtdw` | 2.3.0 | aac3312 | `docs/src/examples/` |
| `v2_4_2_sample.qtdw` | 2.4.2 | aac3312 | `docs/src/examples/sample.qtdw` |

`expected.json` holds, for each file, what the released QtDraw 3.2.0 (`main`, 267b526) reads from it: the
objects, the status, the preferences, the MultiPie status and the camera (see `tests/compat_helpers.py`).
It was written by `make_expected.py` (see its docstring) with PySide6 6.11, pyvista 0.49, pyvistaqt 0.13 and
MultiPie 2 on macOS. Do not change the drawings: they record how drawings of earlier versions must be read.
Write `expected.json` again only with a released version, e.g. after an intended change of how they are read.
