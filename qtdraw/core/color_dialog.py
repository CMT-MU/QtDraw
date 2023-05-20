from qtpy.QtWidgets import QColorDialog
from qtdraw.core.color_palette import hex_colornames, _hex2rgb


# ==================================================
class QtColorDialog(QColorDialog):
    """
    color dialog.

    Attributes:
        hex (str): hex code of color
        name (str): color name
        rgb (tuple): RGB color
    """

    # ==================================================
    def __init__(self, parent=None):
        """
        initialize the class.
        """
        super().__init__(parent)
        self.finished["int"].connect(self._close)

    # ==================================================
    def _close(self):
        color = self.selectedColor()

        self.hex = color.name()
        self.rgb = _hex2rgb(self.hex)
        if self.hex in hex_colornames.keys():
            self.name = hex_colornames[self.hex]
        else:
            self.name = ""

        print(self.name, self.hex, self.rgb)
