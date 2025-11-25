from qtdraw.core.qtdraw_info import __version__

__all__ = ["QtDraw", "PyVistaWidget", "create_qtdraw_file", "convert_qtdraw_v2", "convert_qtdraw_v2", "get_qt_application"]


def __getattr__(name):
    if name == "QtDraw":
        from qtdraw.core.qtdraw_app import QtDraw

        return QtDraw
    if name == "PyVistaWidget":
        from qtdraw.core.pyvista_widget import PyVistaWidget

        return PyVistaWidget
    if name == "create_qtdraw_file":
        from qtdraw.core.pyvista_widget import create_qtdraw_file

        return create_qtdraw_file

    if name == "convert_qtdraw_v2":
        from qtdraw.core.pyvista_widget import convert_qtdraw_v2

        return convert_qtdraw_v2

    if name == "get_qt_application":
        from qtdraw.widget.qt_event_util import get_qt_application

        return get_qt_application

    raise AttributeError
