"""
Basic PolyData objects.

This module provides PolyData objects as fundamental elements to draw.
The following objects are available.

- sphere
- bond
- vector
- orbital
- vector stream
- line
- plane
- circle
- torus
- ellipsoid
- toroid
- box
- polygon
- text3d
- spline
- spline (parametric)
- isosurface
"""

import numpy as np
import sympy as sp
from vtk import vtkParametricSpline
import pyvista as pv
from pyvista.core.utilities import surface_from_para, geometric_sources
from gcoreutils.convert_util import text_to_sympy, text_to_list
from qtdraw.util.util_axis import get_view_vector
from qtdraw.util.util import create_grid
from qtdraw.core.pyvista_widget_setting import widget_detail as detail
from qtdraw.core.pyvista_widget_setting import CHOP


# ==================================================
def _str_poly_array(poly, xyz, var=["x", "y", "z"], size=1.0):
    """
    Convert from polynomial string to scalar array.

    Args:
        poly (str): polynomial string of var.
        xyz (list or numpy.ndarray): list of (x,y,z) points (given by create_sphere and .points), [[float]].
        var (list, optional): polynomial variables, [str].
        size (float, optional): normalize to max. value as size ?

    Returns:
        - (numpy.ndarray) -- scalar array.

    Note:
        - if size is positive, max. value is equivalent to size.
        - if size is negative, abs. value is scaled by size.
    """
    xyz = np.array(xyz, dtype=np.float64)
    r = sp.symbols(" ".join(var), real=True)
    v = {var[0]: r[0], var[1]: r[1], var[2]: r[2]}
    poly = poly.replace("sqrt", "SQ")
    poly = poly.replace("r", "(sqrt(x**2+y**2+z**2))")
    poly = poly.replace("SQ", "sqrt")
    ex = text_to_sympy(poly, local=v)
    x, y, z = xyz.T

    f = sp.lambdify(r, ex)
    fv = f(x, y, z)
    if ex.is_Number:  # for const.
        fv = np.full(np.size(x), fv, dtype=np.float64)

    max_f = np.abs(fv).max()
    if size > CHOP:
        if max_f > CHOP:
            scale = size / max_f
            fv *= scale
    else:
        fv *= np.abs(size)

    return fv


# ==================================================
def _str_vec_array(vec, xyz, normalize=True, var=["x", "y", "z"]):
    """
    Convert from polynomial string (vector) to vector and scalar (abs.) arrays.

    Args:
        vec (str): polynomial component.
        xyz (list or numpy.ndarray): list of (x,y,z) points (given by create_sphere and .points), [[float]].
        normalize (bool, optional): normalize ?
        var (list, optional): polynomial variables, [str].

    Returns:
        - (numpy.ndarray) -- vector array.
        - (numpy.ndarray) -- abs. value array.
    """
    vec = text_to_list(vec)
    xyz = np.array(xyz, dtype=np.float64)

    f1 = _str_poly_array(vec[0], xyz, var)
    f2 = _str_poly_array(vec[1], xyz, var)
    f3 = _str_poly_array(vec[2], xyz, var)
    f = np.array([f1, f2, f3]).T
    if normalize:
        fa = np.linalg.norm(f, axis=1).max()
        if fa > CHOP:
            f = f / fa

    fs = np.linalg.norm(f, axis=1)

    return f, fs


# ==================================================
def create_sphere(
    radius,
    theta_phi_range=None,
    theta_phi_resolution=None,
):
    """
    Create sphere object.

    Args:
        radius (float): radius.
        theta_phi_range (list or numpy.ndarray, optional): theta and phi range, [[float]].
        theta_phi_resolution (list): theta and phi resolution, [int].

    Returns:
        - (vtk.PolyData) -- sphere object.

    Note:
        - if theta_phi_range/theta_phi_resolution is None, default is used.
    """
    if theta_phi_range is None:
        theta_phi_range = detail["theta_phi_range"]

    if theta_phi_resolution is None:
        theta_phi_resolution = detail["theta_phi_resolution"]

    # note that notation (theta, phi) are opposite as usual.
    obj = pv.Sphere(
        radius=radius,
        phi_resolution=theta_phi_resolution[0],
        theta_resolution=theta_phi_resolution[1],
        start_phi=theta_phi_range[0][0],
        end_phi=theta_phi_range[0][1],
        start_theta=theta_phi_range[1][0],
        end_theta=theta_phi_range[1][1],
    )

    return obj


# ==================================================
def create_bond(direction, width=1.0, twotone=True):
    """
    Create bond object.

    Args:
        direction (list or numpy.ndarray): bond direction (cartesian), [float].
        width (float, optional): width.
        twotone (bool, optional): twotone color ?

    Returns:
        - (vtk.PolyData) -- cylinder object

    Note:
        - bond position is at center.
    """
    resolution = detail["bond_resolution"]

    direction = np.array(direction, dtype=np.float64)
    length = np.linalg.norm(direction)

    if twotone:
        p = pv.Cylinder(
            direction=direction,
            radius=width,
            height=length / 2,
            resolution=resolution,
        )
        m = pv.PolyData([(-0.25 * direction).tolist(), (0.25 * direction).tolist()])
        m.point_data["scalars"] = [0, 1]
        obj = m.glyph(geom=(p, p), scale=False, rng=(0, 1), orient=False)
    else:
        p = pv.Cylinder(
            direction=direction,
            radius=width,
            height=length,
            resolution=resolution,
        )
        m = pv.PolyData([[0.0, 0.0, 0.0]])
        m.point_data["scalars"] = [0]
        obj = m.glyph(geom=(p), scale=False, rng=(0, 0), orient=False)

    return obj


# ==================================================
def create_vector(
    direction,
    length=1.0,
    width=1.0,
    offset=-0.43,
    shaft_radius=1.0,
    tip_radius=2.0,
    tip_length=0.25,
):
    """
    Create vector object.

    Args:
        direction (list or numpy.ndarray): direction (cartesian), [float].
        length (float, optional): length.
        width (float, optional): width.
        offset (float, optional): offest ratio.
        shaft_radius (float, optional) :shaft radius.
        tip_radius (float, optional): tip radius.
        tip_length (float, optional): tip length.

    Returns:
        - (vtk.PolyData) -- arrow object.

    Note:
        - if length is negative, norm of direction multiplied by |length| is used.
    """
    shaft_resolution = detail["shaft_resolution"]
    tip_resolution = detail["tip_resolution"]

    direction = np.array(direction, dtype=np.float64)
    norm = np.linalg.norm(direction)
    if length < CHOP:
        length = abs(length) * norm
    direction = length * direction / norm

    obj = pv.Arrow(
        start=offset * direction,
        direction=direction,
        scale=length,
        shaft_radius=shaft_radius * width / length,
        tip_radius=tip_radius * width / length,
        tip_length=tip_length,
        shaft_resolution=shaft_resolution,
        tip_resolution=tip_resolution,
    )

    return obj


# ==================================================
def create_orbital(
    shape,
    surface="",
    size=1.0,
    theta_phi_range=None,
    theta_phi_resolution=None,
):
    """
    Create orbital object.

    Args:
        shape (str): (x,y,z) shape (cartesian).
        surface (str, optional): (x,y,z) surface color (cartesian).
        size (float, optional): size.
        theta_phi_range (list or numpy.ndarray, optional): theta and phi range, [[float]].
        theta_phi_resolution (list): theta and phi resolution, [int].

    Returns:
        - (vtk.PolyData) -- orbital object with "surface".

    Note:
        - if surface is "", the same one of shape is used.
        - if size is positive, max. value is equivalent to size.
        - if size is negative, abs. value is scaled by size.
        - if theta_phi_range is None, default is used.
        - if theta_phi_resolution is None, default is used.
    """
    shape = str(shape)
    surface = str(surface)

    if surface == "":
        surface = shape

    if theta_phi_range is None:
        theta_phi_range = detail["theta_phi_range"]

    obj = create_sphere(1.0, theta_phi_range=theta_phi_range, theta_phi_resolution=theta_phi_resolution)
    sp = obj.points
    fs = np.abs(_str_poly_array(shape, sp, size=size))
    fc = _str_poly_array(surface, sp)
    obj.points = np.tile(fs, (3, 1)).T * sp
    obj["surface"] = np.real(fc)

    return obj


# ==================================================
def create_stream(
    shape="1",
    vector="[x,y,z]",
    size=1.0,
    theta_phi_range=None,
    division=None,
    length=0.1,
    width=0.1,
    offset=-0.43,
    abs_scale=False,
    shaft_radius=1.0,
    tip_radius=2.0,
    tip_length=0.25,
):
    r"""
    Create steam vector object.

    Args:
        shape (str, optional): f(x,y,z) shape (cartesian).
        vector (str, optional): stream vector [vx(x,y,z),vy(x,y,z),vz(x,y,z)] (cartesina).
        size (float, optional): shape size.
        theta_phi_range (list or numpy.ndarray, optional): theta and phi range, [[float]].
        division (list, optional): division for theta and phi, [int].
        length (float, optional): length.
        width (float, optional): width.
        offset (float, optional): offest ratio.
        abs_scale (bool, optional): use \|v(x,y,z)\| * length ?
        shaft_radius (float, optional) :shaft radius.
        tip_radius (float, optional): tip radius.
        tip_length (float, optional): tip length.

    Returns:
        - (vtk.PolyData) -- orbital object with "vector" and "vector_abs".

    Note:
        - if theta_phi_range/division is None, default is used.
        - if size is negative, shape is normalized.
    """
    if division is None:
        division = detail["theta_phi_division"]

    if theta_phi_range is None:
        theta_phi_range = detail["theta_phi_range"]

    stream_vec = create_orbital(
        shape,
        surface="0",
        size=size,
        theta_phi_range=theta_phi_range,
        theta_phi_resolution=division,
    )
    fv, fva = _str_vec_array(vector, stream_vec.points)

    # eliminate zero length points.
    stream_vec["vector"] = fv
    stream_vec["vector_abs"] = fva
    stream_vec = stream_vec.extract_points(fva > CHOP, include_cells=False)

    g = create_vector(
        np.array([1.0, 0.0, 0.0]),
        length=length,
        width=width,
        offset=offset,
        shaft_radius=shaft_radius,
        tip_radius=tip_radius,
        tip_length=tip_length,
    )

    scale = "vector_abs" if abs_scale else None
    obj = stream_vec.glyph(orient="vector", scale=scale, factor=1.0, geom=g)

    return obj


# ==================================================
def create_line(direction, width=1.0, arrow1=False, arrow2=False, tip_radius=2.0, tip_length=0.1):
    """
    Create line object.

    Args:
        direction (list or numpy.ndarray): bond direction (cartesian), [float].
        width (float, optional): width.
        arrow1 (bool, optional): arrow at start point ?
        arrow2 (bool, optional): arrow at end point ?
        tip_radius (float, optional): tip radius.
        tip_length (float, optional): tip length.

    Returns:
        - (vtk.PolyData) -- cylinder object
    """
    resolution = detail["bond_resolution"]

    direction = np.array(direction, dtype=np.float64)
    length = np.linalg.norm(direction)

    obj = pv.Cylinder(center=direction / 2, direction=direction, radius=width, height=length, resolution=resolution)

    if arrow1:
        a1 = create_vector(
            -direction,
            tip_length * width * 100.0,
            1.5 * tip_radius * width,
            offset=0.0,
            shaft_radius=0.0,
            tip_radius=1.0,
            tip_length=1.0,
        )
    if arrow2:
        a2 = create_vector(
            direction,
            tip_length * width * 100.0,
            1.5 * tip_radius * width,
            offset=0.0,
            shaft_radius=0.0,
            tip_radius=1.0,
            tip_length=1.0,
        ).translate(direction, inplace=True)

    if arrow1:
        obj = obj + a1
    if arrow2:
        obj = obj + a2

    return obj


# ==================================================
def create_plane(normal, x_size=1.0, y_size=1.0):
    """
    Create plane object.

    Args:
        normal (list or numpy.ndarray): normal vector (cartesian), [float].
        x_size (float, optional): x size.
        y_size (float, optional): y size.

    Returns:
        - (vtk.PolyData) -- plane object.
    """
    obj = pv.Plane(direction=normal, i_size=x_size, j_size=y_size)

    return obj


# ==================================================
def create_circle(normal, size=0.5):
    """
    Create circle object.

    Args:
        normal (list or numpy.ndarray): normal vector (cartesian), [float].
        size (float, optional): size.

    Returns:
        - (vtk.PolyData) -- circle object.
    """
    resolution = detail["circle_resolution"]
    obj = pv.Circle(radius=size, resolution=resolution)

    obj.rotate_y(90, inplace=True)
    geometric_sources.translate(obj, (0, 0, 0), normal)

    return obj


# ==================================================
def create_torus(normal, size=0.5, width=0.15):
    """
    Create torus object.

    Args:
        normal (list or numpy.ndarray): normal vector (cartesian), [float].
        size (float, optional): size.
        width (float, optioanl): torus width.

    Returns:
        - (vtk.PolyData) -- torus object.
    """
    obj = pv.ParametricTorus(ringradius=size, crosssectionradius=width)

    obj.rotate_y(90, inplace=True)
    geometric_sources.translate(obj, (0, 0, 0), normal)

    return obj


# ==================================================
def create_ellipsoid(normal, x_size=0.5, y_size=0.4, z_size=0.3):
    """
    Create ellipsoid object.

    Args:
        normal (list or numpy.ndarray): normal vector (cartesian), [float].
        x_size (float, optional): x_size.
        y_size (float, optional): y_size.
        z_size (float, optional): z_size.

    Returns:
        - (vtk.PolyData) -- ellipsoid object.
    """
    obj = pv.ParametricEllipsoid(xradius=x_size, yradius=y_size, zradius=z_size)

    obj.rotate_y(90, inplace=True)
    geometric_sources.translate(obj, (0, 0, 0), normal)

    return obj


# ==================================================
def create_toroid(normal, size=0.5, width=0.15, x_scale=1.0, y_scale=1.0, z_scale=1.0, ring_shape=0.3, tube_shape=0.3):
    """
    Create ellipsoid object.

    Args:
        normal (list or numpy.ndarray): normal vector (cartesian), [float].
        size (float, optional): ring size.
        width (float, optional): tube width.
        x_scale (float, optional): scale factor for x axis.
        y_scale (float, optional): scale factor for y axis.
        z_scale (float, optional): scale factor for z axis.
        ring_shape (float, optional): ring shape.
        tube_shape (float, optional): tube shape.

    Returns:
        - (vtk.PolyData) -- toroid object.
    """
    obj = pv.ParametricSuperToroid(
        ringradius=size, crosssectionradius=width, xradius=x_scale, yradius=y_scale, zradius=z_scale, n1=ring_shape, n2=tube_shape
    )

    obj.rotate_y(90, inplace=True)
    geometric_sources.translate(obj, (0, 0, 0), normal)

    return obj


# ==================================================
def create_box(a1=None, a2=None, a3=None):
    """
    Create box object.

    Args:
        a1 (numpy.ndarray, optional): a1 vector (cartesian).
        a2 (numpy.ndarray, optional): a2 vector (cartesian).
        a3 (numpy.ndarray, optional): a3 vector (cartesian).

    Returns:
        - (vtk.PolyData) -- cube object.

    Note:
        - if a1/a2/a3 is None, unit vector is used.
    """
    if a1 is None:
        a1 = np.array([1, 0, 0])
    if a2 is None:
        a2 = np.array([0, 1, 0])
    if a3 is None:
        a3 = np.array([0, 0, 1])

    A = np.eye(4)
    A[0:3, 0] = a1
    A[0:3, 1] = a2
    A[0:3, 2] = a3

    obj = pv.Cube(bounds=(0.0, 1.0, 0.0, 1.0, 0.0, 1.0), clean=False)
    obj.transform(A, inplace=True)

    return obj


# ==================================================
def create_polygon(point, connectivity):
    """
    Create polygon object.

    Args:
        point (list or numpy.ndarray): vertices (cartesian), [float].
        conectivity (list): list connectivities of #point for each plane, [[int]].

    Returns:
        - (vtk.PolyData) -- polygon object.
    """
    n = len(point)
    connectivity = [[len(cell), *[int(i) % n for i in cell]] for cell in connectivity]
    cell = np.hstack(connectivity)
    obj = pv.PolyData(point, cell)

    return obj


# ==================================================
def create_text3d(text, size=1.0, view=None, depth=1.0, offset=[0, 0, 0], A=None):
    """
    Create text3d object.

    Args:
        text (str): text.
        size (float, optional): size.
        view (list, optional): normal indices, [int].
        depth (float, optional): depth.
        offset (list or numpy.ndarray, optional): offset, [float].
        A (numpy.ndarray, optional): (a1, a2, a3) in each column, 4x4 (cartesian).

    Returns:
        - (vtk.PolyData) -- text3d object.

    Note:
        - if normal is None, default is used.
        - if A is None, unit vector is used.
    """
    if view is None:
        view = detail["text_normal"]

    if A is None:
        A = np.eye(4)

    view, viewup = get_view_vector(view, A)

    A = np.eye(4)
    A[0:3, 0] = np.cross(viewup, view)
    A[0:3, 1] = viewup
    A[0:3, 2] = view
    A[0:3, 3] = np.array(offset, dtype=np.float64)

    obj = pv.Text3D(string=text, depth=depth)
    obj.scale([size] * 3, inplace=True)
    obj.transform(A, inplace=True)

    return obj


# ==================================================
def create_spline(
    point, width=1.0, n_interp=500, closed=False, natural=True, arrow1=False, arrow2=False, tip_radius=2.0, tip_length=0.1
):
    """
    Create spline object.

    Args:
        point (list or numpy.ndarray): points to be connected, [[float]].
        width (float, optional); width.
        n_interp (int, optional): number of interpolation points.
        closed (bool, optional): closed spline ?
        natural (bool, optional): natural boundary ?
        arrow1 (bool, optional): arrow at start point ?
        arrow2 (bool, optional): arrow at end point ?
        tip_radius (float, optional): tip radius.
        tip_length (float, optional): tip length.

    Returns:
        - (vtk.PolyData) -- spline object.
    """
    point = np.array(point, dtype=np.float64)
    spline_function = vtkParametricSpline()
    spline_function.SetPoints(pv.vtk_points(points=point, deep=False))

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
    u_res = n_interp
    if u_res is None:
        u_res = point.shape[0]

    u_res -= 1
    spline = surface_from_para(parametric_function=spline_function, u_res=u_res)
    obj = spline.compute_arc_length()
    obj.tube(radius=width, inplace=True)

    if closed:
        return obj

    if arrow1:
        d1 = spline.points[0] - spline.points[1]
        a1 = create_vector(
            d1, tip_length * width * 100.0, 1.5 * tip_radius * width, offset=0.0, shaft_radius=0.0, tip_radius=1.0, tip_length=1.0
        ).translate(spline.points[0], inplace=True)
    if arrow2:
        d2 = spline.points[-1] - spline.points[-2]
        a2 = create_vector(
            d2, tip_length * width * 100.0, 1.5 * tip_radius * width, offset=0.0, shaft_radius=0.0, tip_radius=1.0, tip_length=1.0
        ).translate(spline.points[-1], inplace=True)

    if arrow1:
        obj = obj + a1
    if arrow2:
        obj = obj + a2

    return obj


# ==================================================
def create_spline_t(
    point,
    t_range=None,
    width=1.0,
    n_interp=300,
    closed=False,
    natural=True,
    arrow1=False,
    arrow2=False,
    tip_radius=2.0,
    tip_length=0.1,
    A=None,
):
    """
    Create parametric spline object.

    Args:
        point (str): sympy expression for point in terms of "t".
        t_range (list or numpy.ndarray, optional): t range, [start, stop, step], [float].
        width (float, optional): width.
        n_interp (int, optional): interpolation points.
        closed (bool, optional): closed spline ?
        natural (bool, optional): natural boundary ?
        arrow1 (bool, optional): arrow at start point ?
        arrow2 (bool, optional): arrow at end point ?
        tip_radius (float, optional): tip radius.
        tip_length (float, optional): tip length.
        A (numpy.ndarray, optional): (a1, a2, a3) in each column, 4x4 (cartesian).

    Returns:
        - (vtk.PolyData) -- parameteric spline object.

    Note:
        - if t_range is None, default is used.
        - if A is None, unit vector is used.
    """
    if t_range is None:
        t_range = detail["spline_t_range"]

    if A is None:
        A = np.eye(4)

    point = text_to_list(point)
    tp = np.arange(t_range[0], t_range[1], t_range[2])

    t = sp.symbols("t", real=True)
    ex = [text_to_sympy(i, local={"t": t}) for i in point]

    pts = np.asarray([np.full(tp.shape, i) if i.is_Number else sp.lambdify(t, i, modules="numpy")(tp) for i in ex])
    pointA = np.dot(A[0:3, 0:3], pts).T

    obj = create_spline(pointA, width, n_interp, closed, natural, arrow1, arrow2, tip_radius, tip_length)

    return obj


# ==================================================
def create_isosurface(grid_data, value, surface_name):
    """
    Create isosurface.

    Args:
        grid_data (dict): grid data.
        value (list or numpy.ndarray): value of isosurface.
        surface_name (str): surface data.

    Returns:
        - (vtk.DataSet) -- isosurface object.

    Note:
        - n : [nx,ny,nz] division of grid.
        - origin : [rx,ry,rz] origin in fractional coordinate.
        - Ag : [g1,g2,g3] grid vectors in 4x4 matrix.
        - data : data at each grid point.
        - surface : surface data at each grid point.
        - endpoint : include endpoint ?
        - row_major : row-major grid ?
    """
    n = np.array(grid_data["n"])
    origin = grid_data["origin"]
    A = grid_data["Ag"]
    data = np.array(grid_data["data"])
    endpoint = grid_data["endpoint"]
    row_major = grid_data["row_major"]
    if surface_name != "":
        surface = grid_data["surface"][surface_name]
    else:
        surface = None

    if origin is None:
        origin = np.array([0.0, 0.0, 0.0])
    else:
        origin = np.array(origin)
    if A is None:
        A = np.eye(4)
    else:
        A = np.array(A)
    if surface is not None:
        surface = np.array(surface)

    # convert data in column major.
    if row_major:
        data = data.reshape(n[0], n[1], n[2])
        data = data[:, [2, 1, 0]]
        data = data.reshape(n[0] * n[1] * n[2])
        if surface is not None:
            surface = surface.reshape(n[0], n[1], n[2])
            surface = surface[:, [2, 1, 0]]
            surface = surface.reshape(n[0] * n[1] * n[2])

    r = origin + np.array([1.0, 1.0, 1.0])
    grid = create_grid(n, origin, r, A, endpoint)
    grid[f"data"] = data

    if surface is not None:
        grid[surface_name] = surface

    obj = grid.contour(value, scalars="data")

    return obj


# ==================================================
def create_orbital_data(shape, surface=None, size=1.0, spherical_plot=False, point_size=0.03):
    """
    Create orbital object from data.

    Args:
        shape (ndarray): (x,y,z) shape (cartesian).
        surface (ndarray, optional): (x,y,z) surface color (cartesian).
        size (float, optional): size.
        spherical_plot (bool, optional): spherical-like plot ?
        point_size (float, optional): point size.

    Returns:
        - (vtk.PolyData) -- orbital object with "surface".

    Note:
        - if surface is None, the same one of shape is used.
        - if size is positive, max. value is equivalent to size.
        - if size is negative, abs. value is scaled by size.
        - if point_size is None, no point is shown.
    """
    # shape data.
    if surface is None:
        surface = np.full(shape.shape[0], 1.0)

    if spherical_plot:
        r = np.abs(surface)
        shape = np.tile(r, (3, 1)).T * shape

    max_f = np.linalg.norm(shape, axis=1).max()
    if size > CHOP:
        if max_f > CHOP:
            scale = size / max_f
            shape *= scale
    else:
        shape *= np.abs(size)

    orbital = pv.PolyData(shape)
    orbital["surface"] = surface

    if point_size is None:
        return orbital
    else:
        g = create_sphere(point_size)
        obj = orbital.glyph(orient=False, scale=None, factor=1.0, geom=g)
        return obj


# ==================================================
def create_stream_data(
    shape,
    surface,
    vector,
    size=1.0,
    length=0.1,
    width=0.1,
    offset=-0.43,
    abs_scale=False,
    shaft_radius=1.0,
    tip_radius=2.0,
    tip_length=0.25,
    spherical_plot=False,
):
    r"""
    Create steam vector object.

    Args:
        shape (ndarray): f(x,y,z) shape (cartesian).
        surface (ndarray, optional): (x,y,z) surface color (cartesian).
        vector (ndarray): stream vector [vx(x,y,z),vy(x,y,z),vz(x,y,z)] (cartesina).
        size (float, optional): shape size.
        length (float, optional): length.
        width (float, optional): width.
        offset (float, optional): offest ratio.
        abs_scale (bool, optional): use \|v(x,y,z)\| * length ?
        shaft_radius (float, optional) :shaft radius.
        tip_radius (float, optional): tip radius.
        tip_length (float, optional): tip length.
        spherical_plot (bool, optional): spherical-like plot ?

    Returns:
        - (vtk.PolyData) -- orbital object with "vector" and "vector_abs".

    Note:
        - if size is negative, shape is normalized.
    """
    stream_vec = create_orbital_data(shape, surface=surface, size=size, spherical_plot=spherical_plot, point_size=None)
    vec_norm = np.linalg.norm(vector, axis=1)

    # eliminate zero length points.
    stream_vec["vector"] = vector
    stream_vec["vector_abs"] = vec_norm
    stream_vec = stream_vec.extract_points(vec_norm > CHOP, include_cells=False)

    g = create_vector(
        np.array([1.0, 0.0, 0.0]),
        length=length,
        width=width,
        offset=offset,
        shaft_radius=shaft_radius,
        tip_radius=tip_radius,
        tip_length=tip_length,
    )

    scale = "vector_abs" if abs_scale else None
    obj = stream_vec.glyph(orient="vector", scale=scale, factor=1.0, geom=g)

    return obj
