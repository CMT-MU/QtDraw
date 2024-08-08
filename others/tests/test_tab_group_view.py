"""
Test for tab group view.

This module provides a test for tab group view.
"""

from qtdraw.widget.group_model import GroupModel
from qtdraw.widget.tab_group_view import TabGroupView
from qtdraw.core.pyvista_widget_setting import object_default

# ================================================== main
if __name__ == "__main__":
    app = ()

    _data = {}
    for object_type, value in object_default.items():
        _data[object_type] = GroupModel(object_type, value, parent=None)
        _data_view_group = TabGroupView(_data)
        _data_view_group.resize(800, 600)

    _data["site"].append_row()
    _data["site"].append_row()

    _data_view_group.show()
    _data_view_group.view["site"].expandAll()

    app.exec()
