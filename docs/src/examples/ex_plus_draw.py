"""
Example for QtDraw with additional panel.
"""

from qtdraw.qt_draw import QtDraw


# ==================================================
class PlusDraw(QtDraw):
    """
    extended draw with plus_panel.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._load_plus_panel("plus_panel.ui", __file__)

    def _set_plus_panel(self):
        self.plus_panel.label_1.setText("update label")


# ==================================================
def draw():
    p = PlusDraw()
    p.set_range([[0, 0, 0], [2, 2, 1]])

    position = [[0.1, 0.2, 0.3], [0.3, 0.2, 0.3]]
    caption = [str(i) for i in range(len(position))]
    p.plot_site(position)
    p.plot_bond(position, [0, 0.4, 0])
    p.plot_caption(position, caption, bold=True, color="snow")
    p.show()


# ==================================================
if __name__ == "__main__":
    draw()
