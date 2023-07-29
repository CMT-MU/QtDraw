import numpy as np
import vtk
from vtk import vtkParametricSpline
import pyvista as pv
from pyvista.utilities import surface_from_para
from qtpy.QtWidgets import QApplication, QStyleFactory
from gcoreutils.nsarray import NSArray
from gcoreutils.latex_util import latex_setting
from qtdraw.core.setting import rcParams
from qtdraw.core.color_palette import custom_colormap, all_colors

CHOP = 1e-4


# ==================================================
def create_application(style="fusion", font="Helvetica Neue", font_size=13, latex_mode="standard"):
    """
    create QApplication with style.

    Args:
        style (str, optional): GUI style, "fusion/windows/macintosh".
        font (str, optional): text font, "Helvetica Neue/Monaco/Osaka/Times New Roman".
        font_size (int, optional): text font size.
        latex_mode (str, optional): latex mode, "standard/times/pgf"

    Notes:
        - see, https://qiita.com/Hanjin_Liu/items/9df684920727f8a784c4
    """
    latex_setting(latex_mode)
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    global APPLICATION
    APPLICATION = app
    app.setStyle(QStyleFactory.create(style))
    style_sheet = "*{" + f"font-family: {font}; font-size: {font_size}px;" + "}"
    app.setStyleSheet(style_sheet)

    return app


# ==================================================
def SplineEx(points, n_points=None, closed=False, natural=True):
    spline_function = vtkParametricSpline()
    spline_function.SetPoints(pv.vtk_points(points, False))

    if closed:
        spline_function.ClosedOn()
    else:
        spline_function.ClosedOff()

    if natural and not closed:
        spline_function.SetLeftConstraint(2)
        spline_function.SetLeftValue(0.0)
        spline_function.SetRightConstraint(2)
        spline_function.SetRightValue(0.0)

    # get interpolation density
    u_res = n_points
    if u_res is None:
        u_res = points.shape[0]

    u_res -= 1
    spline = surface_from_para(spline_function, u_res)
    return spline.compute_arc_length()


# ==================================================
def create_unit_cell(A, origin, lower, dims):
    As = A.copy()

    # signle box.
    pts = np.array([[0.0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0], [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]])
    shift = np.array([origin] * len(pts))
    pts = pts + shift
    lines = np.array([5, 0, 1, 2, 3, 0, 5, 4, 5, 6, 7, 4, 2, 0, 4, 2, 1, 5, 2, 2, 6, 2, 3, 7])
    box = pv.PolyData(pts, lines=lines)
    box.transform(As)

    # repeated boxes.
    m = pv.UniformGrid(origin=lower, dims=dims).cast_to_unstructured_grid()
    m.transform(As)
    p = m.glyph(geom=box, factor=1.0)

    return box, p


# ==================================================
def axis_object(normA, labels, size, bold, italic, position):
    # axes arrows.
    a1, a2, a3 = normA
    mesh = pv.PolyData([[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [-1.1, -1.1, -1.1], [1.1, 1.1, 1.1]])

    colors = rcParams["detail.axis.color"] + [rcParams["detail.axis.color.center"]] + ["white", "white"]
    cmap = custom_colormap(colors)

    g0 = pv.Arrow(
        direction=a1,
        shaft_radius=rcParams["detail.axis.shaft.radius"],
        tip_radius=rcParams["detail.axis.tip.radius"],
        tip_length=rcParams["detail.axis.tip.length"],
        tip_resolution=rcParams["detail.axis.tip.resolution"],
    )
    g1 = pv.Arrow(
        direction=a2,
        shaft_radius=rcParams["detail.axis.shaft.radius"],
        tip_radius=rcParams["detail.axis.tip.radius"],
        tip_length=rcParams["detail.axis.tip.length"],
        tip_resolution=rcParams["detail.axis.tip.resolution"],
    )
    g2 = pv.Arrow(
        direction=a3,
        shaft_radius=rcParams["detail.axis.shaft.radius"],
        tip_radius=rcParams["detail.axis.tip.radius"],
        tip_length=rcParams["detail.axis.tip.length"],
        tip_resolution=rcParams["detail.axis.tip.resolution"],
    )
    g3 = pv.Sphere(
        rcParams["detail.axis.center.radius"],
        theta_resolution=rcParams["detail.axis.center.theta"],
        phi_resolution=rcParams["detail.axis.center.phi"],
    )
    g4 = pv.Sphere(0)
    idx = np.array([0, 1, 2, 3, 4, 5])
    mesh.point_data["scalars"] = idx
    axes = mesh.glyph(geom=(g0, g1, g2, g3, g4, g4), factor=rcParams["detail.axis.scale"], scale=False, rng=(0, 5))

    # axes labels.
    lbl_actor = vtk.vtkAxesActor()
    lbl_actor.SetShaftTypeToCylinder()
    lbl_actor.SetTipTypeToCone()
    lbl_actor.SetCylinderRadius(0.0)
    lbl_actor.SetConeRadius(0.0)
    lbl_actor.SetXAxisLabelText(labels[0])
    lbl_actor.SetYAxisLabelText(labels[1])
    lbl_actor.SetZAxisLabelText(labels[2])

    m = np.eye(4)
    m[0:3, 0] = a1
    m[0:3, 1] = a2
    m[0:3, 2] = a3
    transform = vtk.vtkTransform()
    transform.SetMatrix((m * position).ravel().tolist())
    lbl_actor.SetUserTransform(transform)

    x_p = lbl_actor.GetXAxisCaptionActor2D()
    y_p = lbl_actor.GetYAxisCaptionActor2D()
    z_p = lbl_actor.GetZAxisCaptionActor2D()
    for i, c, pos in zip([x_p, y_p, z_p], rcParams["detail.axis.label.color"], rcParams["detail.axis.label.position"]):
        i.GetPositionCoordinate().SetCoordinateSystemToWorld()
        i.GetPositionCoordinate().SetValue(*pos)
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
        rgb = all_colors[c][1]
        i.GetCaptionTextProperty().SetColor(*rgb)

    return axes, cmap, lbl_actor


# ==================================================
def plot_axis(plotter, normA, labels, size, bold, italic, position):
    axes, cmap, lbl_actor = axis_object(normA, labels, size, bold, italic, position)

    # axes.
    axes_actor = plotter.add_mesh(axes, show_scalar_bar=False, cmap=cmap, smooth_shading=True, name="axis")
    axes_widget = plotter.add_orientation_widget(axes_actor)
    axes_widget.SetViewport(*rcParams["detail.axis.viewport"])

    # axes labels.
    axes_label_widget = vtk.vtkOrientationMarkerWidget()
    axes_label_widget.SetOrientationMarker(lbl_actor)
    axes_label_widget.SetCurrentRenderer(plotter.renderer)
    axes_label_widget.SetInteractor(plotter.renderer.parent.iren.interactor)
    axes_label_widget.SetViewport(*rcParams["detail.axis.viewport"])
    axes_label_widget.SetEnabled(True)

    # set non-interactive for axes and labels.
    axes_widget.InteractiveOff()
    axes_label_widget.InteractiveOff()

    # axes actor.
    axes_actor = plotter.add_mesh(axes, show_scalar_bar=False, cmap=cmap, smooth_shading=True, name="axis")

    return axes_widget, axes_label_widget, axes_actor


# ==================================================
def view_vectors(A_norm, n):
    a1 = A_norm[0]
    a2 = A_norm[1]
    a3 = A_norm[2]
    n = NSArray(n, "vector", "value")
    if n.norm() < CHOP:
        return None, None

    v = NSArray(n[0] * a1 + n[1] * a2 + n[2] * a3, "vector", "value").normalize()

    if np.abs(v[2] - 1.0) < CHOP:  # v = (0,0,1)
        u = np.array([0, 1, 0])
    elif np.abs(v[2] + 1.0) < CHOP:  # v = (0,0,-1)
        u = np.array([0, -1, 0])
    else:
        vp = np.sqrt(1.0 - v[2] * v[2])
        u = np.array([-v[2] * v[0] / vp, -v[2] * v[1] / vp, vp])

    return v, u
