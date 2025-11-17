"""
Test for tab group view widget.

This module provides a test for TabGroupView.
"""

from qtdraw.core.pyvista_widget_setting import object_default

from qtdraw.widget.qt_event_util import get_qt_application
from qtdraw.widget.group_view import GroupModel
from qtdraw.widget.tab_group_view import TabGroupView

# ================================================== main
if __name__ == "__main__":
    app = get_qt_application()

    widget = None

    models = {name: GroupModel(widget, name=name, column_info=d) for name, d in object_default.items()}
    # for model in models.values():
    #    model.set_data(model_list)

    tab = TabGroupView(widget, models=models)
    tab.resize(1000, 400)

    tab.show()

    app.exec()
