# sample.py
"""
Example for QtDraw.
"""
from qtdraw.qt_draw import QtDraw


# ==================================================
# view range [lower, upper] in unit of cell.
view_range = [[-1, -1, 0], [1, 1, 1]]

# positions to show objects, and for spline curve.
points = [
    [0.0, 0.0, 0.0],
    [0.5, 0.0, 0.0],
    [0.5, 0.5, 0.0],
    [0.0, 0.5, 0.0],
    [0.0, 0.0, 0.5],
    [0.5, 0.0, 0.5],
    [0.5, 0.5, 0.5],
    [0.0, 0.5, 0.5],
    [0.25, 0.25, 0.25],
]


# ==================================================
def draw():
    # initialize QtDraw.
    p = QtDraw(model="sample", view_range=view_range)
    # set hexagonal axis.
    p.set_crystal("hexagonal")

    # plot site (sphere).
    p.plot_site(points[0:2], size=0.5, name="S", label="L", show_lbl=True)
    # plot bond.
    p.plot_bond(points[1:3], vector=[-0.5, -0.5, 0], color="red", color2="blue")
    # plot vector.
    p.plot_vector(points[2], vector=[0, 0.5, 0], length=0.4)
    # plot orbital.
    p.plot_orbital(points[3], shape="x y z", surface="", size=0.2)
    # plot stream and orbital.
    p.plot_orbital(points[4], "1", size=0.1, theta_range=[0, 120], phi_range=[0, 270], color="snow")
    p.plot_stream_vector(
        points[4], shape="1", vector="[x, y, z]", size=0.1, v_size=0.15, theta=4, phi=8, theta_range=[0, 120], phi_range=[0, 270]
    )
    # plot plane.
    p.plot_plane(points[5], normal=[1, 1, 0], x=0.2, y=0.2)
    # plot box.
    p.plot_box(points[6], a1=[0.1, 0, 0], a2=[0, 0.1, 0], a3=[0, 0, 0.1])
    # plot 3d text.
    p.plot_text3d(points[7], text="sample text", normal=[4, 5, 2], offset=[0.1, 0.1, 0.1], depth=3)
    # plot spline curve from data.
    p.plot_spline(points[0], point=points, width=1, n_interp=100)
    # plot spline curve by parametric function.
    p.plot_spline_t(points[0], "[cos(2pi t),sin(2pi t),t]", [0, 1.1, 0.1], width=1, color="sky", n_interp=100)
    # plot polygon.
    p.plot_polygon(points[8])
    # plot caption.
    p.plot_caption(points, bold=True, color="licorice")
    # plot 2d text.
    p.plot_text([0.02, 0.95], r"$\int \|\psi(x)\|^2 dx=1$")

    # set default view.
    p.set_view()

    # by calling show() in the end of all plots, objects are shown.
    p.show()


# ==================================================
if __name__ == "__main__":
    draw()
