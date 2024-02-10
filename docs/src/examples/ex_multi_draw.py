"""
Example for QtMultiDraw.
"""

from qtdraw.qt_draw import QtMultiDraw


# ==================================================
def draw():
    p = QtMultiDraw(2, model=["draw0", "draw1"], axis_type=["abc", "xyz"])
    p[0].set_range([[0, 0, 0], [2, 2, 1]])
    p[1].set_range([[0, 0, 0], [2, 2, 1]])
    p[0].set_crystal("hexagonal")

    position = [0.1, 0.2, 0.3]
    p[0].plot_plane(position, [0, 1, 0], 0.4, 0.4)
    p[0].plot_box(position, a1="[0.1, 0, 0]", a2="[-0.3, 0.3, 0]", a3="[0, 0, 0.1]")

    p[1].plot_orbital(position, "1", size=0.2, color="white")
    p[1].plot_stream_vector(position, "1", "[x y, y z, z x]", size=0.2, v_size=0.15, component=0)
    p[1].plot_text3d(position, "vector on sphere", normal=[4, 5, 2], offset=[0.1, 0.5, 0.3])

    p.show()


# ==================================================
if __name__ == "__main__":
    draw()
