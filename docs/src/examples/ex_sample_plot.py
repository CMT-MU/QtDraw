"""
Example for QtDraw.
"""

from qtdraw.qt_draw import QtDraw


# ==================================================
def sample1():
    p = QtDraw(model="test")

    p.plot_site([[0, 0, 0], [0, 0.5, 0], [0, 1, 0]], size=1, color="tan", opacity=1)
    p.plot_bond([0.5, 0.5, 0], vector=[0, 1, 0], width=1, color="silver", opacity=1)
    p.plot_vector([1, 0, 0], vector=[0, 1, 0], length=2, width=1, offset=0, color="green", opacity=1)
    p.plot_orbital([0.75, 0.75, 0], shape="x*y", surface="z", size=0.2, color="coolwarm", opacity=1, scale=True)
    p.show()


# ==================================================
def sample2():
    m4 = [
        ("Mu", "[-x, -y, 2z]"),
        ("Mv", "[x, -y, 0]"),
        ("Myz", "[0, z, y]"),
        ("Mzx", "[z, 0, x]"),
        ("Mxy", ["y", "x", "0"]),
    ]

    position = [0, 0, 0]
    for n, m in m4:
        p = QtDraw(model=n)
        p.plot_orbital(position, 1, size=1, color="white", opacity=0.9)
        p.plot_stream_vector(position, 1.2, m, size=1, v_size=0.3)
        p.set_view([1, -1, 1])
        p.show()


# ==================================================
if __name__ == "__main__":
    sample1()
    sample2()
