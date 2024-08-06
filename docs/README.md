# [QtDraw](https://cmt-mu.github.io/QtDraw/)

3D drawing tool for molecules and crystals based on [PyVista](https://docs.pyvista.org/) and [Qt](https://www.riverbankcomputing.com/static/Docs/PyQt5/#).
Drawings are associated with crystallographic symmetry operations provided by [MultiPie](https://github.com/CMT-MU/MultiPie).

- **Authors**: Hiroaki Kusunose

- **Citing QtDraw and MultiPie**: If you are using QtDraw and/or MultiPie in your scientific research, please help our scientific visibility by citing our work:
    > Hiroaki Kusunose, Rikuto Oiwa, and Satoru Hayami, Symmetry-adapted modeling for molecules and crystals, Phys. Rev. B <b>107</b>, 195118 (2023).<br>
    > DOI: [https://doi.org/10.1103/PhysRevB.107.195118](https://doi.org/10.1103/PhysRevB.107.195118)

- **Installation**: QtDraw can be installed from PyPI using pip on Python >= 3.9:
    ```
    pip install qtdraw
    ```
    - It is useful to associate with the following application with `.qtdw` and `.cif` extension.
      - [Mac](https://github.com/CMT-MU/QtDraw/tree/main/others/QtDraw_MacApp.zip)
      - [Windows](https://github.com/CMT-MU/QtDraw/tree/main/others/QtDraw_WinApp.zip)
    - You can also visit [PyPI](https://pypi.org/project/qtdraw/) or [GitHub](https://github.com/CMT-MU/QtDraw) to download the source.
    - See also, [Install Guide (in Japanese)](./src/install_guide.pdf)
    - Shell command `qtdraw [filename]` is available.

- **Requirements**:
  - This library requires [TeXLive](https://www.tug.org/texlive/) environment.
  - Symmetry operation supports are provided by [MultiPie](https://github.com/CMT-MU/MultiPie).

- **See also**:
  - [Manual](https://cmt-mu.github.io/QtDraw/src/overview.html).
  - [MultiPie tutorial (in Japanese)](https://cmt-mu.github.io/MultiPieTutorial/)
  - [QtDraw tutorial (in Japanese)](https://cmt-mu.github.io/QtDrawTutorial/)
