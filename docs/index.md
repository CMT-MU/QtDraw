<img width="128" src="qtdraw_logo.png">

# QtDraw

3D drawing tool for molecules and crystals based on [PyVista](https://docs.pyvista.org/) and [Qt](https://www.riverbankcomputing.com/static/Docs/PyQt5/#).
Drawings are associated with crystallographic symmetry operations provided by [MultiPie](https://github.com/CMT-MU/MultiPie).

## Installation

QtDraw can be installed from PyPI using pip on Python >= 3.8:
```
pip install qtdraw
```
It is useful to associate with the following application with `.qtdw` extension.
- [Mac](https://github.com/CMT-MU/QtDraw/tree/main/others/QtDraw_MacApp.zip)
- [Windows](https://github.com/CMT-MU/QtDraw/tree/main/others/QtDraw_WinApp.zip)

You can also visit
[PyPI](https://pypi.org/project/qtdraw/) or [GitHub](https://github.com/CMT-MU/QtDraw) to download the source.

See also, [Install Guide (in Japanese)](./install_guide.pdf)

## Authors
Hiroaki Kusunose

## Citing QtDraw and MultiPie

If you are using QtDraw and/or MultiPie in your scientific research, please help our scientific visibility by citing our work:

> Hiroaki Kusunose, Rikuto Oiwa, and Satoru Hayami, _Symmetry-adapted modeling for molecules and crystals_, Phys. Rev. B <b>107</b>, 195118 (2023).
>
> DOI: [https://doi.org/10.1103/PhysRevB.107.195118](https://doi.org/10.1103/PhysRevB.107.195118)

BibTex:
```
@article{PhysRevB.107.195118,
title = {Symmetry-adapted modeling for molecules and crystals},
author = {Kusunose, Hiroaki and Oiwa, Rikuto and Hayami, Satoru},
journal = {Phys. Rev. B},
volume = {107},
issue = {19},
pages = {195118},
numpages = {14},
year = {2023},
month = {May},
publisher = {American Physical Society},
doi = {10.1103/PhysRevB.107.195118},
url = {https://link.aps.org/doi/10.1103/PhysRevB.107.195118}
}
```

## Requirements
- This library requires [TeXLive](https://www.tug.org/texlive/) environment.
- Symmetry operation supports are provided by [MultiPie](https://github.com/CMT-MU/MultiPie).

## Objects

QtDraw can draw the following 3D objects.

- sphere (site)
- bond
- vector
- atomic orbital
- stream vector
- plane
- box
- polygon
- text (3d, 2d)
- spline curve by data or parametric function
- caption

To draw these objects, push `list` button in DataSet panel, and then push `Add` and input a group name. Properties of an object are editable by double click of each column.

These objects are also drawn from Python code.
See [API](./API.md) for detail.

Example of all objects is found in [sample.qtdw](./sample.qtdw), which is drawn by [sample.py](./sample.py).

Shell command `qtdraw [filename]` is available.

Drawing supported by [MultiPie](https://github.com/CMT-MU/MultiPie) is shown [here](./multipie.md).

## Change Log
- [version 1.1.3](ver1.1.3.md)
- [version 1.1.2](ver1.1.2.md)
