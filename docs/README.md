# [QtDraw](https://cmt-mu.github.io/QtDraw/)

3D drawing tool especially for molecules and crystals based on [PyVista](https://docs.pyvista.org/) and [PySide6](https://doc.qt.io/qtforpython-6/index.html).
Drawings are associated with crystallographic symmetry operations provided by [MultiPie](https://github.com/CMT-MU/MultiPie).

- **Authors**: Hiroaki Kusunose

- **Installation**: QtDraw can be installed from PyPI using pip on Python >= 3.11:
  In order to use MathJax rendering for LaTeX, install playwright browser such as chromium.
    ```bash
    pip install qtdraw
    playwright instll chromium
    ```

- **Shell commands**:
  - `qtdraw [filename]` : Open QtDraw file.
  - `conv_qtdraw3 [ver1_file.qtdw]` : Convert Version 1 `.qtdw` file into this version (Version 3).

- **Requirements**:
  - [Optional] Symmetry operation supports are provided by [MultiPie](https://github.com/CMT-MU/MultiPie).
  - This project includes [MathJax](https://www.mathjax.org/), which is licensed under the Apache License 2.0.

- **Citing QtDraw and MultiPie**: If you are using QtDraw and/or MultiPie in your scientific research, please help our scientific visibility by citing our work:
    > Hiroaki Kusunose, Rikuto Oiwa, and Satoru Hayami, Symmetry-adapted modeling for molecules and crystals, Phys. Rev. B <b>107</b>, 195118 (2023).<br>
    > DOI: [https://doi.org/10.1103/PhysRevB.107.195118](https://doi.org/10.1103/PhysRevB.107.195118)
