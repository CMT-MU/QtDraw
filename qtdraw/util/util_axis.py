"""
Utility for axis actor and label, unit cell, and view vector.

This module contains utility for axis, etc.
"""

import vtk
import pyvista as pv
import numpy as np
from math import floor, ceil
from gcoreutils.color_palette import all_colors
from gcoreutils.convert_util import text_to_list
from qtdraw.core.pyvista_widget_setting import widget_detail as detail
from qtdraw.core.pyvista_widget_setting import CHOP, DIGIT


# ==================================================
def _create_label_axes_actor(A, label, size, bold, italic, color, scale):
    """
    Create label only orientation axes actor.

    Args:
        A (numpy.ndarray): (a1, a2, a3) unit vectors, 4x4 [float].
        label (str): axes labels.
        size (int): font size.
        bold (bool): bold face ?
        italic (bool): italic ?
        color (list): axes colors, [[float]], RGB in unit of [0,1].
        scale (float): zoom factor.

    Returns:
        - (pyvista.AxesActor) -- axes actor.
    """
    label = text_to_list(label.replace(" ", ""))

    # font size is zoomed manually.
    size = int(size * scale)

    # set transform for non-orthogonal axes.
    transform = vtk.vtkTransform()
    transform.SetMatrix(A.ravel().tolist())

    # create axes actor with label only.
    lbl = pv.AxesActor()
    lbl.SetShaftTypeToCylinder()
    lbl.SetTipTypeToCone()
    lbl.SetCylinderRadius(0.0)
    lbl.SetConeRadius(0.0)
    lbl.SetUserTransform(transform)

    # set font properties.
    lbl.SetXAxisLabelText(label[0])
    lbl.SetYAxisLabelText(label[1])
    lbl.SetZAxisLabelText(label[2])

    x_p = lbl.GetXAxisCaptionActor2D()
    y_p = lbl.GetYAxisCaptionActor2D()
    z_p = lbl.GetZAxisCaptionActor2D()
    for i, c in zip([x_p, y_p, z_p], color):
        i.GetPositionCoordinate().SetCoordinateSystemToWorld()
        i.GetTextActor().SetTextScaleModeToViewport()
        if bold:
            i.GetCaptionTextProperty().BoldOn()
        else:
            i.GetCaptionTextProperty().BoldOff()
        if italic:
            i.GetCaptionTextProperty().ItalicOn()
        else:
            i.GetCaptionTextProperty().ItalicOff()
        i.GetCaptionTextProperty().SetFontSize(size)
        i.GetCaptionTextProperty().SetColor(*c)

    return lbl


# ==================================================
def _create_axes_actor(
    A,
    label,
    label_size,
    label_bold,
    label_italic,
    label_color,
    scale,
    shaft_color,
    sphere_color,
    shaft_radius,
    tip_radius,
    tip_length,
    tip_resolution,
    sphere_radius,
    theta_phi_resolution,
):
    """
    Create custom axes actor.

    Args:
        A (numpy.ndarray): (a1, a2, a3) unit vectors, 4x4 [float].
        label (str): axes labels.
        label_size (int): font size.
        label_bold (bool): bold face ?
        label_italic (bool): italic ?
        label_color (list): axes label color names, [str].
        scale (float): zoom factor.
        shaft_color (list): axes color names, [str].
        sphere_color (str): center color name.
        shaft_radius (float): axes cylinder radius.
        tip_radius (float): axes tip radius.
        tip_length (float): axes tip length.
        tip_resolution (int): axes tip resolution.
        sphere_radius (float): axes sphere radius.
        theta_phi_resolution (list): axes sphere theta, phi resolution, [int].

    Returns:
        - (vtk.vtkPropAssembly) -- custom axes actor.
    """
    # convert from color name to RGB float.
    shaft_color = [(np.array(all_colors[c][1]) / 255) for c in shaft_color]
    sphere_color = np.array(all_colors[sphere_color][1]) / 255
    # convert from color name to RGB.
    label_color = [all_colors[c][1] for c in label_color]

    # create axes.
    assembly = vtk.vtkPropAssembly()
    for d, c in zip(A[0:3, 0:3].T, shaft_color):
        # axes arrows.
        g = pv.Arrow(
            direction=d,
            shaft_radius=shaft_radius,
            tip_radius=tip_radius,
            tip_length=tip_length,
            tip_resolution=tip_resolution,
        )
        actor = pv.Actor(mapper=pv.DataSetMapper(g))
        actor.GetProperty().SetColor(c)
        assembly.AddPart(actor)

        # dummy axes to keep rotation center as origin.
        g = pv.Sphere(radius=0.0, center=-np.array(d))
        actor = pv.Actor(mapper=pv.DataSetMapper(g))
        assembly.AddPart(actor)

    # center sphere (theta, phi are used differently).
    phi, theta = theta_phi_resolution
    g0 = pv.Sphere(radius=sphere_radius, theta_resolution=theta, phi_resolution=phi)
    actor = pv.Actor(mapper=pv.DataSetMapper(g0))
    actor.GetProperty().SetColor(sphere_color)
    assembly.AddPart(actor)

    # add axes label.
    if label is not None:
        lbl = _create_label_axes_actor(
            A,
            label=label,
            size=label_size,
            bold=label_bold,
            italic=label_italic,
            color=label_color,
            scale=scale,
        )
        assembly.AddPart(lbl)

    return assembly


# ==================================================
def create_axes_widget(
    pv_widget,
    A,
    label="[x,y,z]",
    label_size=28,
    label_bold=True,
    label_italic=False,
    label_color=["black", "black", "black"],
    viewport=True,
):
    """
    Create axes widget.

    Args:
        pv_widget (PyVistaWidget): pyvista widget.
        A (numpy.ndarray): (a1, a2, a3) unit vectors, 4x4 [float].
        label (str, optional): axes labels.
        label_size (int, optional): font size.
        label_bold (bool, optional): bold face ?
        label_italic (bool, optional): italic ?
        label_color (list, optional): axes label color names, [str].
        viewport (bool, optional): set viewport ?

    Note:
        - if label is None, no label is used.
    """
    scale = detail["scale"]
    pickable = detail["pickable"]
    shaft_color = detail["shaft_color"]
    sphere_color = detail["sphere_color"]
    shaft_radius = detail["shaft_radius"]
    tip_radius = detail["tip_radius"]
    tip_length = detail["tip_length"]
    tip_resolution = detail["tip_resolution"]
    sphere_radius = detail["sphere_radius"]
    theta_phi_resolution = detail["theta_phi_resolution"]

    if viewport:
        viewport = detail["viewport"]
    else:
        viewport = [0.0, 0.0, 1.0, 1.0]
        pickable = False

    # create axes actor.
    marker = _create_axes_actor(
        A,
        label=label,
        label_size=label_size,
        label_bold=label_bold,
        label_italic=label_italic,
        label_color=label_color,
        scale=scale,
        shaft_color=shaft_color,
        sphere_color=sphere_color,
        shaft_radius=shaft_radius,
        tip_radius=tip_radius,
        tip_length=tip_length,
        tip_resolution=tip_resolution,
        sphere_radius=sphere_radius,
        theta_phi_resolution=theta_phi_resolution,
    )

    # create axes widget.
    pv_widget.add_orientation_widget(marker, interactive=pickable, viewport=viewport)
    pv_widget.renderer.axes_widget.SetZoom(scale)


# ==================================================
def create_unit_cell(A, origin, lower=None, dimensions=None):
    """
    Create unit cell mesh.

    Args:
        A (numpy.ndarray): (a1, a2, a3) unit vectors, 4x4 [float].
        origin (list or numpy.ndarray): origin, [float].
        lower (list, optional): lower bound indices, [int].
        dimensions (list, optional): repeat times, [int].

    Returns:
        - (pyvista.PolyData) -- unit cel mesh.
    """
    if lower is None:
        lower = [0, 0, 0]
    if dimensions is None:
        dimensions = [1, 1, 1]

    # signle box.
    pts = np.array(
        [
            [0, 0, 0],
            [1, 0, 0],
            [1, 1, 0],
            [0, 1, 0],
            [0, 0, 1],
            [1, 0, 1],
            [1, 1, 1],
            [0, 1, 1],
        ],
        dtype=np.float64,
    )
    shift = np.array([origin] * len(pts), dtype=np.float64)
    pts = pts + shift
    lines = [5, 0, 1, 2, 3, 0, 5, 4, 5, 6, 7, 4, 2, 0, 4, 2, 1, 5, 2, 2, 6, 2, 3, 7]
    box = pv.PolyData(pts, lines=lines)
    box.transform(A, inplace=True)

    # repeated boxes.
    m = pv.ImageData(dimensions=dimensions, origin=lower).cast_to_unstructured_grid()
    m.transform(A, inplace=True)
    p = m.glyph(geom=box, factor=1.0, scale=False, orient=False)

    return p


# ==================================================
def get_view_vector(n, A):
    """
    Get view and viewup.

    Args:
        n (list): view indices of [a1,a2,a3], [int].
        A (numpy.ndarray): (a1, a2, a3) unit vectors, 4x4 [float].

    Returns:
        - (numpy.ndarray) -- view.
        - (numpy.ndarray) -- viewup.
    """
    view = n[0] * A[0:3, 0] + n[1] * A[0:3, 1] + n[2] * A[0:3, 2]
    norm = np.linalg.norm(view)
    view = view / norm

    if np.allclose(view, [0, 1, 0]) or np.allclose(view, [0, 0, -1]):
        viewup = np.array([1, 0, 0])
    elif np.allclose(view, [0, 0, 1]) or np.allclose(view, [-1, 0, 0]):
        viewup = np.array([0, 1, 0])
    elif np.allclose(view, [1, 0, 0]) or np.allclose(view, [0, -1, 0]):
        viewup = np.array([0, 0, 1])
    else:
        vz = np.sqrt(1.0 - view[2] * view[2])
        vx = -view[2] * view[0] / vz
        vy = -view[2] * view[1] / vz
        viewup = np.array([vx, vy, vz], dtype=np.float64)

    return view, viewup


# ==================================================
def create_grid(ilower, dims):
    """
    Create grid point.

    Parameters:
    Args:
        ilower (list): start cell.
        dims (list): range in each dim.

    Returns:
        - (list) -- grid point, [str].
    """
    # range.
    x = np.arange(ilower[0], ilower[0] + dims[0])
    y = np.arange(ilower[1], ilower[1] + dims[1])
    z = np.arange(ilower[2], ilower[2] + dims[2])

    # mesh grid.
    X, Y, Z = np.meshgrid(x, y, z, indexing="ij")

    # transform grid to point.
    grid = np.vstack([X.ravel(), Y.ravel(), Z.ravel()]).T

    grid = [str(i).replace(" ", "") for i in grid.tolist()]

    return grid


# ==================================================
def get_lattice_vector(crystal, cell):
    """
    Get lattice vector.

    Args:
        crystal (str): crystal.
        cell (dict): cell.

    Returns:
        - dict: cell.
        - list: A.
    """
    a = float(cell["a"])
    b = float(cell["b"])
    c = float(cell["c"])
    alpha = float(cell["alpha"])
    beta = float(cell["beta"])
    gamma = float(cell["gamma"])

    if crystal == "monoclinic":
        alpha = 90.0
        gamma = 90.0
    elif crystal == "orthorhombic":
        alpha = 90.0
        beta = 90.0
        gamma = 90.0
    elif crystal in ["trigonal", "hexagonal"]:
        alpha = 90.0
        beta = 90.0
        gamma = 120.0
        b = a
    elif crystal == "tetragonal":
        alpha = 90.0
        beta = 90.0
        gamma = 90.0
        b = a
    elif crystal == "cubic":
        alpha = 90.0
        beta = 90.0
        gamma = 90.0
        b = a
        c = a

    ca = np.cos(alpha * np.pi / 180)
    cb = np.cos(beta * np.pi / 180)
    cc = np.cos(gamma * np.pi / 180)
    sc = np.sin(gamma * np.pi / 180)
    s = 1.0 - ca * ca - cb * cb - cc * cc + 2.0 * ca * cb * cc
    s = max(CHOP, np.sqrt(s))

    a1 = np.array([a, 0, 0]).round(DIGIT).tolist()
    a2 = np.array([b * cc, b * sc, 0]).round(DIGIT).tolist()
    a3 = np.array([c * cb, c * (ca - cb * cc) / sc, c * s / sc]).round(DIGIT).tolist()

    A = np.eye(4)
    A[0:3, 0] = a1
    A[0:3, 1] = a2
    A[0:3, 2] = a3

    A = A.round(DIGIT).tolist()
    cell = {"a": a, "b": b, "c": c, "alpha": alpha, "beta": beta, "gamma": gamma}

    return cell, A


# ==================================================
def get_repeat_range(lower, upper):
    """
    Get repeart range.

    Args:
        lower (list): upper.
        upper (list): lower.

    Returns:
        - list: lower cell.
        - list: size of repeat.
    """
    i1 = [floor(lower[0]), floor(lower[1]), floor(lower[2])]
    i2 = [ceil(upper[0] + CHOP), ceil(upper[1] + CHOP), ceil(upper[2] + CHOP)]
    dims = [i2[0] - i1[0], i2[1] - i1[1], i2[2] - i1[2]]
    for i in range(3):
        dims[i] = max(1, dims[i])

    return i1, dims


# ==================================================
def get_outside_box(point, lower, upper):
    """
    Get indices outside range.

    Args:
        point (numpy.ndarray): a set of points.
        lower (list): lower bound.
        upper (list): upper bound.

    Returns:
        - (numpy.ndarray) -- list of indices.
    """
    xmin, ymin, zmin = lower
    xmax, ymax, zmax = upper

    in_x = (point[:, 0] >= xmin) & (point[:, 0] <= xmax)
    in_y = (point[:, 1] >= ymin) & (point[:, 1] <= ymax)
    in_z = (point[:, 2] >= zmin) & (point[:, 2] <= zmax)

    in_box = in_x & in_y & in_z
    outside = np.where(~in_box)[0]

    return outside
