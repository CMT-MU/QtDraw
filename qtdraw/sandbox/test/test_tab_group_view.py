from qtdraw.sandbox.qt_event_util import get_qt_application
from qtdraw.sandbox.group_view import GroupModel
from qtdraw.sandbox.tab_group_view import TabGroupView
from test_group_view import site, model_list

# ================================================== main
if __name__ == "__main__":
    app = get_qt_application()

    widget = None

    models = {i: GroupModel(widget, name=i, column_info=site) for i in ["site1", "site2"]}
    for model in models.values():
        model.set_data(model_list)

    tab = TabGroupView(widget, models=models)
    tab.resize(1000, 400)

    tab.show()

    app.exec()
