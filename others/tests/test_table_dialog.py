from qtdraw.core.table_dialog import TableDialog
from qtdraw.core.util import create_application

header = ["col1", "col2", "colo3"]
vheader = ["a", "b", "c", "d"]
data = [[1, "\int dx\,f(x)", 1], [2, "2", 1], [3, "1", 2], [4, "3", 1]]
role = ["text", "math", "text"]
align = ["left", "right", "right"]


app = create_application()
table = TableDialog(data, title="QtDrawMP - Group Browser", header=header, vheader=vheader, role=role, align=align)
table.show()
app.exec()
