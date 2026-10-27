# [QtDraw](https://cmt-mu.github.io/QtDraw/)

3D drawing tool especially for molecules and crystals based on [PyVista](https://docs.pyvista.org/) and [PySide6](https://doc.qt.io/qtforpython-6/index.html).
Drawings are associated with crystallographic symmetry operations provided by [MultiPie](https://github.com/CMT-MU/MultiPie).

- **Authors**: Hiroaki Kusunose

- **Installation**: QtDraw can be installed from PyPI using pip on Python >= 3.12:
  In order to use MathJax rendering for LaTeX, install playwright browser such as chromium.
    ```bash
    pip install qtdraw
    playwright install chromium  # on Linux, also run `playwright install-deps chromium`.
    ```

- **Shell commands**:
  - `qtdraw [filename]` : Open a QtDraw file (`.qtdw`, which may be omitted) or a material file (`.cif`, `.vesta`, `.xsf`).
  - `conv_qtdraw3 ver1_file[.qtdw]` : Convert a version-1 `.qtdw` file to version 3, written as `ver1_file_v3.qtdw` next to it.

- **Requirements**:
  - Symmetry operation supports are provided by [MultiPie](https://github.com/CMT-MU/MultiPie), which is installed together with QtDraw.
  - This project includes [MathJax](https://www.mathjax.org/), which is licensed under the Apache License 2.0.

- **Citing QtDraw and MultiPie**: If you are using QtDraw and/or MultiPie in your scientific research, please help our scientific visibility by citing our work:
    > Hiroaki Kusunose, Rikuto Oiwa, and Satoru Hayami, Symmetry-adapted modeling for molecules and crystals, Phys. Rev. B <b>107</b>, 195118 (2023).<br>
    > DOI: [https://doi.org/10.1103/PhysRevB.107.195118](https://doi.org/10.1103/PhysRevB.107.195118)

- **License**: QtDraw is distributed under the [Mozilla Public License version 2.0 (MPL v2)](https://mozilla.org/MPL/2.0/).
  Versions up to 3.2.0 were distributed under the MIT License. The bundled MathJax keeps its own license (Apache License 2.0).
