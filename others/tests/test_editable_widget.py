from qtpy.QtWidgets import QWidget, QGridLayout
from qtdraw.core.editable_widget import (
    QtColorSelector,
    QtCheckBox,
    QtRadioGroup,
    QtComboBox,
    QtImage,
    QtColorLabel,
    QtText,
    QtMath,
)
from qtdraw.core.util import create_application


IMAGEFILE = __file__[: __file__.rfind("/")] + "/../test/fig.jpg"


app = create_application()


def show_label(text):
    print("label =", text)


obj = [
    QtColorLabel("strawberry"),
    QtColorLabel("coolwarm"),
    QtColorSelector("strawberry", color_type="color"),
    QtColorSelector("coolwarm", color_type="color_both"),
    QtMath(r"\int dx\,f(x),\quad \begin{pmatrix} a & b \\ c & d \end{pmatrix}", show_label),
    QtMath("1/3+4I", show_label, validator="s_scalar"),
    QtMath("[1,sin(y),cos(z)]", show_label, validator="s_column"),
    QtMath("[[1,2,3],[2x,y,z]]", show_label, validator="s_matrix"),
    QtText("1+4i", show_label),
    QtText("[0,3,-4]", show_label, validator="i_row"),
    QtText("[2,0,-4]", show_label, validator="i_column"),
    QtText("[[1,3,-4],[2,1,-4]]", show_label, validator="r_matrix"),
    QtImage(IMAGEFILE, width=100),
    QtCheckBox("check", True, lambda flag: print("status =", flag), show_label),
    QtRadioGroup(["a", "b", "c"], current=1, vertical=True),
    QtComboBox(["A", "B", "C"], current=2),
]

w = QWidget()
layout = QGridLayout()
for i, o in enumerate(obj):
    layout.addWidget(o, i // 4, i % 4)
w.setLayout(layout)

w.resize(800, 100)
w.show()
app.exec()
