from qtdraw.core.color_dialog import QtColorDialog
from qtdraw.core.util import create_application

app = create_application()
w = QtColorDialog()
w.show()
app.exec()
