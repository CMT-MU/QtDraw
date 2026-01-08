# Overview

**QtDraw** is 3D drawing tool especially for molecules and crystals based on [PyVista](https://docs.pyvista.org/) and [PySide6](https://doc.qt.io/qtforpython-6/index.html).
The main window and available objects looks like the following.

![sample.jpg](fig/sample.jpg)

All objects can be modified by GUI in the `Dataset` window.

![dataset.jpg](fig/dataset.jpg)

All objectes are located at the `position` + `cell` in the fractional coordinate of the `crystal` system with the `origin`, which allows us to repeat the drawn objects just by pushing `repeat` button.
By `non-repeat` button, the repeated objects can be converted to those at the same `position` with the home cell, i.e., `cell=[0,0,0]`.

By installing the Pyhton package, [MultiPie](https://github.com/CMT-MU/MultiPie), which provides the various crystallographic symmetry operations and symmetry-adapted multipole basis (SAMB) construction, object drawing in **QtDraw** is also associated by the symmetry operation and the SAMB.
To use this functionality, after installing `MultiPie`, push `MultiPie` button in the bottom right.
The additional window for `MultiPie` plug-in is shown, which consists of three panels:

- **Group Info.**

    show various group information.
    ![multipie_group.jpg](fig/multipie_group.jpg)

- **Object Drawing**

    draw objects by given symmetry operations.
    ![multipie_object.jpg](fig/multipie_object.jpg)

- **Basis Drawing**

    draw SAMB object (with modulation over multiple cells)
    ![multipie_basis.jpg](fig/multipie_basis.jpg)

For the API, please refer to the following:

- [Core module](api_core.md) core modules for end users.
- [Summary](api_summary.md) for various modules for implementation purpose.
