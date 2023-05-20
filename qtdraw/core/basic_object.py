import numpy as np
import sympy as sp
import pyvista as pv
from gcoreutils.nsarray import NSArray
from gcoreutils.convert_util import text_to_list, text_to_sympy
from qtdraw.core.util import view_vectors, SplineEx

CHOP = 1e-4


# ==================================================
def str_poly_array(poly, xyz, normalize=True, var=["x", "y", "z"]):
    """
    convert from polynomial string to scalar array.

    Args:
        poly (str): polynomial string of var.
        xyz (ndarray): list of (x,y,z) points (given by create_sphere and .points).
        normalize (bool, optional): normalize ?
        var (list, optional): polynomial variables.

    Returns:
        ndarray: scalar array.
    """
    r = sp.symbols(" ".join(var), real=True)
    v = {var[0]: r[0], var[1]: r[1], var[2]: r[2]}
    poly = poly.replace("sqrt", "SQ")
    poly = poly.replace("r", "(sqrt(x**2+y**2+z**2))")
    poly = poly.replace("SQ", "sqrt")
    ex = text_to_sympy(poly, local=v)
    x, y, z = xyz.T

    f = sp.lambdify(r, ex)
    fv = f(x, y, z)
    if not sorted(map(str, ex.atoms(sp.Symbol))):  # for const.
        fv = np.full(np.size(x), fv)

    if poly != "0" and normalize:
        fv = fv / np.abs(fv).max()

    return fv


# ==================================================
def str_vec_array(vec, xyz, normalize=True, var=["x", "y", "z"]):
    """
    convert from polynomial string (vector) to vector and scalar (abs.) arrays.

    Args:
        vec (NSArray): polynomial component.
        xyz (ndarray): list of (x,y,z) points (given by create_sphere and .points).
        normalize (bool, optional): normalize ?
        var (list, optional): polynomial variables.

    Returns: tuple
        - ndarray: vector array.
        - ndarray: abs. value array.
    """
    f1 = str_poly_array(str(vec[0]), xyz, False, var)
    f2 = str_poly_array(str(vec[1]), xyz, False, var)
    f3 = str_poly_array(str(vec[2]), xyz, False, var)
    f = np.array([f1, f2, f3]).T
    if normalize:
        fa = np.linalg.norm(f, axis=1).max()
        f = f / fa

    fs = np.linalg.norm(f, axis=1)

    return f, fs


# ==================================================
def create_sphere(radius, theta_phi_resolution, theta_range, phi_range):
    """
    create sphere object.

    Args:
        radius (float): radius.
        theta_phi_resolution (list): theta-phi resolution.
        theta_range (list): theta range.
        phi_range (list): phi range.

    Returns:
        PolyData: sphere object.
    """
    th, phi = theta_phi_resolution
    th0, th1 = theta_range
    ph0, ph1 = phi_range
    obj = pv.Sphere(
        radius=radius, theta_resolution=phi, phi_resolution=th, start_phi=th0, end_phi=th1, start_theta=ph0, end_theta=ph1
    )
    return obj


# ==================================================
def create_bond(v, width=1.0, two=True):
    """
    bond object.

    Args:
        v (str or NSArray): bond direction vector (cartesian).
        width (float, optional): width.
        two (bool, optional): twotone color ?

    Returns:
        PolyData: cylinder object
    """
    if not isinstance(v, (str, NSArray)):
        raise KeyError(f"{type(v)} is invalid.")

    if type(v) == str:
        v = NSArray(v, fmt="value")

    length = v.norm()

    if two:
        p = pv.Cylinder(direction=v.numpy(), radius=0.018 * width, height=length / 2)
        m = pv.PolyData([(-v * 0.25).tolist(), (v * 0.25).tolist()])
        m.point_data["scalars"] = [0, 1]
        obj = m.glyph(geom=(p, p), scale=False, rng=(0, 1))
    else:
        p = pv.Cylinder(direction=v.numpy(), radius=0.018 * width, height=length)
        m = pv.PolyData([[0.0, 0.0, 0.0]])
        m.point_data["scalars"] = [0]
        obj = m.glyph(geom=(p), scale=False, rng=(0, 0))

    return obj


# ==================================================
def create_vector(v, length, width, offset, tip_l, shaft_r, tip_r):
    """
    vector object.

    Args:
        v (str or NSArray): vector direction (to be normalized, cartesian).
        length (float): length.
        width (float): width.
        offset (float): offest ratio.

    Returns:
        PolyData: arrow object.
    """
    if not isinstance(v, (str, NSArray)):
        raise KeyError(f"{type(v)} is invalid.")

    if type(v) == str:
        v = NSArray(v, fmt="value")

    v = v.normalize()

    obj = pv.Arrow(
        offset * v.numpy() * length,
        v.numpy(),
        tip_length=tip_l,
        shaft_radius=shaft_r * width / length,
        tip_radius=tip_r * width / length,
        scale=length,
        tip_resolution=100,
        shaft_resolution=100,
    )
    return obj


# ==================================================
def create_orbital(shape, surface, size, theta_phi_res, scale, theta_range, phi_range):
    """
    orbital object.

    Args:
        shape (str): (x,y,z) shape (cartesian).
        surface (str): (x,y,z) surface color (cartesian).
        size (float): size.
        theta_phi_res (tuple): resolution for theta and phi.
        scale (bool): if True, shappe is scaled.
        theta_range (list): theta range.
        phi_range (list): phi range.

    Returns:
        PolyData: orbital object with "surface".
    """
    obj = create_sphere(size, theta_phi_res, theta_range=theta_range, phi_range=phi_range)
    sp = obj.points
    fs = np.abs(str_poly_array(shape, sp, normalize=scale))
    fc = str_poly_array(surface, sp)
    obj.points = np.tile(fs, (3, 1)).T * sp
    obj["surface"] = np.real(fc)

    return obj


# ==================================================
def create_stream_vector(shape, vector, size, theta_phi_res, theta_range, phi_range):
    """
    steam vector object.

    Args:
        shape (str): f(x,y,z) shape (cartesian).
        vector(str or NSArray): "[vx(x,y,z),vy(x,y,z),vz(x,y,z)]" vector string (cartesina).
        size (float): size.
        theta_phi_res (tuple): resolution for theta and phi.
        theta_range (list): theta range.
        phi_range (list): phi range.

    Returns:
        PolyData: orbital object with "vector" and "vector_abs".
    """
    if not isinstance(vector, (str, NSArray)):
        raise KeyError(f"{type(vector)} is invalid.")

    if type(vector) == str:
        vector = NSArray(vector)

    obj = create_orbital(shape, "0", size, theta_phi_res, True, theta_range, phi_range)
    fv, fva = str_vec_array(vector, obj.points)
    obj["vector"] = fv
    obj["vector_abs"] = fva

    return obj


# ==================================================
def create_plane(v, x=1.0, y=1.0):
    """
    plane object.

    Args:
        v (str or NSArray): vector direction (to be normalized, cartesian).
        x (float, optional): x size.
        y (float, optional): y size.

    Returns:
        PolyData: plane object.
    """
    if not isinstance(v, (str, NSArray)):
        raise KeyError(f"{type(v)} is invalid.")

    if type(v) == str:
        v = NSArray(v, fmt="value")

    v = v.normalize()

    obj = pv.Plane(direction=v.numpy(), i_size=x, j_size=y)
    return obj


# ==================================================
def create_box(a1, a2, a3):
    """
    box object.

    Args:
        a1 (str or NSArray): 1st direction (reduced).
        a2 (str or NSArray): 2nd direction (reduced).
        a3 (str or NSArray): 3rd direction (reduced).

    Returns:
        PolyData: cube object.
    """
    if not isinstance(a1, (str, NSArray)):
        raise KeyError(f"{type(a1)} is invalid.")
    if not isinstance(a2, (str, NSArray)):
        raise KeyError(f"{type(a2)} is invalid.")
    if not isinstance(a3, (str, NSArray)):
        raise KeyError(f"{type(a3)} is invalid.")

    if type(a1) == str:
        a1 = NSArray(a1, fmt="value")
    if type(a2) == str:
        a2 = NSArray(a2, fmt="value")
    if type(a3) == str:
        a3 = NSArray(a3, fmt="value")

    A = np.eye(4)
    A[0:3, 0] = a1.numpy()
    A[0:3, 1] = a2.numpy()
    A[0:3, 2] = a3.numpy()

    obj = pv.Cube(bounds=(0.0, 1.0, 0.0, 1.0, 0.0, 1.0))
    obj.transform(A, inplace=True)
    return obj


# ==================================================
def create_linebox(a1, a2, a3):
    """
    linebox object.

    Args:
        a1 (str or NSArray): 1st direction (reduced).
        a2 (str or NSArray): 2nd direction (reduced).
        a3 (str or NSArray): 3rd direction (reduced).

    Returns:
        PolyData: linebox object.
    """
    if not isinstance(a1, (str, NSArray)):
        raise KeyError(f"{type(a1)} is invalid.")
    if not isinstance(a2, (str, NSArray)):
        raise KeyError(f"{type(a2)} is invalid.")
    if not isinstance(a3, (str, NSArray)):
        raise KeyError(f"{type(a3)} is invalid.")

    if type(a1) == str:
        a1 = NSArray(a1, fmt="value")
    if type(a2) == str:
        a2 = NSArray(a2, fmt="value")
    if type(a3) == str:
        a3 = NSArray(a3, fmt="value")

    A = np.eye(4)
    A[0:3, 0] = a1.numpy()
    A[0:3, 1] = a2.numpy()
    A[0:3, 2] = a3.numpy()

    pts = np.array([[0.0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0], [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]])
    lines = np.array([5, 0, 1, 2, 3, 0, 5, 4, 5, 6, 7, 4, 2, 0, 4, 2, 1, 5, 2, 2, 6, 2, 3, 7])
    obj = pv.PolyData(pts, lines=lines)
    obj.transform(A, inplace=True)

    return obj


# ==================================================
def create_polygon(pt, cnt):
    """
    polygon object.

    Args:
        pt (str or NSArray): vertices (cartesian).
        cnt (list): list of connected vectices for each plane.

    Returns:
        PolyData: polygon object.
    """
    if not isinstance(pt, (str, NSArray)):
        raise KeyError(f"{type(pt)} is invalid.")

    if type(pt) == str:
        pt = NSArray(pt, fmt="value")

    n = len(pt)
    if type(cnt) is str:
        cnt = text_to_list(cnt)
    cnt = [[len(cell), *[int(i) % n for i in cell]] for cell in cnt]
    cell = np.hstack(cnt)
    obj = pv.PolyData(pt.numpy(), cell)

    return obj


# ==================================================
def create_text(txt, size, normal, A, offset, depth=1.0):
    """
    text3d object.

    Args:
        txt (str): text.
        depth (float, optional): depth.

    Returns:
        PolyData: text3d object.
    """
    v, u = view_vectors(A, normal)
    A = NSArray(
        [
            [u[1] * v[2] - u[2] * v[1], u[0], v[0], offset[0]],
            [u[2] * v[0] - u[0] * v[2], u[1], v[1], offset[1]],
            [u[0] * v[1] - u[1] * v[0], u[2], v[2], offset[2]],
            [0, 0, 0, 1],
        ],
        "matrix",
        "value",
    )

    obj = pv.Text3D(txt, depth)
    obj.scale([size] * 3, inplace=True)
    obj.transform(A, inplace=True)

    return obj


# ==================================================
def create_spline(pts, n_interp, width=1.0, closed=False, natural=True):
    """
    spline object.

    Args:
        pts (str or NSArray): points.
        width (float, optional); width.
        n_interp (int, optional): number of interpolation points.
        closed (bool, optional): closed spline ?
        natural (bool, optional): natural boundary ?

    Returns:
        PolyData: spline object.
    """
    if not isinstance(pts, (str, NSArray)):
        raise KeyError(f"{type(pts)} is invalid.")

    if type(pts) == str:
        pts = NSArray(pts, fmt="value")

    obj = SplineEx(pts.numpy(), n_interp, closed, natural)
    obj.tube(radius=0.01 * width, inplace=True)
    return obj
