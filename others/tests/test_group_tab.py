from gcoreutils.dataset import DataSet
from qtdraw.core.group_tab import GroupTab
from qtdraw.core.util import create_application
from data import test_data1, test_data2

ds1 = DataSet(test_data1)
ds2 = DataSet(test_data2)

app = create_application()

ex1 = GroupTab(ds1, read_only=True)
ex1.show()

ex2 = GroupTab(ds2)
ex2.show()

app.exec()
