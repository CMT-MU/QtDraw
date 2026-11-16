# User Guide

A Japanese version is [here](user_guide_ja.md).

A practical tutorial of MultiPie via QtDraw is given by [Tutorial via QtDraw](tutorial_multipie_qtdraw.pdf)

This guide explains how a drawing of **QtDraw** is made: what it consists of, the objects in the data tables, the drawing with MultiPie, and the use from Python code.
The menus, the mouse and the keys are summarized in [Getting Started](getting_started.md), and all the methods in [Usage from Python code](from_python.md).

## 1. Overview

### A drawing

A drawing consists of three parts, which are saved together in a `.qtdw` file.

| part | contents | where to change |
| --- | --- | --- |
| objects | sites, bonds, vectors, orbitals, ... (19 types) | `DataSet` window (data tables) |
| unit cell | crystal system, `a`, `b`, `c`, `alpha`, `beta`, `gamma`, origin | side panel |
| view | range, repeat, clip, view direction, axis and cell display | side panel, `View` menu |

A material file (`.cif`, `.vesta`, `.xsf`) can also be opened: it is converted to a drawing of sites and bonds (and the grid data of an `.xsf` file).

### Position of an object

Every object is placed at `position` + `cell`:

- `position`: a point in the **fractional coordinates** of the unit cell, e.g. `[1/2,1/2,0]`;
- `cell`: a lattice translation `[n1,n2,n3]`, `[0,0,0]` for the home cell.

A direction of an object (of a bond, a vector, ...) is given in the fractional or in the Cartesian coordinates, chosen by its `cartesian` column.

### Range, repeat and clip

- `range` (`lower`, `upper`): the region to draw, in fractional coordinates.
- `repeat`: draws every object also at all the lattice translations within the range.
- `clip`: cuts away the parts outside the range.
- `non-repeat` (`View` menu): turns the repeated objects back into the objects of the home cell.

For example, two sites in a cubic cell, repeated over 2 × 2 × 1 cells:

```python
from qtdraw import QtDraw

win = QtDraw()
win.add_site(position="[0,0,0]", color="red")
win.add_site(position="[1/2,1/2,1/2]", color="blue")
win.set_range(lower="[0,0,0]", upper="[2,2,1]")
win.set_repeat(True)
```

## 2. Data tables

### The DataSet window

The `e` key, or the `DataSet` button, opens the `DataSet` window: a table for each type of object, in tabs.

- Objects with the same `name` form a group. The check box of `name` shows or hides it.
- Double-click a cell to edit it. A value that cannot be read is not accepted.
- Right-click to insert, copy or remove rows. Shift or Ctrl (Cmd on macOS) + click selects several rows, and `Delete` (also `Backspace` on macOS) removes the selected rows at once.
- Right-click an object in the main panel to open its row, hide it or remove it.

### Values

| kind | example | note |
| --- | --- | --- |
| vector | `[1/2,0,0]`, `[sqrt(3)/2,1/2,0]` | numbers or expressions |
| polynomial | `x*y`, `3z**2-r**2` | in `x`, `y`, `z` and `r` (= $\sqrt{x^2+y^2+z^2}$) |
| color | `red`, `darkseagreen` | a color name |
| colormap | `coolwarm`, `Wistia` | for an orbital, a stream or an isosurface, a colormap is also accepted |
| check | on / off | e.g. `cartesian`, `arrow1` |
| LaTeX | `$\alpha_1$` | in a label, a caption or a 2D text; drawn with MathJax |

### Columns common to all objects

| column | meaning | default |
| --- | --- | --- |
| `name` | name of the group; its check box shows or hides the group | `untitled` |
| `label` | label text; its check box shows the label | `label` (hidden) |
| `margin` | space between the object and its label (number of space characters) | `3` |
| `position` | position in fractional coordinates | `[0,0,0]` |
| `cell` | lattice translation | `[0,0,0]` |
| `opacity` | from 0 (transparent) to 1 | `1.0` |

In Python, these are keyword arguments of every `add_*` method, e.g. `win.add_site(name="Cu", label="Cu1", position="[0,0,0]")`. The check boxes of `name` and `label` are `show` and `show_label`, e.g. `win.add_site(show=False)` for a hidden object, `win.add_site(label="Cu1", show_label=True)` for a shown label.
The other columns of each object follow.

### Points and arrows

**site**: a sphere.

| column | meaning |
| --- | --- |
| `size` | radius |
| `color` | color |

```python
win.add_site(position="[1/2,0,0]", size=0.2, color="red")
```

**bond**: a cylinder; `position` is its **center**, and `direction` the vector from one end to the other.

| column | meaning |
| --- | --- |
| `direction` | vector from the tail to the head |
| `width` | radius |
| `color`, `color2` | colors of the tail and head halves |
| `cartesian` | `direction` in Cartesian coordinates ? (off: fractional) |

```python
win.add_bond(position="[1/2,0,0]", direction="[1,0,0]", color="red", color2="blue")
```

**vector**: an arrow through `position`.

| column | meaning |
| --- | --- |
| `direction` | direction of the arrow |
| `length` | length; a negative value uses \|`length`\| × the norm of `direction` |
| `width` | width |
| `offset` | position of the tail, in units of the length (`-0.43`: the arrow is centered near `position`) |
| `color` | color |
| `cartesian` | `direction` in Cartesian coordinates ? (on by default) |
| `shaft R`, `tip R`, `tip length` | shape of the arrow, relative to `width` and `length` |

```python
win.add_vector(position="[0,0,0]", direction="[1,1,0]", length=0.8, color="green")
```

**line**: a line (or an arrow) from `position` to `position` + `direction`.

| column | meaning |
| --- | --- |
| `direction` | vector from the start to the end |
| `width` | width |
| `arrow1`, `arrow2` | arrow heads at the start and at the end |
| `tip R`, `tip length` | shape of the arrow heads |
| `color` | color |
| `cartesian` | `direction` in Cartesian coordinates ? |

```python
win.add_line(position="[0,0,0]", direction="[1,0,0]", arrow2=True)
```

### Functions on a sphere

**orbital**: a surface $r(\theta,\phi) \propto |f|$ of a polynomial $f(x,y,z)$, colored by another polynomial.

| column | meaning |
| --- | --- |
| `shape` | polynomial $f$ of the shape |
| `surface` | polynomial of the color (empty: the same as `shape`) |
| `size` | the maximum radius; a negative value scales the radius by \|`size`\| |
| `range` | range of $\theta$ and $\phi$ in degrees, `[[0,180],[0,360]]` |
| `color` | color, or colormap of the `surface` value |

```python
win.add_orbital(position="[0,0,0]", shape="x*y", size=0.5, color="coolwarm")
```

**stream**: arrows of a vector field drawn on a surface.

| column | meaning |
| --- | --- |
| `shape` | polynomial of the surface on which the arrows are put (`1`: a sphere) |
| `vector` | polynomials of the vector field, `[vx,vy,vz]` |
| `size` | size of the surface; a negative value normalizes the shape |
| `range` | range of $\theta$ and $\phi$ in degrees |
| `division` | numbers of arrows in $\theta$ and $\phi$ |
| `length`, `width`, `offset` | size of each arrow |
| `abs_scale` | scale each arrow by the size of the vector ? |
| `color`, `component` | color, or colormap of the component (`x`, `y`, `z`, `abs`) |
| `shaft R`, `tip R`, `tip length` | shape of the arrows |

```python
win.add_stream(position="[0,0,0]", vector="[-y,x,0]", color="coolwarm", component="abs")
```

### Shapes

**plane**: a rectangle centered at `position`.

| column | meaning |
| --- | --- |
| `normal` | normal vector |
| `x_size`, `y_size` | lengths of the sides |
| `color` | color |
| `grid`, `grid_color`, `width` | grid lines on the plane, their color and width |
| `cartesian` | `normal` in Cartesian coordinates ? |

```python
win.add_plane(position="[1/2,1/2,0]", normal="[0,0,1]", x_size=2, y_size=2, opacity=0.3)
```

**circle**: a disk centered at `position`.

| column | meaning |
| --- | --- |
| `normal` | normal vector |
| `size` | radius |
| `color` | color |
| `edge`, `edge_color`, `width` | its edge, the color and width of the edge |
| `cartesian` | `normal` in Cartesian coordinates ? |

```python
win.add_circle(position="[0,0,0]", normal="[1,0,0]", size=0.3)
```

**torus**: a ring.

| column | meaning |
| --- | --- |
| `normal` | axis of the ring |
| `size` | radius of the ring |
| `width` | radius of the tube |
| `color` | color |
| `cartesian` | `normal` in Cartesian coordinates ? |

```python
win.add_torus(position="[0,0,0]", size=0.5, width=0.1)
```

**ellipsoid**: an ellipsoid centered at `position`.

| column | meaning |
| --- | --- |
| `normal` | direction of the `z_size` axis |
| `x_size`, `y_size`, `z_size` | radii along the three axes |
| `color` | color |
| `cartesian` | `normal` in Cartesian coordinates ? |

```python
win.add_ellipsoid(position="[0,0,0]", x_size=0.5, y_size=0.3, z_size=0.2)
```

**toroid**: a superellipsoidal ring, e.g. a rounded square ring.

| column | meaning |
| --- | --- |
| `normal` | axis of the ring |
| `size`, `width` | radius of the ring and of the tube |
| `x_scale`, `y_scale`, `z_scale` | scales along the three axes |
| `ring_shape`, `tube_shape` | shape exponents of the ring and of the tube (1: round, smaller: squarer, larger: pointed) |
| `color` | color |
| `cartesian` | `normal` in Cartesian coordinates ? |

```python
win.add_toroid(position="[0,0,0]", size=0.5, width=0.15, ring_shape=0.3)
```

**box**: a parallelepiped with a corner at `position`.

| column | meaning |
| --- | --- |
| `a1`, `a2`, `a3` | edge vectors |
| `color` | color |
| `edge`, `edge_color`, `width` | its edges, their color and width |
| `wireframe` | draw only the edges ? |
| `cartesian` | edge vectors in Cartesian coordinates ? (off: fractional) |

```python
win.add_box(position="[0,0,0]", a1="[1,0,0]", a2="[0,1,0]", a3="[0,0,1/2]", opacity=0.3)
```

**polygon**: a polyhedron given by its vertices and faces.

| column | meaning |
| --- | --- |
| `point` | vertices, relative to `position` |
| `connectivity` | faces, each a list of vertex indices (from 0) |
| `color`, `edge`, `edge_color`, `width`, `wireframe` | as for a box |
| `cartesian` | `point` in Cartesian coordinates ? (off: fractional) |

```python
win.add_polygon(point="[[0,0,0],[1,0,0],[0,1,0],[0,0,1]]", connectivity="[[0,1,2],[0,1,3],[0,2,3],[1,2,3]]")
```

### Curves

**spline**: a smooth curve through points.

| column | meaning |
| --- | --- |
| `point` | points of the curve, relative to `position` |
| `width` | width |
| `n_interp` | number of interpolated points |
| `closed` | closed curve ? |
| `natural` | natural end conditions ? |
| `arrow1`, `arrow2`, `tip R`, `tip length` | arrow heads at the start and at the end |
| `color` | color |
| `cartesian` | `point` in Cartesian coordinates ? |

```python
win.add_spline(point="[[0,0,0],[1,0,1],[0,1,2]]", arrow2=True)
```

**spline_t**: a curve given by a function of a parameter `t`.

| column | meaning |
| --- | --- |
| `point` | function of `t`, `[x(t),y(t),z(t)]` |
| `t_range` | `[t0,t1,dt]` |
| others | as for a spline |

```python
win.add_spline_t(point="[cos(2 pi t), sin(2 pi t), t/2]", t_range="[0,2,0.02]")
```

### Texts

**text3d**: a 3D text placed in the drawing.

| column | meaning |
| --- | --- |
| `text` | text |
| `size` | height |
| `view` | direction from which the text is read |
| `depth` | thickness |
| `offset` | shift from `position` |
| `color` | color |

```python
win.add_text3d(position="[0,0,1]", text="Cu", size=0.3)
```

**caption**: texts at several positions, of a fixed size on the screen.

| column | meaning |
| --- | --- |
| `position` | positions, one for each caption, `[[x1,y1,z1],[x2,y2,z2],...]` |
| `caption` | captions, `[A,B,...]` |
| `size`, `bold`, `color` | font size, bold and color |

```python
win.add_caption(position="[[0,0,0],[1,0,0]]", caption="[A,B]")
```

**text2d**: a text fixed on the window, e.g. a title.

| column | meaning |
| --- | --- |
| `position` | position in the window, `[x,y,0]`, with `x` and `y` from 0 to 1 |
| `caption` | text (LaTeX in `$...$`) |
| `size`, `color`, `font` | font size, color and font |

```python
win.add_text2d(caption=r"$E = \hbar\omega$", position="[0.05,0.9,0]", size=12)
```

### Data

**isosurface**: isosurfaces of grid data, e.g. a charge density in an `.xsf` file.

| column | meaning |
| --- | --- |
| `data` | file of the grid data (`.xsf`, or a dict file written by QtDraw), relative to the drawing |
| `value` | values of the isosurfaces, `[v1,v2,...]` |
| `surface` | name of other data used for the color of the surface (empty: one color) |
| `color` | color, or colormap of the `surface` data |
| `color_range` | range of the colormap |

```python
win.add_isosurface(data="Si.xsf", value="[0.05]", color="skyblue", opacity=0.5)
```

## 3. Drawing with MultiPie

[MultiPie](https://github.com/CMT-MU/MultiPie) gives the symmetry operations of point and space groups (also magnetic ones) and the symmetry-adapted multipole basis (SAMB).
With it, QtDraw draws all the objects equivalent by symmetry, and SAMBs.
QtDraw works with MultiPie Ver.2 (2.5 or later) and Ver.3. Without MultiPie, the `MultiPie` button offers to install it.

### The MultiPie dialog

The `MultiPie` button opens the dialog.
At its top, a group is chosen by its type (PG, SG, MPG, MSG), crystal system and name; the unit cell of QtDraw follows the crystal system of the group.
The `Info.` buttons show the symmetry operations, the character table, the Wyckoff sites and bonds and the product table.
The dialog has three tabs:

| tab | what it does |
| --- | --- |
| **Group Info.** | irrep and harmonics decompositions, harmonics, finding and drawing Wyckoff sites and bonds, atomic multipoles, response tensors |
| **Object Drawing** | draws the sites, bonds, vectors and orbitals equivalent to a representative one |
| **Basis Drawing** | lists the SAMBs of a site, bond, vector or orbital cluster, and draws one of them, a linear combination, or a modulation over cells (space groups only) |

What is drawn is a set of ordinary objects, which can be edited in the data tables as any other.

### How to give a site, a bond, a vector and an orbital

| object | form | example |
| --- | --- | --- |
| site | `[x,y,z]` | `[1/3,2/3,0]` |
| bond | `[x0,y0,z0];[x1,y1,z1]` (tail;head), `[X,Y,Z]@[x,y,z]` (vector@center), or `[x0,y0,z0]:[X,Y,Z]` (start:vector) | `[2/3,1/3,0];[1/3,2/3,0]` |
| vector | `[X,Y,Z] # site/bond` | `[0,0,1] # [1/3,2/3,0]` |
| orbital | `polynomial # site/bond` | `x*y # [0,0,0]` |

### From Python

A group is set by its tag: e.g. `D6h` (point group), `D6h^1` (space group), `MPG:1.1.1`, `MSG:123.345` (magnetic groups).
The `mp_*` methods do what the dialog does:

```python
from qtdraw import QtDraw

win = QtDraw()
win.mp_set_group("D6h^1")  # graphene.
win.mp_add_site("[1/3,2/3,0]")  # equivalent sites.
win.mp_add_bond("[2/3,1/3,0];[1/3,2/3,0]")  # equivalent bonds.

lst = win.mp_site_samb_list("[1/3,2/3,0]")  # SAMBs of the site cluster.
print(lst)
win.mp_add_site_samb(lst[1])  # draw one of them.
```

A vector or orbital SAMB is drawn by its tag (e.g. `Q01`), a linear combination of tags (e.g. `Q02+G01`), or a modulation:

```python
lst = win.mp_vector_samb_list("[1/3,2/3,0]", "M")  # magnetic-dipole SAMBs, {type: [tags]}.
win.mp_add_vector_samb("M01")
win.mp_add_vector_samb_modulation("[[M01, 1, [1/2,0,0], cos]] : [2,2,1]")  # [[tag, coefficient, k, cos/sin]] : cells.
```

A modulation needs the lattice translations of a space group; for a point group it is ignored with a warning.
More examples: [Graphene](examples/mp_graphene.ipynb), [Te](examples/mp_Te.ipynb), [all mp_* methods](examples/multipie.ipynb).

## 4. Usage from Python code

### Two ways

| way | use |
| --- | --- |
| `QtDraw()` | the QtDraw window, drawn from a script or a Jupyter notebook |
| `create_qtdraw_file(filename, callback)` | writes a `.qtdw` file without a window (background job) |

The arguments of `add_*` are the columns of the data tables, as strings or numbers; an argument left out (or `None`) takes the default value.

### A script

```python
from qtdraw import QtDraw

win = QtDraw()
win.set_crystal("hexagonal")
win.set_unit_cell({"a": 2.46, "c": 6.7})
win.add_site(position="[1/3,2/3,0]", size=0.2, label="C1")
win.add_site(position="[2/3,1/3,0]", size=0.2, label="C2")
win.add_bond(position="[1/2,1/2,0]", direction="[1/3,-1/3,0]")  # C1-C2.
win.set_view([0, 0, 1])  # view along c.
win.save("graphene.qtdw")
win.save_screenshot("graphene.png")  # also .pdf, .svg, ...
win.exec()  # in a script, show the window until it is closed (not needed in Jupyter).
```

### Without a window

```python
from qtdraw import create_qtdraw_file


def draw(widget):
    for i in range(8):
        widget.add_site(position=f"[{i/8},0,0]", size=0.05)


create_qtdraw_file(filename="chain.qtdw", callback=draw)
```

### From a drawing to Python code

`File` > `Export as Python...` writes the current drawing as Python code that draws the same, e.g. to start a script from a drawing made by hand. `win.to_python()` returns the code, and `win.save_python("drawing.py")` saves it.

```python
win.save_python("graphene.py")
```

writes, for example,

```python
import sys

from qtdraw import QtDraw

win = QtDraw()
win.set_model('graphene')
win.mp_set_group('D6h^1')
win.set_crystal('hexagonal')
win.set_unit_cell({'a': 2.46, 'b': 2.46, 'c': 6.7, 'alpha': 90.0, 'beta': 90.0, 'gamma': 120.0})

# site.
win.add_site(label='C1', show_label=True, position='[1/3,2/3,0]', size=0.2)
...
```

- The code is made from the current state: the objects, the unit cell, the range, repeat and clip, the view settings, the model name and the MultiPie group. The camera (zoom and rotation), the preferences and the MultiPie dialog are not written.
- Only the values that differ from the defaults are written. The objects drawn by MultiPie are written one by one, after `mp_set_group`.
- With repeat, only the objects of the home cell are written, and `set_repeat(True)` repeats them.
- An isosurface whose data is not in a file is not written (a comment tells it).

### Useful methods

| method | does |
| --- | --- |
| `set_crystal`, `set_unit_cell`, `set_origin` | unit cell |
| `set_range`, `set_repeat`, `set_clip`, `set_nonrepeat` | range, repeat and clip |
| `set_view`, `set_parallel_projection`, `set_axis`, `set_cell`, `set_grid` | view |
| `set_model` | model name |
| `load`, `save` | files |
| `to_python`, `save_python` | Python code of the drawing |
| `save_screenshot` | image of the drawing (`.png`, `.bmp`, `.tif`, `.tiff`, `.svg`, `.eps`, `.ps`, `.pdf`), as `File` > `Screenshot` |
| `clear_data` | remove all objects |
| `update_preference` | preferences, e.g. `update_preference("label", "default_check", True)` to show labels |
| `undo`, `redo` | history |

All methods are listed in [Usage from Python code](from_python.md), and more examples are in [Examples](example.md).
