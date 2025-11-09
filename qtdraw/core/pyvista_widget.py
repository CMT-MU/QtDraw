"""
Core widget to draw 3d objects via PyVista.

This module provides a class to draw various
3d objects, and manage data, view, and so on.
"""

import os
from pathlib import Path
import ast
import subprocess
import numpy as np
import copy
from PySide6.QtWidgets import QMainWindow, QMenu, QSizePolicy
from PySide6.QtGui import QCursor, QMouseEvent
from PySide6.QtCore import QEvent, Qt, QCoreApplication, Signal, QSize, QObject, QModelIndex
import pyvista as pv
from pyvistaqt import QtInteractor
from gcoreutils.color_palette import all_colors, custom_colormap, check_color
from gcoreutils.convert_util import text_to_list, apply
from qtdraw.util.util_axis import (
    create_axes_widget,
    get_view_vector,
    create_unit_cell,
    create_grid,
    get_lattice_vector,
    get_repeat_range,
    get_outside_box,
)
from qtdraw.core.pyvista_widget_setting import (
    default_status,
    default_preference,
    object_default,
    COLUMN_NAME_CHECK,
    COLUMN_NAME_ACTOR,
    COLUMN_LABEL,
    COLUMN_LABEL_CHECK,
    COLUMN_LABEL_ACTOR,
    COLUMN_CELL,
    COLUMN_POSITION,
    COLUMN_ISOSURFACE_FILE,
)
from qtdraw.core.pyvista_widget_setting import widget_detail as detail
from qtdraw.core.pyvista_widget_setting import DIGIT
from qtdraw.widget.group_model import GroupModel
from qtdraw.widget.tab_group_view import TabGroupView
from qtdraw.util.basic_object import (
    create_sphere,
    create_bond,
    create_vector,
    create_orbital,
    create_stream,
    create_line,
    create_plane,
    create_circle,
    create_torus,
    create_ellipsoid,
    create_toroid,
    create_box,
    create_polygon,
    create_text3d,
    create_spline,
    create_spline_t,
    create_isosurface,
    create_orbital_data,
    create_stream_data,
)
from qtdraw.util.util import convert_to_str, read_dict, convert_str_vector, split_filename, cat_filename, get_data_range
from qtdraw.parser.read_material import read_draw
from qtdraw.parser.xsf import extract_data_xsf
from qtdraw.parser.converter import convert_version2
from qtdraw.util.logging_util import LogWidget
from qtdraw.util.qt_event_util import get_qt_application
from qtdraw.__init__ import __version__, __date__, __author__


# ==================================================
class Window(QMainWindow):
    # ==================================================
    def __init__(self, level):
        """
        Window with logging.

        Args:
            level (Level): log level.

        :meta private:
        """
        self.app = get_qt_application()
        self.logger = LogWidget(level=level)
        super().__init__()


# ==================================================
def create_qtdraw_file(filename, callback):
    """
    Create QtDraw file as background.

    Args:
        filename (str): full filename.
        callback (function): callback to draw objects, f(widget).
    """
    app = get_qt_application()
    widget = PyVistaWidget(off_screen=True)
    callback(widget)
    widget.save(filename)
    app.quit()


# ==================================================
def convert_qtdraw_v2(filename):
    """
    Convert qtdraw file to version 2.

    Args:
        filename (str): filename.
    """
    app = get_qt_application()
    widget = PyVistaWidget(off_screen=True)
    widget.load(filename)
    path_abs, path_rel, base, ext, folder = split_filename(filename)
    filename2 = cat_filename(base + "_v2", ext)
    widget.save(filename2)
    app.quit()


# ==================================================
class PlotSignal(QObject):
    """
    Plot signal.

    :meta private:
    """

    # signal for plotting an object.
    plot = Signal(QModelIndex, dict, np.ndarray)  # index, data, pointT.

    def __init__(self, instance, f):
        """
        For dict type of signal.

        Args:
            instance (Any): PyVistaWidget instance.
            f (function): function object.
        """
        super().__init__()
        self.plot.connect(lambda index, data, positionT: f(instance, index, data, positionT))


# ==================================================
class PyVistaWidget(QtInteractor):
    # signal for write info.
    message = Signal(str)  # messsage.

    # ==================================================
    def __init__(self, parent=None, off_screen=False):
        """
        Widget for 3d plot layer using PyVista.

        Args:
            parent (QWidget, optional): parent.
            off_screen (bool, optional): off screen ?
        """
        os.environ["PYVISTA_QT_BACKEND"] = "PySide6"
        # avoid recursion of the close() until the PyVistaWidget.__init__() is called, see pyvistaqt/plotting.py.
        self._closed = True

        # set default.
        self._off_screen = off_screen
        self.clear_info()

        # set interactor.
        super().__init__(
            parent=parent,
            off_screen=self._off_screen,
            multi_samples=detail["multi_samples"],
            line_smoothing=detail["line_smoothing"],
            point_smoothing=detail["point_smoothing"],
            polygon_smoothing=detail["polygon_smoothing"],
            auto_update=detail["auto_update"],
        )
        assert not self._closed

        # set data model.
        self.init_data_model()

        # self.set_theme()
        if detail["anti_aliasing"]:
            self.enable_anti_aliasing()
        else:
            self.disable_anti_aliasing()

        # set minimum window size.
        self.setMinimumSize(QSize(*detail["minimum_window_size"]))
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # set picking actor.
        if not self._off_screen:
            self.enable_mesh_picking(
                self.show_context_menu,
                use_actor=True,
                show=False,
                show_message=False,
            )

        # create data view group.
        self._tab_group_view = TabGroupView(self._data, parent=self)
        self._tab_group_view.resize(800, 600)

        # add "e" key to open data view group.
        if not self._off_screen:
            self.add_key_event(detail["data_edit_key"], self.open_tab_group_view)

        # connection.
        for object_type, model in self._data.items():
            model.dataModified.connect(self.plot_data)
            model.dataRemoved.connect(self.remove_data)
            model.checkChanged.connect(self.change_check_state)
            self._tab_group_view.view[object_type].selectionChanged.connect(self.change_selection)

        # create signal and connection for objects (row, data).
        self._plot_signal = {}
        for object_type in object_default.keys():
            f = getattr(PyVistaWidget, "plot_data_" + object_type)
            self._plot_signal[object_type] = PlotSignal(self, f)

        # refresh.
        self.refresh()
        self.set_view()

    # ==================================================
    def paintEvent(self, event):
        # override the function to do nothing for PySide 6.10 or later.
        pass

    # ==================================================
    def clear_info(self):
        """
        Clear info.

        :meta private:
        """
        self.set_theme()
        self._status = copy.deepcopy(default_status)
        self._status["multipie"] = {"plus": {}}  # for multipie.
        self._status["plus"] = {}  #  for temporaly working purpose.
        self.set_additional_status()
        self._preference = copy.deepcopy(default_preference)
        self._label_counter = 0  # id for label actor.
        self._isosurface_data = {}
        self._backup = None
        self._block_remove_isosurface = False

    # ==================================================
    def set_additional_status(self):
        """
        Set additional status.

        :meta private:
        """
        cell, A = get_lattice_vector(self._status["crystal"], self._status["cell"])
        i1, dims = get_repeat_range(self._status["lower"], self._status["upper"])
        self._status["cell"] = cell  # update.
        self._status["plus"]["A"] = A  # addition.
        self._status["plus"]["ilower"] = i1  # addition.
        self._status["plus"]["dims"] = dims  # addition.

    # ==================================================
    # add_object_type
    # ==================================================
    def add_site(self, size=None, color=None, opacity=None, position=None, cell=None, name=None, label=None, margin=None):
        """
        Add site.

        Args:
            size (float, optional): site size. (default: 0.1)
            color (str, optional): site color. (default: darkseagreen)
            opacity (float, optional): opacity, [0,1]. (default: 1.0)
            position (str, optional): position in cell, [x,y,z]. (default: [0,0,0])
            cell (str, optional): cell, [nx,ny,nz]. (default: [0,0,0])
            name (str, optional): name of group. (default: untitled)
            label (str, optional): label. (default: label)
            margin (int, optional): label margin. (default: 3)

        Note:
            - if keyword is None, default value is used.
        """
        row_data = self.set_common_row_data("site", opacity, position, cell, name, label, margin)

        if size is not None:
            row_data["size"] = convert_to_str(size)
        if color is not None:
            row_data["color"] = convert_to_str(color)

        row_data = list(row_data.values())
        self._data["site"].append_row(row_data)

    # ==================================================
    def add_bond(
        self,
        direction=None,
        width=None,
        color=None,
        color2=None,
        cartesian=None,
        opacity=None,
        position=None,
        cell=None,
        name=None,
        label=None,
        margin=None,
    ):
        """
        Add bond.

        Args:
            direction (str, optional): bond direction. (default: [0,0,1])
            width (float, optional): bond width. (default: 0.02)
            color (str, optional): bond color (tail side). (default: silver)
            color2 (str, optional): bond color (head side). (default: silver)
            cartesian (bool, optional): cartesian coordinate for direction ? (default: False)
            opacity (float, optional): opacity, [0,1]. (default: 1.0)
            position (str, optional): position in cell, [x,y,z]. (default: [0,0,0])
            cell (str, optional): cell, [nx,ny,nz]. (default: [0,0,0])
            name (str, optional): name of group. (default: untitled)
            label (str, optional): label. (default: label)
            margin (int, optional): label margin. (default: 3)

        Note:
            - if keyword is None, default value is used.
            - bond position is at center.
        """
        row_data = self.set_common_row_data("bond", opacity, position, cell, name, label, margin)

        if direction is not None:
            if isinstance(direction, np.ndarray):
                direction = direction.tolist()
            row_data["direction"] = convert_to_str(direction)
        if width is not None:
            row_data["width"] = convert_to_str(width)
        if color is not None:
            row_data["color"] = convert_to_str(color)
        if color2 is not None:
            row_data["color2"] = convert_to_str(color2)
        if cartesian is not None:
            row_data["cartesian_check"] = cartesian

        row_data = list(row_data.values())
        self._data["bond"].append_row(row_data)

    # ==================================================
    def add_vector(
        self,
        direction=None,
        length=None,
        width=None,
        offset=None,
        color=None,
        cartesian=None,
        shaft_R=None,
        tip_R=None,
        tip_length=None,
        opacity=None,
        position=None,
        cell=None,
        name=None,
        label=None,
        margin=None,
    ):
        """
        Add vector.

        Args:
            direction (str, optional): vector direction. (default: [0,0,1])
            length (float, optional): vector length. (default: 1.0)
            width (float, optional): vector width. (default: 0.02)
            offset (float, optional): vector offset. (default: -0.43)
            color (str, optional): vector color. (default: orange)
            cartesian (bool, optional): cartesian coordinate for direction ? (default: True)
            shaft_R (float, optional): shaft radius. (default: 1.0)
            tip_R (float, optional): tip radius. (default: 2.0)
            tip_length (float, optional): tip length. (default: 0.25)
            opacity (float, optional): opacity, [0,1]. (default: 1.0)
            position (str, optional): position in cell, [x,y,z]. (default: [0,0,0])
            cell (str, optional): cell, [nx,ny,nz]. (default: [0,0,0])
            name (str, optional): name of group. (default: untitled)
            label (str, optional): label. (default: label)
            margin (int, optional): label margin. (default: 3)

        Note:
            - if keyword is None, default value is used.
            - if length is negative, norm of direction multiplied by |length| is used.
        """
        row_data = self.set_common_row_data("vector", opacity, position, cell, name, label, margin)

        if direction is not None:
            if isinstance(direction, np.ndarray):
                direction = direction.tolist()
            row_data["direction"] = convert_to_str(direction)
        if length is not None:
            row_data["length"] = convert_to_str(length)
        if width is not None:
            row_data["width"] = convert_to_str(width)
        if offset is not None:
            row_data["offset"] = convert_to_str(offset)
        if color is not None:
            row_data["color"] = convert_to_str(color)
        if cartesian is not None:
            row_data["cartesian_check"] = cartesian
        if shaft_R is not None:
            row_data["shaft R"] = convert_to_str(shaft_R)
        if tip_R is not None:
            row_data["tip R"] = convert_to_str(tip_R)
        if tip_length is not None:
            row_data["tip length"] = convert_to_str(tip_length)

        row_data = list(row_data.values())
        self._data["vector"].append_row(row_data)

    # ==================================================
    def add_orbital(
        self,
        shape=None,
        surface=None,
        size=None,
        range=None,
        color=None,
        opacity=None,
        position=None,
        cell=None,
        name=None,
        label=None,
        margin=None,
    ):
        """
        Add orbital.

        Args:
            shape (str, optional): orbital shape polynomial in terms of (x,y,z,r). (default: 3z**2-r**2)
            surface (str, optional): orbital colormap polynomial in terms of (x,y,z,r). (default: "")
            size (float, optional): orbital size. (default: 0.5)
            range (list, optional): plot range of [th,phi]. (default: [[0,180],[0,360]])
            color (str, optional): orbital color or colormap. (default: Wistia)
            opacity (float, optional): opacity, [0,1]. (default: 1.0)
            position (str, optional): position in cell, [x,y,z]. (default: [0,0,0])
            cell (str, optional): cell, [nx,ny,nz]. (default: [0,0,0])
            name (str, optional): name of group. (default: untitled)
            label (str, optional): label. (default: label)
            margin (int, optional): label margin. (default: 3)

        Note:
            - if keyword is None, default value is used.
            - if surface is "", the same one of shape is used.
            - if size is positive, max. value is equivalent to size.
            - if size is negative, abs. value is scaled by size.
        """
        row_data = self.set_common_row_data("orbital", opacity, position, cell, name, label, margin)

        if shape is not None:
            row_data["shape"] = shape
        if surface is not None:
            row_data["surface"] = surface
        if size is not None:
            row_data["size"] = convert_to_str(size)
        if range is not None:
            if isinstance(range, np.ndarray):
                range = range.tolist()
            row_data["range"] = convert_to_str(range)
        if color is not None:
            row_data["color"] = convert_to_str(color)

        row_data = list(row_data.values())
        self._data["orbital"].append_row(row_data)

    # ==================================================
    def add_stream(
        self,
        shape=None,
        vector=None,
        size=None,
        range=None,
        division=None,
        length=None,
        width=None,
        offset=None,
        abs_scale=None,
        color=None,
        component=None,
        shaft_R=None,
        tip_R=None,
        tip_length=None,
        opacity=None,
        position=None,
        cell=None,
        name=None,
        label=None,
        margin=None,
    ):
        """
        Add stream.

        Args:
            shape (str, optional): shape polynomial on which stream put. (default: 1)
            vector (str, optional): stream polynomials for [x,y,z] components. (default: [x,y,z])
            size (float, optional): shape size. (default: 0.5)
            range (list, optional): plot range of [th,phi]. (default: [[0,180],[0,360]])
            division (list, optional): division of stream of [th,phi]. (default: [9,18])
            length (float, optional): stream arrow size. (default: 0.1)
            width (float, optional): stream arrow width. (default: 0.01)
            offset (float, optional): stream arrow offset. (default: -0.43)
            abs_scale (bool, optional): stream arrow scaled ? (default: False)
            color (str, optional): stream arrow color or colormap. (default: coolwarm)
            component (str, optional): use component or abs, "x/y/z/abs". (default: abs)
            shaft_R (float, optional): shaft radius. (default: 1.0)
            tip_R (float, optional): tip radius. (default: 2.0)
            tip_length (float, optional): tip length. (default: 0.25)
            opacity (float, optional): opacity, [0,1]. (default: 1.0)
            position (str, optional): position in cell, [x,y,z]. (default: [0,0,0])
            cell (str, optional): cell, [nx,ny,nz]. (default: [0,0,0])
            name (str, optional): name of group. (default: untitled)
            label (str, optional): label. (default: label)
            margin (int, optional): label margin. (default: 3)

        Note:
            - if keyword is None, default value is used.
            - if size is negative, shape is normalized.
        """
        row_data = self.set_common_row_data("stream", opacity, position, cell, name, label, margin)

        if shape is not None:
            row_data["shape"] = shape
        if vector is not None:
            row_data["vector"] = vector
        if size is not None:
            row_data["size"] = convert_to_str(size)
        if range is not None:
            if isinstance(range, np.ndarray):
                range = range.tolist()
            row_data["range"] = convert_to_str(range)
        if division is not None:
            if isinstance(division, np.ndarray):
                division = division.tolist()
            row_data["division"] = convert_to_str(division)
        if length is not None:
            row_data["length"] = convert_to_str(length)
        if width is not None:
            row_data["width"] = convert_to_str(width)
        if offset is not None:
            row_data["offset"] = convert_to_str(offset)
        if abs_scale is not None:
            row_data["abs_scale_check"] = abs_scale
        if color is not None:
            row_data["color"] = convert_to_str(color)
        if component is not None:
            row_data["component"] = convert_to_str(component)
        if shaft_R is not None:
            row_data["shaft R"] = convert_to_str(shaft_R)
        if tip_R is not None:
            row_data["tip R"] = convert_to_str(tip_R)
        if tip_length is not None:
            row_data["tip length"] = convert_to_str(tip_length)

        row_data = list(row_data.values())
        self._data["stream"].append_row(row_data)

    # ==================================================
    def add_line(
        self,
        direction=None,
        width=None,
        arrow1=None,
        arrow2=None,
        tip_R=None,
        tip_length=None,
        color=None,
        cartesian=None,
        opacity=None,
        position=None,
        cell=None,
        name=None,
        label=None,
        margin=None,
    ):
        """
        Add line.

        Args:
            direction (str, optional): line direction. (default: [0,0,1])
            width (float, optional): line width. (default: 0.02)
            arrow1 (bool, optional): arrow (tail side) ? (default: False)
            arrow2 (bool, optional): arrow (head side) ? (default: False)
            tip_R (float, optional): arrow tip radius. (default: 2.0)
            tip_length (float, optional): arrow tip length. (default: 0.1)
            color (str, optional): line color. (default: strawberry)
            cartesian (bool, optional): cartesian coordinate for direction ? (default: False)
            opacity (float, optional): opacity, [0,1]. (default: 1.0)
            position (str, optional): position in cell, [x,y,z]. (default: [0,0,0])
            cell (str, optional): cell, [nx,ny,nz]. (default: [0,0,0])
            name (str, optional): name of group. (default: untitled)
            label (str, optional): label. (default: label)
            margin (int, optional): label margin. (default: 3)

        Note:
            - if keyword is None, default value is used.
        """
        row_data = self.set_common_row_data("line", opacity, position, cell, name, label, margin)

        if direction is not None:
            if isinstance(direction, np.ndarray):
                direction = direction.tolist()
            row_data["direction"] = convert_to_str(direction)
        if arrow1 is not None:
            row_data["arrow1_check"] = arrow1
        if arrow2 is not None:
            row_data["arrow2_check"] = arrow2
        if tip_R is not None:
            row_data["tip R"] = convert_to_str(tip_R)
        if tip_length is not None:
            row_data["tip length"] = convert_to_str(tip_length)
        if color is not None:
            row_data["color"] = convert_to_str(color)
        if cartesian is not None:
            row_data["cartesian_check"] = cartesian

        row_data = list(row_data.values())
        self._data["line"].append_row(row_data)

    # ==================================================
    def add_plane(
        self,
        normal=None,
        x_size=None,
        y_size=None,
        color=None,
        width=None,
        grid=None,
        grid_color=None,
        cartesian=None,
        opacity=None,
        position=None,
        cell=None,
        name=None,
        label=None,
        margin=None,
    ):
        """
        Add plane.

        Args:
            normal (str, optional): plane normal vector. (default: [0,0,1])
            x_size (float, optional): plane x size. (default: 1.0)
            y_size (float, optional): plane y size. (default: 1.0)
            color (str, optional): plane color. (default: sky)
            width (float, optional): plane grid width. (default: 2.0)
            grid (bool, optional): grid ? (default: False)
            grid_color (str, optional): grid color. (default: black)
            cartesian (bool, optional): cartesian coordinate for normal ? (default: True)
            opacity (float, optional): opacity, [0,1]. (default: 1.0)
            position (str, optional): position in cell, [x,y,z]. (default: [0,0,0])
            cell (str, optional): cell, [nx,ny,nz]. (default: [0,0,0])
            name (str, optional): name of group. (default: untitled)
            label (str, optional): label. (default: label)
            margin (int, optional): label margin. (default: 3)

        Note:
            - if keyword is None, default value is used.
        """
        row_data = self.set_common_row_data("plane", opacity, position, cell, name, label, margin)

        if normal is not None:
            if isinstance(normal, np.ndarray):
                normal = normal.tolist()
            row_data["normal"] = convert_to_str(normal)
        if x_size is not None:
            row_data["x_size"] = convert_to_str(x_size)
        if y_size is not None:
            row_data["y_size"] = convert_to_str(y_size)
        if color is not None:
            row_data["color"] = convert_to_str(color)
        if width is not None:
            row_data["width"] = convert_to_str(width)
        if grid is not None:
            row_data["grid_check"] = grid
        if grid_color is not None:
            row_data["grid_color"] = convert_to_str(grid_color)
        if cartesian is not None:
            row_data["cartesian_check"] = cartesian

        row_data = list(row_data.values())
        self._data["plane"].append_row(row_data)

    # ==================================================
    def add_circle(
        self,
        normal=None,
        size=None,
        color=None,
        width=None,
        edge=None,
        edge_color=None,
        cartesian=None,
        opacity=None,
        position=None,
        cell=None,
        name=None,
        label=None,
        margin=None,
    ):
        """
        Add circle.

        Args:
            normal (str, optional): circle normal vector. (default: [0,0,1])
            size (float, optional): circle size. (default: 0.5)
            color (str, optional): circle color. (default: salmon)
            width (float, optional): edge width. (default: 2.0)
            edge (bool, optional): edge ? (default: True)
            edge_color (str, optional): edge color. (default: black)
            cartesian (bool, optional): cartesian coordinate for normal ? (default: True)
            opacity (float, optional): opacity, [0,1]. (default: 1.0)
            position (str, optional): position in cell, [x,y,z]. (default: [0,0,0])
            cell (str, optional): cell, [nx,ny,nz]. (default: [0,0,0])
            name (str, optional): name of group. (default: untitled)
            label (str, optional): label. (default: label)
            margin (int, optional): label margin. (default: 3)

        Note:
            - if keyword is None, default value is used.
        """
        row_data = self.set_common_row_data("circle", opacity, position, cell, name, label, margin)

        if normal is not None:
            if isinstance(normal, np.ndarray):
                normal = normal.tolist()
            row_data["normal"] = convert_to_str(normal)
        if size is not None:
            row_data["size"] = convert_to_str(size)
        if color is not None:
            row_data["color"] = convert_to_str(color)
        if width is not None:
            row_data["width"] = convert_to_str(width)
        if edge is not None:
            row_data["edge_check"] = edge
        if edge_color is not None:
            row_data["edge_color"] = convert_to_str(edge_color)
        if cartesian is not None:
            row_data["cartesian_check"] = cartesian

        row_data = list(row_data.values())
        self._data["circle"].append_row(row_data)

    # ==================================================
    def add_torus(
        self,
        normal=None,
        size=None,
        width=None,
        color=None,
        cartesian=None,
        opacity=None,
        position=None,
        cell=None,
        name=None,
        label=None,
        margin=None,
    ):
        """
        Add torus.

        Args:
            normal (str, optional): torus normal vector. (default: [0,0,1])
            size (float, optional): torus size. (default: 0.5)
            width (float, optional): torus width. (default: 0.15)
            color (str, optional): torus color. (default: cantaloupe)
            cartesian (bool, optional): cartesian coordinate for normal ? (default: True)
            opacity (float, optional): opacity, [0,1]. (default: 1.0)
            position (str, optional): position in cell, [x,y,z]. (default: [0,0,0])
            cell (str, optional): cell, [nx,ny,nz]. (default: [0,0,0])
            name (str, optional): name of group. (default: untitled)
            label (str, optional): label. (default: label)
            margin (int, optional): label margin. (default: 3)

        Note:
            - if keyword is None, default value is used.
        """
        row_data = self.set_common_row_data("torus", opacity, position, cell, name, label, margin)

        if normal is not None:
            if isinstance(normal, np.ndarray):
                normal = normal.tolist()
            row_data["normal"] = convert_to_str(normal)
        if size is not None:
            row_data["size"] = convert_to_str(size)
        if width is not None:
            row_data["width"] = convert_to_str(width)
        if color is not None:
            row_data["color"] = convert_to_str(color)
        if cartesian is not None:
            row_data["cartesian_check"] = cartesian

        row_data = list(row_data.values())
        self._data["torus"].append_row(row_data)

    # ==================================================
    def add_ellipsoid(
        self,
        normal=None,
        x_size=None,
        y_size=None,
        z_size=None,
        color=None,
        cartesian=None,
        opacity=None,
        position=None,
        cell=None,
        name=None,
        label=None,
        margin=None,
    ):
        """
        Add ellipsoid.

        Args:
            normal (str, optional): ellipsoid normal vector. (default: [0,0,1])
            x_size (float, optional): ellipsoid x size. (default: 0.5)
            y_size (float, optional): ellipsoid y size. (default: 0.4)
            z_size (float, optional): ellipsoid z size. (default: 0.3)
            color (str, optional): ellipsoid color. (default: cornflowerblue)
            cartesian (bool, optional): cartesian coordinate for normal ? (default: True)
            opacity (float, optional): opacity, [0,1]. (default: 1.0)
            position (str, optional): position in cell, [x,y,z]. (default: [0,0,0])
            cell (str, optional): cell, [nx,ny,nz]. (default: [0,0,0])
            name (str, optional): name of group. (default: untitled)
            label (str, optional): label. (default: label)
            margin (int, optional): label margin. (default: 3)

        Note:
            - if keyword is None, default value is used.
        """
        row_data = self.set_common_row_data("ellipsoid", opacity, position, cell, name, label, margin)

        if normal is not None:
            if isinstance(normal, np.ndarray):
                normal = normal.tolist()
            row_data["normal"] = convert_to_str(normal)
        if x_size is not None:
            row_data["x_size"] = convert_to_str(x_size)
        if y_size is not None:
            row_data["y_size"] = convert_to_str(y_size)
        if z_size is not None:
            row_data["z_size"] = convert_to_str(z_size)
        if color is not None:
            row_data["color"] = convert_to_str(color)
        if cartesian is not None:
            row_data["cartesian_check"] = cartesian

        row_data = list(row_data.values())
        self._data["ellipsoid"].append_row(row_data)

    # ==================================================
    def add_toroid(
        self,
        normal=None,
        size=None,
        width=None,
        x_scale=None,
        y_scale=None,
        z_scale=None,
        ring_shape=None,
        tube_shape=None,
        color=None,
        cartesian=None,
        opacity=None,
        position=None,
        cell=None,
        name=None,
        label=None,
        margin=None,
    ):
        """
        Add toroid.

        Args:
            normal (str, optional): toroid normal vector. (default: [0,0,1])
            size (float, optional): toroid size. (default: 0.5)
            width (float, optional): toroid width. (default: 0.15)
            x_scale (float, optional): toroid x scale. (default: 1.0)
            y_scale (float, optional): toroid y scale. (default: 1.0)
            z_scale (float, optional): toroid z scale. (default: 1.0)
            ring_shape (float, optional): toroid ring shape. (default: 0.3)
            tube_shape (float, optional): toroid tube shape. (default: 0.3)
            color (str, optional): toroid color. (default: tan)
            cartesian (bool, optional): cartesian coordinate for normal ? (default: True)
            opacity (float, optional): opacity, [0,1]. (default: 1.0)
            position (str, optional): position in cell, [x,y,z]. (default: [0,0,0])
            cell (str, optional): cell, [nx,ny,nz]. (default: [0,0,0])
            name (str, optional): name of group. (default: untitled)
            label (str, optional): label. (default: label)
            margin (int, optional): label margin. (default: 3)

        Note:
            - if keyword is None, default value is used.
        """
        row_data = self.set_common_row_data("toroid", opacity, position, cell, name, label, margin)

        if normal is not None:
            if isinstance(normal, np.ndarray):
                normal = normal.tolist()
            row_data["normal"] = convert_to_str(normal)
        if size is not None:
            row_data["size"] = convert_to_str(size)
        if width is not None:
            row_data["width"] = convert_to_str(width)
        if x_scale is not None:
            row_data["x_scale"] = convert_to_str(x_scale)
        if y_scale is not None:
            row_data["y_scale"] = convert_to_str(y_scale)
        if z_scale is not None:
            row_data["z_scale"] = convert_to_str(z_scale)
        if ring_shape is not None:
            row_data["ring_shape"] = convert_to_str(ring_shape)
        if tube_shape is not None:
            row_data["tube_shape"] = convert_to_str(tube_shape)
        if color is not None:
            row_data["color"] = convert_to_str(color)
        if cartesian is not None:
            row_data["cartesian_check"] = cartesian

        row_data = list(row_data.values())
        self._data["toroid"].append_row(row_data)

    # ==================================================
    def add_box(
        self,
        a1=None,
        a2=None,
        a3=None,
        width=None,
        edge=None,
        edge_color=None,
        wireframe=None,
        color=None,
        cartesian=None,
        opacity=None,
        position=None,
        cell=None,
        name=None,
        label=None,
        margin=None,
    ):
        """
        Add box.

        Args:
            a1 (str, optional): box a1 vector. (default: [1,0,0])
            a2 (str, optional): box a2 vector. (default: [0,1,0])
            a3 (str, optional): box a3 vector. (default: [0,0,1])
            width (float, optional): edge width. (default: 2.0)
            edge (bool, optional): edge ? (default: True)
            edge_color (str, optional): edge color. (default: black)
            wireframe (bool, optional): wireframe ? (default: False)
            color (str, optional): box color. (default: yellowgreen)
            cartesian (bool, optional): cartesian coordinate for shape ? (default: False)
            opacity (float, optional): opacity, [0,1]. (default: 1.0)
            position (str, optional): position in cell, [x,y,z]. (default: [0,0,0])
            cell (str, optional): cell, [nx,ny,nz]. (default: [0,0,0])
            name (str, optional): name of group. (default: untitled)
            label (str, optional): label. (default: label)
            margin (int, optional): label margin. (default: 3)

        Note:
            - if keyword is None, default value is used.
        """
        row_data = self.set_common_row_data("box", opacity, position, cell, name, label, margin)

        if a1 is not None:
            if isinstance(a1, np.ndarray):
                a1 = a1.tolist()
            row_data["a1"] = convert_to_str(a1)
        if a2 is not None:
            if isinstance(a2, np.ndarray):
                a2 = a2.tolist()
            row_data["a2"] = convert_to_str(a2)
        if a3 is not None:
            if isinstance(a3, np.ndarray):
                a3 = a3.tolist()
            row_data["a3"] = convert_to_str(a3)
        if width is not None:
            row_data["width"] = convert_to_str(width)
        if edge is not None:
            row_data["edge_check"] = edge
        if edge_color is not None:
            row_data["edge_color"] = convert_to_str(edge_color)
        if wireframe is not None:
            row_data["wireframe_check"] = wireframe
        if color is not None:
            row_data["color"] = convert_to_str(color)
        if cartesian is not None:
            row_data["cartesian_check"] = cartesian

        row_data = list(row_data.values())
        self._data["box"].append_row(row_data)

    # ==================================================
    def add_polygon(
        self,
        point=None,
        connectivity=None,
        width=None,
        edge=None,
        edge_color=None,
        wireframe=None,
        color=None,
        cartesian=None,
        opacity=None,
        position=None,
        cell=None,
        name=None,
        label=None,
        margin=None,
    ):
        """
        Add polygon.

        Args:
            point (str, optional): polygon vertex points. (default: [[0,0,0],[0.8,0,0],[0,0.6,0],[0,0,0.4],[0.6,0.6,0]])
            connectivity (str, optional): connectivity. (default: [[0,1,4,2],[0,1,3],[1,4,3],[2,0,3],[2,3,4]])
            width (float, optional): edge width. (default: 2.0)
            edge (bool, optional): edge ? (default: True)
            edge_color (str, optional): edge color. (default: black)
            wireframe (bool, optional): wireframe ? (default: False)
            color (str, optional): polygon color. (default: aluminum)
            cartesian (bool, optional): cartesian coordinate for shape ? (default: False)
            opacity (float, optional): opacity, [0,1]. (default: 1.0)
            position (str, optional): position in cell, [x,y,z]. (default: [0,0,0])
            cell (str, optional): cell, [nx,ny,nz]. (default: [0,0,0])
            name (str, optional): name of group. (default: untitled)
            label (str, optional): label. (default: label)
            margin (int, optional): label margin. (default: 3)

        Note:
            - if keyword is None, default value is used.
        """
        row_data = self.set_common_row_data("polygon", opacity, position, cell, name, label, margin)

        if point is not None:
            if isinstance(point, np.ndarray):
                point = point.tolist()
            row_data["point"] = convert_to_str(point)
        if connectivity is not None:
            if isinstance(connectivity, np.ndarray):
                connectivity = connectivity.tolist()
            row_data["connectivity"] = convert_to_str(connectivity)
        if width is not None:
            row_data["width"] = convert_to_str(width)
        if edge is not None:
            row_data["edge_check"] = edge
        if edge_color is not None:
            row_data["edge_color"] = convert_to_str(edge_color)
        if wireframe is not None:
            row_data["wireframe_check"] = wireframe
        if color is not None:
            row_data["color"] = convert_to_str(color)
        if cartesian is not None:
            row_data["cartesian_check"] = cartesian

        row_data = list(row_data.values())
        self._data["polygon"].append_row(row_data)

    # ==================================================
    def add_spline(
        self,
        point=None,
        width=None,
        n_interp=None,
        closed=None,
        natural=None,
        arrow1=None,
        arrow2=None,
        tip_R=None,
        tip_length=None,
        color=None,
        cartesian=None,
        opacity=None,
        position=None,
        cell=None,
        name=None,
        label=None,
        margin=None,
    ):
        """
        Add spline.

        Args:
            point (str, optional): spline vertex points. (default: [[0,0,0],[1,0,1],[0,1,2]])
            width (float, optional): spline width. (default: 0.01)
            n_interp (int, optional): spline interpolation points. (default: 500)
            closed (bool, optional): closed curve ? (default: False)
            natural (bool, optional): natural edge ? (default: True)
            arrow1 (bool, optional): arrow (tail side) ? (default: False)
            arrow2 (bool, optional): arrow (head side) ? (default: False)
            tip_R (float, optional): arrow tip radius. (default: 2.0)
            tip_length (float, optional): arrow tip length. (default: 0.1)
            color (str, optional): spline color. (default: banana)
            cartesian (bool, optional): cartesian coordinate for point ? (default: True)
            opacity (float, optional): opacity, [0,1]. (default: 1.0)
            position (str, optional): position in cell, [x,y,z]. (default: [0,0,0])
            cell (str, optional): cell, [nx,ny,nz]. (default: [0,0,0])
            name (str, optional): name of group. (default: untitled)
            label (str, optional): label. (default: label)
            margin (int, optional): label margin. (default: 3)

        Note:
            - if keyword is None, default value is used.
        """
        row_data = self.set_common_row_data("spline", opacity, position, cell, name, label, margin)

        if point is not None:
            if isinstance(point, np.ndarray):
                point = point.tolist()
            row_data["point"] = convert_to_str(point)
        if width is not None:
            row_data["width"] = convert_to_str(width)
        if n_interp is not None:
            row_data["n_interp"] = convert_to_str(n_interp)
        if closed is not None:
            row_data["closed_check"] = closed
        if natural is not None:
            row_data["natural_check"] = natural
        if arrow1 is not None:
            row_data["arrow1_check"] = arrow1
        if arrow2 is not None:
            row_data["arrow2_check"] = arrow2
        if tip_R is not None:
            row_data["tip R"] = convert_to_str(tip_R)
        if tip_length is not None:
            row_data["tip length"] = convert_to_str(tip_length)
        if color is not None:
            row_data["color"] = convert_to_str(color)
        if cartesian is not None:
            row_data["cartesian_check"] = cartesian

        row_data = list(row_data.values())
        self._data["spline"].append_row(row_data)

    # ==================================================
    def add_spline_t(
        self,
        point=None,
        t_range=None,
        width=None,
        n_interp=None,
        closed=None,
        natural=None,
        arrow1=None,
        arrow2=None,
        tip_R=None,
        tip_length=None,
        color=None,
        cartesian=None,
        opacity=None,
        position=None,
        cell=None,
        name=None,
        label=None,
        margin=None,
    ):
        """
        Add spline (parametric).

        Args:
            point (str, optional): spline function vector in terms of t. (default: [cos(2 pi t), sin(2 pi t), t/2])
            t_range (str, optional): spline t range [t0,t1,dt]. (default: [0,1,0.05])
            width (float, optional): spline width. (default: 0.01)
            n_interp (int, optional): spline interpolation points. (default: 500)
            closed (bool, optional): closed curve ? (default: False)
            natural (bool, optional): natural edge ? (default: True)
            arrow1 (bool, optional): arrow (tail side) ? (default: False)
            arrow2 (bool, optional): arrow (head side) ? (default: False)
            tip_R (float, optional): arrow tip radius. (default: 2.0)
            tip_length (float, optional): arrow tip length. (default: 0.1)
            color (str, optional): splline color. (default: crimson)
            cartesian (bool, optional): cartesian coordinate for point ? (default: True)
            opacity (float, optional): opacity, [0,1]. (default: 1.0)
            position (str, optional): position in cell, [x,y,z]. (default: [0,0,0])
            cell (str, optional): cell, [nx,ny,nz]. (default: [0,0,0])
            name (str, optional): name of group. (default: untitled)
            label (str, optional): label. (default: label)
            margin (int, optional): label margin. (default: 3)

        Note:
            - if keyword is None, default value is used.
        """
        row_data = self.set_common_row_data("spline_t", opacity, position, cell, name, label, margin)

        if point is not None:
            row_data["point"] = point
        if t_range is not None:
            if isinstance(t_range, np.ndarray):
                t_range = t_range.tolist()
            row_data["t_range"] = convert_to_str(t_range)
        if width is not None:
            row_data["width"] = convert_to_str(width)
        if n_interp is not None:
            row_data["n_interp"] = convert_to_str(n_interp)
        if closed is not None:
            row_data["closed_check"] = closed
        if natural is not None:
            row_data["natural_check"] = natural
        if arrow1 is not None:
            row_data["arrow1_check"] = arrow1
        if arrow2 is not None:
            row_data["arrow2_check"] = arrow2
        if tip_R is not None:
            row_data["tip R"] = convert_to_str(tip_R)
        if tip_length is not None:
            row_data["tip length"] = convert_to_str(tip_length)
        if color is not None:
            row_data["color"] = convert_to_str(color)
        if cartesian is not None:
            row_data["cartesian_check"] = cartesian

        row_data = list(row_data.values())
        self._data["spline_t"].append_row(row_data)

    # ==================================================
    def add_text3d(
        self,
        text=None,
        size=None,
        view=None,
        depth=None,
        offset=None,
        color=None,
        opacity=None,
        position=None,
        cell=None,
        name=None,
        label=None,
        margin=None,
    ):
        """
        Add text 3d.

        Args:
            text (str, optional): text. (default: text)
            size (float, optional): text size. (default: 0.3)
            view (str, optional): text viewpoint. (default: [0,0,1])
            depth (float, optional): text depth. (default: 0.2)
            offset (str, optional): text offset. (default: [0,0,0])
            color (str, optional): text color. (default: iron)
            opacity (float, optional): opacity, [0,1]. (default: 1.0)
            position (str, optional): position in cell, [x,y,z]. (default: [0,0,0])
            cell (str, optional): cell, [nx,ny,nz]. (default: [0,0,0])
            name (str, optional): name of group. (default: untitled)
            label (str, optional): label. (default: label)
            margin (int, optional): label margin. (default: 3)

        Note:
            - if keyword is None, default value is used.
        """
        row_data = self.set_common_row_data("text3d", opacity, position, cell, name, label, margin)

        if text is not None:
            row_data["text"] = text
        if size is not None:
            row_data["size"] = convert_to_str(size)
        if view is not None:
            if isinstance(view, np.ndarray):
                view = view.tolist()
            row_data["view"] = convert_to_str(view)
        if depth is not None:
            row_data["depth"] = convert_to_str(depth)
        if offset is not None:
            if isinstance(offset, np.ndarray):
                offset = offset.tolist()
            row_data["offset"] = convert_to_str(offset)
        if color is not None:
            row_data["color"] = convert_to_str(color)

        row_data = list(row_data.values())
        self._data["text3d"].append_row(row_data)

    # ==================================================
    def add_isosurface(
        self,
        data=None,
        value=None,
        surface=None,
        color=None,
        color_range=None,
        opacity=None,
        position=None,
        cell=None,
        name=None,
        label=None,
        margin=None,
    ):
        """
        Add isosurface.

        Args:
            data (str, optional): data (file) name for grid data. (default: "")
            value (str, optional): isosurface values. (default: [0.5])
            surface (str, optional): surface value name. (default: "")
            color (str, optional): text color. (default: white)
            color_range (str, optional): color range. (default: [0,1])
            opacity (float, optional): opacity, [0,1]. (default: 0.8)
            position (str, optional): position in cell, [x,y,z]. (default: [0,0,0])
            cell (str, optional): cell, [nx,ny,nz]. (default: [0,0,0])
            name (str, optional): name of group. (default: untitled)
            label (str, optional): label. (default: label)
            margin (int, optional): label margin. (default: 3)

        Note:
            - if keyword is None, default value is used.
            - if filename is tuple, (name, dict), use dict data as name.
        """
        row_data = self.set_common_row_data("isosurface", opacity, position, cell, name, label, margin)

        if data is None or data == "":
            row_data["data"] = ""
        else:
            if type(data) == tuple:
                name, dic = data
                row_data["data"] = name
                self._isosurface_data[name] = dic
            else:
                row_data["data"] = self.set_isosurface_data(data)

        if surface is not None:
            row_data["surface"] = convert_to_str(surface)
        if value is not None:
            if isinstance(value, np.ndarray):
                value = value.tolist()
            row_data["value"] = convert_to_str(value)
        if color is not None:
            row_data["color"] = convert_to_str(color)
        if color_range is not None:
            if isinstance(color_range, np.ndarray):
                color_range = color_range.tolist()
            row_data["color_range"] = convert_to_str(color_range)

        row_data = list(row_data.values())
        self._data["isosurface"].append_row(row_data)

    # ==================================================
    def add_caption(
        self,
        caption=None,
        size=None,
        bold=None,
        color=None,
        position=None,
        cell=None,
        name=None,
        margin=None,
    ):
        """
        Add caption.

        Args:
            caption (str, optional): caption list. (default: [A,B,C])
            size (int, optional): caption size. (default: 18)
            bold (bool, optional): bold ? (default: True)
            color (str, optional): caption color. (default: licorice)
            position (str, optional): position of each caption. (default: [[0,0,0],[1,0,0],[1,1,0]])
            cell (str, optional): cell. (default: [0,0,0])
            name (str, optional): name of group. (default: untitled)
            margin (int, optional): label margin. (default: 3)

        Note:
            - if keyword is None, default value is used.
        """
        row_data = self.set_common_row_data("caption", None, position, cell, name, None, margin)

        if caption is not None:
            row_data["caption"] = caption
        if size is not None:
            row_data["size"] = convert_to_str(size)
        if bold is not None:
            row_data["bold_check"] = bold
        if color is not None:
            row_data["color"] = convert_to_str(color)

        row_data = list(row_data.values())
        self._data["caption"].append_row(row_data)

    # ==================================================
    def add_text2d(
        self,
        caption=None,
        size=None,
        color=None,
        font=None,
        position=None,
        name=None,
    ):
        """
        Add text 2d.

        Args:
            caption (str, optional): caption. (default: text)
            size (int, optional): caption size. (default: 8)
            color (str, optional): caption color. (default: licorice)
            font (str, optional): caption font. (default: arial)
            position (str, optional): position in cell, [x,y,z]. (default: [0,0,0])
            name (str, optional): name of group. (default: untitled)

        Note:
            - if keyword is None, default value is used.
        """
        row_data = self.set_common_row_data("text2d", None, position, None, name, None, None)

        if caption is not None:
            row_data["caption"] = caption
        if size is not None:
            row_data["size"] = convert_to_str(size)
        if color is not None:
            row_data["color"] = convert_to_str(color)
        if font is not None:
            row_data["font"] = convert_to_str(font)

        row_data = list(row_data.values())
        self._data["text2d"].append_row(row_data)

    # ==================================================
    # io interface
    # ==================================================
    def load(self, filename):
        """
        Load all info.

        Args:
            filename (str): full file name.
        """
        # rename.
        file = Path(filename)
        folder = file.parent.as_posix()

        # set current directory.
        self.set_model(file.stem)
        if folder != "":
            os.chdir(folder)

        # read.
        f = file.resolve().as_posix()
        self.clear_info()
        self.reload()
        if file.suffix == detail["extension"]:
            all_data = read_dict(f)
            ver = int(all_data["version"].split(".")[0])  # major version.
            if ver < 2:
                widget = PyVistaWidget(off_screen=True)
                all_data = convert_version2(all_data, widget)  # for old version.
                widget.close()
        elif file.suffix in detail["ext_material"]:
            all_data = read_draw(f, self)
        else:
            raise Exception(f"cannot read {file.suffix} file.")
        self.write_info(f"* read from {f}.")

        # set data.
        self.set_property(all_data["status"], all_data["preference"])
        if file.suffix == detail["extension"]:
            self.set_camera_info(all_data["camera"])
            self.reload(all_data["data"])
        else:
            self.set_view()

    # ==================================================
    def get_data_dict(self, home_cell=False):
        """
        Get data dict.

        Args:
            home_cell (bool, optional): home cell only ?

        Returns:
            - (dict) -- data dict, {object_type: [[data]]}.

        :meta private:
        """
        center_cell = "[0,0,0]"

        data = {}
        for object_type, model in self._data.items():
            lst = np.array(model.tolist(), dtype=object)
            if len(lst) > 0:
                if home_cell:
                    lst = lst[np.char.strip(lst[:, COLUMN_CELL].astype(str)) == center_cell]
                lst[:, COLUMN_NAME_ACTOR] = ""
                lst[:, COLUMN_LABEL_ACTOR] = ""
                data[object_type] = lst.tolist()

        return data

    # ==================================================
    def restore(self):
        """
        Restore data and status from backup.

        :meta private:
        """
        if self._backup is None:
            return

        status = self._backup["status"]
        preference = self._backup["preference"]
        camera = self._backup["camera"]
        data = self._backup["data"]

        self.set_property(status, preference)
        self.set_camera_info(camera)
        self.reload(data)
        self.refresh()

    # ==================================================
    def save_current(self):
        """
        Save current data and stutus into self._backup.

        :meta private:
        """
        all_data = {
            "version": __version__,
            "data": self.get_data_dict(),
            "status": self._status,
            "preference": self._preference,
            "camera": self.get_camera_info(),
        }

        self._backup = copy.deepcopy(all_data)

    # ==================================================
    def save(self, filename):
        """
        save all info.

        Args:
            filename (str): full file name.
        """
        # rename.
        file = Path(filename)
        folder = file.parent.as_posix()
        base = file.stem
        self.set_model(base)
        if folder != "":
            os.chdir(folder)

        # set self._backup.
        self.save_current()
        # remove temp. info.
        if "plus" in self._backup["status"].keys():
            del self._backup["status"]["plus"]
        if "multipie" in self._backup["status"].keys() and "plus" in self._backup["status"]["multipie"].keys():
            del self._backup["status"]["multipie"]["plus"]

        isosurface = self._backup["data"].get("isosurface")
        if isosurface and len(isosurface) > 0:
            for iso in isosurface:
                name = iso[COLUMN_ISOSURFACE_FILE]
                with open(name, mode="w", encoding="utf-8") as f:
                    print(self._isosurface_data[name], file=f)

        # write.
        file = file.resolve().as_posix()
        header = "\nQtDraw data file in Python dict format.\n"
        with open(file, mode="w", encoding="utf-8") as f:
            print('"""' + header + '"""', file=f)
            print(self._backup, file=f)

        # formatter.
        try:
            cmd = f"black --line-length=300 {filename}"
            subprocess.run(cmd, capture_output=True, check=True, shell=True)
        except:
            pass

        self.write_info(f"* write to {file}.")

    # ==================================================
    def save_screenshot(self, filename):
        """
        Save screenshot to file.

        Args:
            full_path (str): fullpath file name.
        """
        file = Path(filename)
        f = file.resolve().as_posix()

        if file.suffix in detail["image_file"]:
            self.screenshot(f, transparent_background=True)
        elif file.suffix in detail["vector_file"]:
            self.save_graphic(f, "")

        self.write_info(f"* write screenshot to {f}.")

    # ==================================================
    def write_info(self, text):
        """
        Write text message (emit message signal).

        Args:
            text (str): message.

        :meta private:
        """
        self.message.emit(text)

    # ==================================================
    # widget control.
    # ==================================================
    def set_property(self, status=None, preference=None):
        """
        Set status and preference.

        Args:
            status (dict, optional): status.
            preference (dict, optional): preference.

        :meta private:
        """
        if status is not None:
            self._status.update(status)
        self.set_additional_status()

        if preference is not None:
            for key, value in preference.items():
                for k, v in value.items():
                    self._preference[key][k] = v

        if status is not None or preference is not None:
            self.refresh()
            self.redraw()

    # ==================================================
    def update_status(self, key, value):
        """
        Update status.

        Args:
            key (str): status key.
            value (Any): value.

        :meta private:
        """
        self.set_property(status={key: value})

    # ==================================================
    def update_preference(self, category, key, value):
        """
        Update preference.

        Args:
            category (str): category.
            key (str): status key.
            value (Any): value.

        :meta private:
        """
        self.set_property(preference={category: {key: value}})

    # ==================================================
    def reload(self, data=None):
        """
        Reload data and draw object.

        Args:
            data (dict, optional): object data.

        :meta private:
        """
        self._block_remove_isosurface = True
        for model in self._data.values():
            model.clear_data()
        self.deselect_actor_all()
        if data is None:
            self._status["repeat"] = False
            self._status["grid"] = False
        else:
            self.add_data(data)
        self.reset_camera()
        self._block_remove_isosurface = False

    # ==================================================
    def refresh(self):
        """
        Refresh widget setting.

        :meta private:
        """
        self.set_parallel_projection()
        self.set_grid()
        self.set_axis()
        self.set_cell()
        self.set_light()
        self.set_latex()
        self.set_bar()

    # ==================================================
    # propery
    # ==================================================
    @property
    def a1(self):
        """
        Get a1 unit vector.

        Returns:
            - (list) -- a1 unit vector.
        """
        return self.A_matrix[0:3, 0]

    # ==================================================
    @property
    def a2(self):
        """
        Get a2 unit vector.

        Returns:
            - (list) -- a2 unit vector.
        """
        return self.A_matrix[0:3, 1]

    # ==================================================
    @property
    def a3(self):
        """
        Get a3 unit vector.

        Returns:
            - (list) -- a3 unit vector.
        """
        return self.A_matrix[0:3, 2]

    # ==================================================
    @property
    def origin(self):
        """
        Get origin.

        Returns:
            - (list) -- origin.
        """
        return self._status["origin"]

    # ==================================================
    @property
    def cell_volume(self):
        """
        Get cell volume.

        Returns:
            - (float) -- unit cell volume.
        """
        a1 = self.A_matrix[0:3, 0]
        a2 = self.A_matrix[0:3, 1]
        a3 = self.A_matrix[0:3, 2]

        volume = np.abs(np.dot(a1, np.cross(a2, a3)))
        return volume

    # ==================================================
    @property
    def A_matrix(self):
        """
        Get transform matrix.

        Returns:
            - (numpy.ndarray) -- primitive vectors in each column (4x4).
        """
        A = np.array(self._status["plus"]["A"], dtype=np.float64)

        return A

    # ==================================================
    @property
    def A_matrix_norm(self):
        """
        Get transform matrix (normalized).

        Returns:
            - (numpy.ndarray) -- primitive vectors in each column (4x4).
        """
        A = self.A_matrix
        A = A / np.linalg.norm(A, axis=0)

        return A

    # ==================================================
    @property
    def G_matrix(self):
        """
        Get metric matrix.

        Returns:
            - (numpy.ndarray) -- metric matrix (4x4).
        """
        A = self.A_matrix
        G = A.T @ A

        return G

    # ==================================================
    @property
    def actor_list(self):
        """
        Get list of actor.

        Returns:
            - (list) -- actor names, [str].
        """
        return list(self.actors.keys())

    # ==================================================
    @property
    def window_title(self):
        """
        Get window title.

        Returns:
            - (str) -- window title.
        """
        model = self._status["model"]
        return f"QtDraw - {model}"

    # ==================================================
    @property
    def copyright(self):
        """
        Copyright string.

        Returns:
            - (str) -- copyright string.
        """
        cr = f"Versoin {__version__}, Copyright (C) {__date__} by {__author__}"
        return cr

    # ==================================================
    # set status
    # ==================================================
    def set_model(self, name=None):
        """
        Set model name.

        Args:
            name (str, optional): model name.

        Note:
            - if name is None, default is used.
        """
        if name is not None:
            self._status["model"] = name

    # ==================================================
    def set_crystal(self, crystal=None):
        """
        Set crystal.

        Args:
            crystal (str, optional): crystal, "triclinic/monoclinic/orthorhombic/tetragonal/trigonal/hexagonal/cubic".

        Note:
            - if crystal is None, default is used.
            - set unit cell.
        """
        if crystal is not None:
            self._status["crystal"] = crystal

        self.set_unit_cell()

    # ==================================================
    def set_origin(self, origin=None):
        """
        Set origin.

        Args:
            origin (list or str, optional): origin.

        Note:
            - if origin is None, default is used.
            - set cell.
        """
        if origin is not None:
            if type(origin) == str:
                origin = convert_str_vector(origin, transform=False).tolist()
            self._status["origin"] = origin

        self.set_cell()

    # ==================================================
    def set_unit_cell(self, cell=None):
        """
        Set unit cell.

        Args:
            cell (dict, optional): unit cell, {a, b, c, alpha, beta, gamma}.

        Note:
            - if cell is None, default is used.
            - set cell.
        """
        if cell is not None:
            self._status["cell"].update(cell)

        self.set_additional_status()

        self.set_cell()
        self.set_repeat()

    # ==================================================
    def set_clip(self, mode=None):
        """
        Set clip mode.

        Args:
            mode (bool, optional): clip object ?

        Note:
            - if mode is None, default is used.
        """
        if mode is None:
            mode = self._status["clip"]
        else:
            self._status["clip"] = mode

        if mode:
            self.hide_outside_actor()
        else:
            self.show_outside_actor()

    # ==================================================
    def hide_outside_actor(self):
        """
        Hide actors outside the range.

        :meta private:
        """
        lower = self._status["lower"]
        upper = self._status["upper"]
        for object_type, model in self._data.items():
            if object_type != "text2d":
                value = np.array(model.tolist(), dtype=object)
                if len(value) > 0:
                    point = "[" + ",".join(value[:, COLUMN_POSITION]) + "]"
                    cell = "[" + ",".join(value[:, COLUMN_CELL]) + "]"
                    name_actor = value[:, COLUMN_NAME_ACTOR]
                    point = convert_str_vector(point, cell, False)
                    idx = get_outside_box(point, lower, upper)
                    hide = name_actor[idx]
                    for actor_name in hide:
                        if actor_name != "":
                            self.actors[actor_name].SetVisibility(False)
                    if object_type != "caption":
                        label_actor = value[:, COLUMN_LABEL_ACTOR][idx]
                        for i in label_actor:
                            if i != "":
                                self.actors[i].SetVisibility(False)

    # ==================================================
    def clip_actor(self, position, cell, name_actor, label_actor):
        """
        Clip actor.

        Args:
            position (str): position.
            cell (str): cell.
            name_actor (str): name actor.
            label_actor (str): label actor.

        :meta private:
        """
        if not self._status["clip"]:
            return

        lower = self._status["lower"]
        upper = self._status["upper"]
        point = "[" + position + "]"
        cell = "[" + cell + "]"
        point = convert_str_vector(point, cell, False)
        idx = get_outside_box(point, lower, upper)
        if len(idx) > 0 and name_actor != "":
            self.actors[name_actor].SetVisibility(False)
        if label_actor is not None and len(idx) > 0 and label_actor != "":
            self.actors[label_actor].SetVisibility(False)

    # ==================================================
    def show_outside_actor(self):
        """
        Show actors outside the range.

        :meta private:
        """
        for object_type, model in self._data.items():
            if object_type != "text2d":
                value = np.array(model.tolist(), dtype=object)
                if len(value) > 0:
                    name_actor = value[:, COLUMN_NAME_ACTOR]
                    name_actor_check = value[:, COLUMN_NAME_CHECK].astype(bool)
                    idx = name_actor_check
                    show = name_actor[idx]
                    for actor_name in show:
                        self.actors[actor_name].SetVisibility(True)
                    if object_type != "caption":
                        label_actor_check = value[:, COLUMN_LABEL_CHECK].astype(bool)
                        idx = label_actor_check
                        label_actor = value[:, COLUMN_LABEL_ACTOR][idx]
                        for i in label_actor:
                            if i != "":
                                self.actors[i].SetVisibility(True)

    # ==================================================
    def set_repeat(self, mode=None):
        """
        Set repeat mode.

        Args:
            mode (bool, optional): repeat mode.

        Note:
            - if mode is None, default is used.
            - repeat data.
        """
        if mode is not None:
            self._status["repeat"] = mode

        self.repeat_data()
        self.set_clip()

    # ==================================================
    def set_range(self, lower=None, upper=None):
        """
        Set cell range.

        Args:
            lower (list or str, optional): lower bound, [float].
            upper (list or str, optional): upper bound, [float].

        Note:
            - if lower/upper is None, default is used.
            - set cell.
        """
        if lower is None:
            lower = self._status["lower"]
        else:
            if type(lower) == str:
                lower = convert_str_vector(lower, transform=False).tolist()
            self._status["lower"] = lower
        if upper is None:
            upper = self._status["upper"]
        else:
            if type(upper) == str:
                upper = convert_str_vector(upper, transform=False).tolist()
            self._status["upper"] = upper

        for i in range(3):
            if lower[i] > upper[i]:
                lower[i], upper[i] = upper[i], lower[i]
        self._status["lower"] = lower
        self._status["upper"] = upper

        self.set_additional_status()

        self.set_cell()
        self.set_repeat()

    # ==================================================
    def set_view(self, view=None):
        """
        Set view point.

        Args:
            view (list or str, optional): view indices of [a1,a2,a3], [int].

        Note:
            - if view is None, default is used.
        """
        if view is None:
            view = detail["default_view"]
        elif type(view) == str:
            view = convert_str_vector(view, transform=False)
            view = view.astype(int).tolist()

        if view == [0, 0, 0]:
            return

        self._status["view"] = view

        n = self._status["view"]

        # set view and viewup in cartesian coordinate.
        view, viewup = get_view_vector(n, self.A_matrix_norm)

        # set view and viewup of camera.
        self.view_vector(view, viewup)

    # ==================================================
    def set_parallel_projection(self, mode=None):
        """
        Set parallel projection mode.

        Args:
            mode (bool, optional): use parallel projection ?

        Note:
            - if mode is None, default is used.
        """
        if mode is None:
            mode = self._status["parallel_projection"]
        else:
            self._status["parallel_projection"] = mode

        if mode:
            self.enable_parallel_projection()
        else:
            self.disable_parallel_projection()

    # ==================================================
    def set_grid(self, mode=None):
        """
        Set grid mode.

        Args:
            mode (bool, optional): use grid ?

        Note:
            - if mode is None, default is used.
        """
        if mode is None:
            mode = self._status["grid"]
        else:
            self._status["grid"] = mode

        if mode:
            self.show_grid(location="all", bounds=self.bounds)
        else:
            self.remove_bounds_axes()
            self.remove_bounding_box()

    # ==================================================
    def set_bar(self, mode=None):
        """
        Set scalar bar mode.

        Args:
            mode (bool, optional): show scalar bar ?

        Note:
            - if mode is None, default is used.
        """
        if mode is None:
            mode = self._status["bar"]
        else:
            self._status["bar"] = mode

        if mode:
            self.add_scalar_bar(
                vertical=detail["bar_vertical"],
                width=detail["bar_width"],
                height=detail["bar_height"],
                position_x=detail["bar_x"],
                position_y=detail["bar_y"],
                label_font_size=detail["bar_size"],
                fmt=detail["bar_format"],
            )
        elif len(self._scalar_bars) > 0:
            self.remove_scalar_bar()

    # ==================================================
    def set_axis(self, axis_type=None):
        """
        Set axis widget.

        Args:
            axis_type (str, optional): axis type, "on/axis/full/off".

        Note:
            - if axis_type is None, default is used.
        """
        label_size = self._preference["axis"]["size"]
        label_bold = self._preference["axis"]["bold"]
        label_italic = self._preference["axis"]["italic"]
        label_color = detail["label_color"]

        if axis_type is None:
            axis_type = self._status["axis_type"]
        else:
            self._status["axis_type"] = axis_type

        viewport = True
        if axis_type == "on":
            label = self._preference["axis"]["label"]
        elif axis_type == "axis":
            label = None
        elif axis_type == "full":
            label = None
            viewport = False
        else:
            self.renderer.hide_axes()
            return

        if not self._off_screen:
            self.screen_off()
            create_axes_widget(
                self,
                self.A_matrix_norm,
                label=label,
                label_size=label_size,
                label_bold=label_bold,
                label_italic=label_italic,
                label_color=label_color,
                viewport=viewport,
            )
            self.screen_on()

    # ==================================================
    def set_cell(self, mode=None):
        """
        Set unit cell.

        Args:
            mode (str, optional): mode "single/all/off.

        Note:
            - if mode is None, default is used.
        """
        if mode is None:
            mode = self._status["cell_mode"]
        else:
            self._status["cell_mode"] = mode

        if mode == "off":
            self.remove_actor("unit_cell")
        elif mode == "single":
            self.show_cell([0, 0, 0], [1, 1, 1])
        else:
            self.show_cell()
        self.set_axis()

    # ==================================================
    # internal use (general).
    # ==================================================
    def init_data_model(self):
        """
        Initialize data model.

        :meta private:
        """
        self._selected_actor = {}  # actor selection, {actor_name: property}.

        self._actor_object_type = {}  # from actor_name to (object_type).
        self._data = {}
        for object_type, value in object_default.items():
            self._data[object_type] = GroupModel(object_type, value, parent=self)

    # ==================================================
    def set_theme(self, theme=None):
        """
        Set pyvista theme.

        Args:
            theme (str): pyvista theme, "document/dark/paraview".

        :meta private:
        """
        if theme is None:
            theme = detail["theme"]
        pv.set_plot_theme(theme)
        pv.global_theme.transparent_background = True
        pv.global_theme.axes.show = False
        pv.global_theme.axes.box = False
        pv.global_theme.cmap = "bwr"
        pv.global_theme.show_scalar_bar = False
        pv.global_theme.allow_empty_mesh = True

    # ==================================================
    def show_cell(self, lower=None, dimensions=None):
        """
        Show unit cell.

        Args:
            lower (list, optional): lower bound indices, [int].
            dimensions (list, optional): repeat times, [int].

        Note:
            - if lower/dimensions is None, default is used.

        :meta private:
        """
        origin = self.origin
        if lower is None:
            lower = self._status["plus"]["ilower"]
        if dimensions is None:
            dimensions = self._status["plus"]["dims"]
        cell = create_unit_cell(self.A_matrix, origin, lower, dimensions)

        self.screen_off()
        self.add_mesh(
            cell,
            line_width=self._preference["cell"]["line_width"],
            color=all_colors[self._preference["cell"]["color"]][0],  # hex,
            opacity=self._preference["cell"]["opacity"],
            smooth_shading=detail["smooth_shading"],
            name="unit_cell",
            pickable=False,
        )
        self.screen_on()

    # ==================================================
    def set_light(self, light_type=None, color=None, intensity=None):
        """
        Set light.

        Args:
            light_type (str, optional): light type, "lightkit/3 lights/ver1".
            color (str, optional): light color.
            intensity (float, optional): intensity of light.

        Note:
            - if light_type/color/intensity is None, default is used.

        :meta private:
        """
        preference = self._preference["light"]
        if light_type is None:
            light_type = preference["type"]
        else:
            preference["type"] = light_type
        if color is None:
            color = preference["color"]
        else:
            preference["color"] = color
        if intensity is None:
            intensity = preference["intensity"]
        else:
            preference["intensity"] = intensity

        color = all_colors[color][1]

        def set_light_prop(color, lights):
            for light in lights:
                light.specular_color = color
                light.diffuse_color = color
                light.ambient_color = all_colors["black"][1]

        if light_type == "lightkit":
            self.remove_all_lights()
            self.enable_lightkit()
            lights = self.renderer.lights
            set_light_prop(color, lights)
            for light in lights:
                light.intensity = light.intensity + 0.2 * (intensity - 0.5) + 0.1
        elif light_type == "3 lights":
            self.remove_all_lights()
            self.enable_3_lights()
            lights = self.renderer.lights
            set_light_prop(color, lights)
            for light in lights[1:]:
                light.intensity = light.intensity + 0.4 * (intensity - 0.5)
        elif light_type == "ver1":
            self.remove_all_lights()
            self.add_light(pv.Light(light_type="headlight", intensity=0.55))
            self.add_light(pv.Light(light_type="headlight", intensity=intensity))

        if preference["pbr"]:
            self.add_light(pv.Light(color=color, light_type="headlight", intensity=1.0))

    # ==================================================
    def set_latex(self):
        """
        Set LaTeX environment.

        :meta private:
        """
        pass

    # ==================================================
    def screen_off(self):
        """
        Screen off.
        """
        self.ren_win.SetOffScreenRendering(1)

    # ==================================================
    def screen_on(self):
        """
        Screen on.
        """
        self.ren_win.SetOffScreenRendering(0)

    # ==================================================
    def clear_data(self):
        """
        Clear Data.
        """
        self.reload()

    # ==================================================
    def get_camera_info(self):
        """
        Get camera info.

        Returns:
            - (dict) -- camera info.

        :meta private:
        """
        camera = self.camera
        position = np.array(camera.position).round(DIGIT).tolist()
        viewup = np.array(camera.up).round(DIGIT).tolist()
        focal_point = np.array(camera.focal_point).round(DIGIT).tolist()
        angle = np.array(camera.view_angle).round(DIGIT).tolist()
        scale = np.array(camera.parallel_scale).round(DIGIT).tolist()
        clipping_range = np.array(camera.clipping_range).round(DIGIT).tolist()
        distance = np.array(camera.distance).round(DIGIT).tolist()

        dic = {
            "position": position,
            "viewup": viewup,
            "focal_point": focal_point,
            "angle": angle,
            "clipping_range": clipping_range,
            "distance": distance,
            "scale": scale,
        }

        return dic

    # ==================================================
    def set_camera_info(self, info):
        """
        Get camera info.

        Args:
            info (dict): camera info.

        :meta private:
        """
        self.camera.position = info["position"]
        self.camera.up = info["viewup"]
        self.camera.focal_point = info["focal_point"]
        self.camera.view_angle = info["angle"]
        self.camera.clipping_range = info["clipping_range"]
        self.camera.distance = info["distance"]
        self.camera.parallel_scale = 1.0
        self.camera.zoom(1.0 / info["scale"])

    # ==================================================
    # internal use (access data).
    # ==================================================
    def add_data(self, data):
        """
        Add data.

        Args:
            data (dict): all object data, {object_type: [[data]]}.

        :meta private:
        """
        if sum(len(i) for i in data.values()) == 0:
            return

        for object_type, model in data.items():
            self._data[object_type].block_update_widget(True)
            self._data[object_type].set_data(model)
            self._data[object_type].block_update_widget(False)

    # ==================================================
    def repeat_data(self):
        """
        Repeat data.

        :meta private:
        """
        data = self.get_data_dict(home_cell=True)
        if self._status["repeat"]:
            grid = create_grid(self._status["plus"]["ilower"], self._status["plus"]["dims"])
            for object_type, model in data.items():
                n = len(model)
                if object_type != "text2d" and n > 0:
                    model = np.tile(np.array(model, dtype=object), (len(grid), 1))
                    for i, g in enumerate(grid):
                        model[n * i : n * (i + 1), COLUMN_CELL] = str(g)
                    data[object_type] = model.tolist()

        self.reload(data)

    # ==================================================
    def set_nonrepeat(self):
        """
        Transform data to non-repeat data.
        """
        self.nonrepeat_data()

    # ==================================================
    def nonrepeat_data(self):
        """
        Transform data to non-repeat data.

        :meta private:
        """
        data = self.get_data_dict()
        for object_type, model in data.items():
            n = len(model)
            if object_type not in ["text2d", "caption"] and n > 0:
                model = np.array(model, dtype=object)
                pos = np.array(list(map(ast.literal_eval, model[:, COLUMN_POSITION])))
                cell = np.array(list(map(ast.literal_eval, model[:, COLUMN_CELL])))
                pos += cell
                pos = np.array(list(map(str, pos.tolist())), dtype=object)
                model[:, COLUMN_POSITION] = pos
                model[:, COLUMN_CELL] = "[0,0,0]"
                data[object_type] = model.tolist()

        self.reload(data)

    # ==================================================
    def set_actor(self, object_type, index, actor_name, column=COLUMN_NAME_ACTOR):
        """
        Set actor.

        Args:
            object_type (str): object type.
            index (QModelIndex): index.
            actor_name (str): actor name.
            column (int, optional): column.

        :meta private:
        """
        model = self._data[object_type]
        model.set_row_data(index, column, actor_name)
        if column == COLUMN_NAME_ACTOR:
            self._actor_object_type[actor_name] = object_type

        # set saved property.
        if actor_name in self._selected_actor.keys():
            actor = self.actors[actor_name]
            self._selected_actor[actor_name] = (actor.prop.show_edges, actor.prop.edge_color)

    # ==================================================
    def delete_actor(self, actor_name):
        """
        Remove actor.

        Args:
            actor_name (str): actor name.

        :meta private:
        """
        if actor_name != "":
            self.remove_actor(actor_name)
            if actor_name in self._actor_object_type.keys():
                del self._actor_object_type[actor_name]

    # ==================================================
    def change_check_state(self, object_type, row_data, index):
        """
        Change check state (when name is off, label is also off).

        Args:
            object_type (str): object type.
            row_data (list): row data.
            index (QModelIndex): index.

        :meta private:
        """
        UNCHECK = 0  # Qt.Uncheck.
        if object_type not in ["caption", "text2d"] and index.column() == 0:
            state = index.data(Qt.CheckStateRole)
            if state == UNCHECK:
                self._data[object_type].set_check(index, COLUMN_LABEL, UNCHECK)
        self.plot_data(object_type, row_data, index)

    # ==================================================
    # internal use (gui interface).
    # ==================================================
    def open_tab_group_view(self):
        """
        Open tab group view.

        :meta private:
        """
        self._tab_group_view.show()
        self._tab_group_view.update_widget()

    # ==================================================
    def release_mouse(self):
        """
        Release mouse button.

        :meta private:
        """
        pos = QCursor().pos()
        event = QMouseEvent(
            QEvent.MouseButtonRelease,
            pos,
            pos,
            Qt.LeftButton,
            Qt.LeftButton,
            Qt.NoModifier,
        )
        QCoreApplication.sendEvent(self, event)

    # ==================================================
    def keyPressEvent(self, event):
        """
        In order to prevent default keys.

        :meta private:
        """
        prevent_keys = detail["prevent_key"]
        if event.text() not in prevent_keys:
            super().keyPressEvent(event)
        else:
            pass

    # ==================================================
    def closeEvent(self, event):
        """
        In order to close QInteractor, and opened dialogs.

        :meta private:
        """
        self.close()

    # ==================================================
    def close(self):
        """
        In order to close QInteractor, and opened dialogs.

        :meta private:
        """
        self._tab_group_view.close()
        super().close()

    # ==================================================
    def remove_data(self, object_type, row_data, index):
        """
        Remove data.

        Args:
            object_type (str): object type.
            row_data (list): row data.
            index (QIndexModel): index.

        :meta private:
        """
        actor_name = row_data[COLUMN_NAME_ACTOR]
        self.delete_actor(actor_name)

        if object_type not in ["caption", "text2d"]:
            actor_name = row_data[COLUMN_LABEL_ACTOR]
            self.delete_actor(actor_name)

        if object_type == "isosurface" and not self._block_remove_isosurface:
            filename = row_data[COLUMN_ISOSURFACE_FILE]
            if filename in self._isosurface_data.keys():
                del self._isosurface_data[filename]

    # ==================================================
    # internal use (context menu).
    # ==================================================
    def show_context_menu(self, actor):
        """
        Show context menu.

        Args:
            actor (pv.Actor): picked actor.

        Note:
            - connect to open_selected, hide_selected, remove_selected signals are required.

        :meta private:
        """
        self.select_actor(actor.name)

        menu = QMenu(self)

        # open menu.
        opn = menu.addAction("Open")
        opn.triggered.connect(lambda: self.open_action(actor))

        # hide menu. default hiding actor is called at the end.
        hide = menu.addAction("Hide")
        hide.triggered.connect(lambda: self.hide_action(actor))

        # remove menu. default removing actor is called at the end.
        remove = menu.addAction("Remove")
        remove.triggered.connect(lambda: self.remove_action(actor))

        # should release mouse, and show context menu.
        self.release_mouse()
        menu.exec(QCursor().pos())

        # restore actor property.
        self.deselect_actor(actor.name)

    # ==================================================
    def open_action(self, actor):
        """
        Action for open in context menum.

        Args:
            actor (pv.Actor): actor.

        :meta private:
        """
        object_type, index = self.find_index(actor)
        self.open_tab_group_view()
        self._tab_group_view.select_tab(object_type)
        self._tab_group_view.view[object_type].select_row(index)

    # ==================================================
    def hide_action(self, actor):
        """
        Action for hide in context menu.

        Args:
            actor (pv.Actor): actor.

        :meta private:
        """
        object_type, index = self.find_index(actor)
        UNCHECK = 0  # Qt.Uncheck.
        self._data[object_type].setData(index, UNCHECK, Qt.CheckStateRole)

    # ==================================================
    def remove_action(self, actor):
        """
        Action for remove in context menu.

        Args:
            actor (pv.Actor): actor.

        :meta private:
        """
        object_type, index = self.find_index(actor)
        self._data[object_type].remove_row(index)
        self.deselect_actor_all()

    # ==================================================
    def select_actor(self, actor_name):
        """
        Select actor with spotlight.

        Args:
            actor_name (str): actor name.

        :meta private:
        """
        # already selected.
        if actor_name in self._selected_actor.keys():
            return

        actor = self.actors[actor_name]

        # save actor's diffuse color setting.
        prop = (actor.prop.show_edges, actor.prop.edge_color)
        self._selected_actor[actor_name] = prop

        # set selected.
        color = all_colors[detail["spotlight_color"]][0]  # hex
        actor.prop.show_edges = True
        actor.prop.edge_color = color

    # ==================================================
    def deselect_actor(self, actor_name):
        """
        Deselect actor with reset of spotlight.

        Args:
            actor_name (str): actor name.

        :meta private:
        """
        if actor_name in self.actors.keys() and actor_name in self._selected_actor.keys():
            actor = self.actors[actor_name]
            prop = self._selected_actor[actor_name]
            actor.prop.show_edges = prop[0]
            actor.prop.edge_color = prop[1]
            del self._selected_actor[actor_name]

    # ==================================================
    def deselect_actor_all(self):
        """
        Deselect all selected actors.

        :meta private:
        """
        for actor_name, prop in self._selected_actor.items():
            if actor_name in self.actors.keys():
                actor = self.actors[actor_name]
                actor.prop.show_edges = prop[0]
                actor.prop.edge_color = prop[1]
        self._selected_actor = {}

    # ==================================================
    def change_selection(self, object_type, deselect, select):
        """
        Change selection for spotlight.

        Args:
            object_type (str): object type.
            deselect (list): deselected rows.
            select (list): selected rows.

        :meta private:
        """
        # skip for caption and text2d.
        if object_type in ["caption", "text2d"]:
            return

        # deselected.
        if deselect is not None:
            for row in deselect:
                actor_name = row[COLUMN_NAME_ACTOR]
                self.deselect_actor(actor_name)

        # selected.
        if select is not None:
            for row in select:
                actor_name = row[COLUMN_NAME_ACTOR]
                if actor_name != "":
                    self.select_actor(actor_name)

    # ==================================================
    def find_index(self, actor):
        """
        Find index from actor.

        Args:
            actor (pv.Actor): actor.
            label (bool, optional): label actor ?

        Returns:
            - (str) -- object type.
            - (QModelIndex) -- index.

        :meta private:
        """
        actor_name = actor.name
        object_type = self._actor_object_type[actor_name]
        index = self._data[object_type].find_item(actor_name, COLUMN_NAME_ACTOR)
        assert len(index) < 3
        # when parent=child[0], take child one.
        index = index[-1].index().siblingAtColumn(0)
        return object_type, index

    # ==================================================
    # internal use (add object utility).
    # ==================================================
    def set_common_row_data(self, object_type, opacity, position, cell, name, label, margin):
        """
        Set common row data.

        Args:
            object_type (str): object type.
            opacity (float): opacity.
            position (str): position.
            cell (str): cell.
            name (str): group name.
            label (str): label.
            margin (int): label margin.

        Returns:
            - (dict) -- row data.

        :meta private:
        """
        data = self._data[object_type].column_default
        header = self._data[object_type].header
        row_data = dict(zip(header, data))

        if opacity is not None:
            row_data["opacity"] = convert_to_str(opacity)
        if position is not None:
            if isinstance(position, np.ndarray):
                position = position.tolist()
            row_data["position"] = convert_to_str(position)
        if cell is not None:
            if isinstance(cell, np.ndarray):
                cell = cell.tolist()
            row_data["cell"] = convert_to_str(cell)
        if name is not None:
            row_data["name"] = name
        if label is not None:
            row_data["label"] = label
            row_data["label_check"] = self._preference["label"]["default_check"]
        if margin is not None:
            row_data["margin"] = convert_to_str(margin)

        return row_data

    # ==================================================
    # internal use (plot object utility).
    # ==================================================
    def plot_data(self, object_type, row_data, index):
        """
        Plot mesh from data.

        Args:
            object_type (str): object type.
            row_data (list): row data.
            index (QIndexModel): index.

        :meta private:
        """
        tag = self._data[object_type].header
        no_label = object_type in ["caption", "text2d"]
        row_info = dict(zip(tag, row_data))
        name_check, label_check = self.check_hide(row_info, no_label)
        position = row_info["position"]
        cell = row_info["cell"]
        positionT = convert_str_vector(vector=position, cell=cell, A=self.A_matrix)
        if name_check:
            self._plot_signal[object_type].plot.emit(index, row_info, positionT)
        if label_check and not no_label:
            self.plot_label(object_type, index, row_info, positionT)

    # ==================================================
    def redraw(self):
        """
        Redraw all object.

        :meta private:
        """
        for model in self._data.values():
            model.emit_update_all()

    # ==================================================
    def common_option(self, actor, positionT, obj):
        """
        Create common option to plot.

        Args:
            actor (str): actor name.
            positionT (numpy.ndarray): position (transformed).
            obj (vtk.PolyData): object to plot.

        Returns:
            - (dict) -- common option.

        :meta private:
        """
        if actor == "":
            actor = None

        g = obj.copy()
        g = g.translate(positionT, inplace=True)

        option = {
            "mesh": g,
            "smooth_shading": detail["smooth_shading"],
            "pbr": self._preference["light"]["pbr"],
            "metallic": self._preference["light"]["metallic"],
            "roughness": self._preference["light"]["roughness"],
            "name": actor,
            "show_edges": False,
        }

        return option

    # ==================================================
    def label_option(self, positionT, label, margin):
        """
        Create common option to plot.

        Args:
            positionT (numpy.ndarray): position (transformed).
            label (str): label.
            margin (int): margin.

        Returns:
            - (dict) -- label option.

        :meta private:
        """
        option = {
            "points": positionT,
            "labels": [" " * int(margin) + label],
            "font_family": self._preference["label"]["font"],
            "font_size": self._preference["label"]["size"],
            "bold": self._preference["label"]["bold"],
            "italic": self._preference["label"]["italic"],
            "text_color": all_colors[self._preference["label"]["color"]][0],
            "shape": None,
            "show_points": False,
            "always_visible": True,
        }

        return option

    # ==================================================
    def check_hide(self, row_data, no_label=False):
        """
        Check hide state.

        Args:
            row_data (list): data in a row, [str].
            no_label (bool, optional): without label data ?

        Returns:
            - (bool) -- display name ?
            - (bool) -- display label ?

        :meta private:
        """
        name_check = row_data["name_check"]
        if not no_label:
            if name_check:
                label_check = row_data["label_check"]
            else:
                label_check = False
        else:
            label_check = True

        if not label_check:
            label = row_data["label_actor"]
            if label in self.actors.keys():
                actor = self.actors[label]
                actor.SetVisibility(False)
        if not name_check:
            name = row_data["name_actor"]
            if name in self.actors.keys():
                actor = self.actors[name]
                actor.SetVisibility(False)

        return name_check, label_check

    # ==================================================
    # internal use (plot each object).
    # ==================================================
    def plot_data_site(self, index, data, positionT):
        """
        Plot site.

        Args:
            index (QModelIndex): index.
            data (dict): data list.
            positionT (numpy.ndarray): position (transformed).

        :meta private:
        """
        actor = data["name_actor"]
        size = float(data["size"])
        color = all_colors[data["color"]][0]  # hex
        opacity = float(data["opacity"])

        obj = create_sphere(radius=size)
        option_add = {"color": color, "opacity": opacity}

        option = self.common_option(actor=actor, positionT=positionT, obj=obj)
        option = option | option_add

        actor = self.add_mesh(**option)
        self.set_actor("site", index, actor.name)
        self.clip_actor(data["position"], data["cell"], actor.name, data["label_actor"])

    # ==================================================
    def plot_data_bond(self, index, data, positionT):
        """
        Plot bond.

        Args:
            index (QModelIndex): index.
            data (dict): data list.
            positionT (numpy.ndarray): position (transformed).

        :meta private:
        """
        actor = data["name_actor"]
        direction = data["direction"]
        width = float(data["width"])
        color = data["color"]
        color2 = data["color2"]
        transform = not data["cartesian_check"]
        opacity = float(data["opacity"])

        directionT = convert_str_vector(vector=direction, transform=transform, A=self.A_matrix)

        if color2 != color:
            obj = create_bond(direction=directionT, width=width, twotone=True)
            cmap = custom_colormap([color, color2])
            option_add = {"show_scalar_bar": False, "cmap": cmap, "opacity": opacity}
        else:
            obj = create_bond(direction=directionT, width=width, twotone=False)
            option_add = {"color": all_colors[color][0], "opacity": opacity}

        option = self.common_option(actor=actor, positionT=positionT, obj=obj)
        option = option | option_add

        actor = self.add_mesh(**option)
        self.set_actor("bond", index, actor.name)
        self.clip_actor(data["position"], data["cell"], actor.name, data["label_actor"])

    # ==================================================
    def plot_data_vector(self, index, data, positionT):
        """
        Plot vector.

        Args:
            index (QModelIndex): index.
            data (dict): data list.
            positionT (numpy.ndarray): position (transformed).

        :meta private:
        """
        actor = data["name_actor"]
        direction = data["direction"]
        length = float(data["length"])
        width = float(data["width"])
        offset = float(data["offset"])
        color = all_colors[data["color"]][0]  # hex
        transform = not data["cartesian_check"]
        shaft_radius = float(data["shaft R"])
        tip_radius = float(data["tip R"])
        tip_length = float(data["tip length"])
        opacity = float(data["opacity"])

        directionT = convert_str_vector(vector=direction, transform=transform, A=self.A_matrix)

        obj = create_vector(
            direction=directionT,
            length=length,
            width=width,
            offset=offset,
            shaft_radius=shaft_radius,
            tip_radius=tip_radius,
            tip_length=tip_length,
        )
        option_add = {"color": color, "opacity": opacity}

        option = self.common_option(actor=actor, positionT=positionT, obj=obj)
        option = option | option_add

        actor = self.add_mesh(**option)
        self.set_actor("vector", index, actor.name)
        self.clip_actor(data["position"], data["cell"], actor.name, data["label_actor"])

    # ==================================================
    def plot_data_orbital(self, index, data, positionT):
        """
        Plot orbital.

        Args:
            index (QModelIndex): index.
            data (dict): data list.
            positionT (numpy.ndarray): position (transformed).

        :meta private:
        """
        actor = data["name_actor"]
        shape = data["shape"]
        surface = data["surface"]
        size = float(data["size"])
        theta_phi_range = apply(float, text_to_list(data["range"]))
        color = data["color"]
        opacity = float(data["opacity"])

        obj = create_orbital(shape=shape, surface=surface, size=size, theta_phi_range=theta_phi_range)
        if check_color(color):
            option_add = {"color": all_colors[color][0], "opacity": opacity}
        else:
            scalars = "surface"
            if scalars in obj.array_names:
                clim = get_data_range(obj[scalars])
                option_add = {
                    "cmap": color.strip("*"),
                    "scalars": scalars,
                    "clim": clim,
                    "opacity": opacity,
                    "show_scalar_bar": False,
                }
            else:
                option_add = {
                    "cmap": color.strip("*"),
                    "opacity": opacity,
                    "show_scalar_bar": False,
                }

        option = self.common_option(actor=actor, positionT=positionT, obj=obj)
        option = option | option_add

        actor = self.add_mesh(**option)
        self.set_actor("orbital", index, actor.name)
        self.clip_actor(data["position"], data["cell"], actor.name, data["label_actor"])

    # ==================================================
    def plot_data_stream(self, index, data, positionT):
        """
        Plot stream (vectors in cartesian coordinate).

        Args:
            index (QModelIndex): index.
            data (dict): data list.
            positionT (numpy.ndarray): position (transformed).

        :meta private:
        """
        component_str = {"abs": None, "x": 0, "y": 1, "z": 2}

        actor = data["name_actor"]
        shape = data["shape"]
        vector = data["vector"]
        size = float(data["size"])
        theta_phi_range = apply(float, text_to_list(data["range"]))
        division = apply(int, text_to_list(data["division"]))
        length = float(data["length"])
        width = float(data["width"])
        offset = float(data["offset"])
        abs_scale = data["abs_scale_check"]
        color = data["color"]
        component = component_str[data["component"]]
        shaft_radius = float(data["shaft R"])
        tip_radius = float(data["tip R"])
        tip_length = float(data["tip length"])
        opacity = float(data["opacity"])

        obj = create_stream(
            shape=shape,
            vector=vector,
            size=size,
            theta_phi_range=theta_phi_range,
            division=division,
            length=length,
            width=width,
            offset=offset,
            abs_scale=abs_scale,
            shaft_radius=shaft_radius,
            tip_radius=tip_radius,
            tip_length=tip_length,
        )

        if check_color(color):
            option_add = {
                "color": all_colors[color][0],
                "opacity": opacity,
            }
        else:
            scalars = "GlyphVector"
            if scalars in obj.array_names:
                clim = get_data_range(obj[scalars])
                option_add = {
                    "clim": clim,
                    "scalars": scalars,
                    "cmap": color.strip("*"),
                    "show_scalar_bar": False,
                    "component": component,
                    "opacity": opacity,
                }
            else:
                option_add = {
                    "cmap": color.strip("*"),
                    "show_scalar_bar": False,
                    "opacity": opacity,
                }

        option = self.common_option(actor=actor, positionT=positionT, obj=obj)
        option = option | option_add

        actor = self.add_mesh(**option)
        self.set_actor("stream", index, actor.name)
        self.clip_actor(data["position"], data["cell"], actor.name, data["label_actor"])

    # ==================================================
    def plot_data_line(self, index, data, positionT):
        """
        Plot line.

        Args:
            index (QModelIndex): index.
            data (dict): data list.
            positionT (numpy.ndarray): position (transformed).

        :meta private:
        """
        actor = data["name_actor"]
        direction = data["direction"]
        width = float(data["width"])
        arrow1 = data["arrow1_check"]
        arrow2 = data["arrow2_check"]
        tip_radius = float(data["tip R"])
        tip_length = float(data["tip length"])
        color = all_colors[data["color"]][0]
        transform = not data["cartesian_check"]
        opacity = float(data["opacity"])

        directionT = convert_str_vector(vector=direction, transform=transform, A=self.A_matrix)

        obj = create_line(
            direction=directionT, width=width, arrow1=arrow1, arrow2=arrow2, tip_radius=tip_radius, tip_length=tip_length
        )
        option_add = {"color": color, "opacity": opacity}

        option = self.common_option(actor=actor, positionT=positionT, obj=obj)
        option = option | option_add

        actor = self.add_mesh(**option)
        self.set_actor("line", index, actor.name)
        self.clip_actor(data["position"], data["cell"], actor.name, data["label_actor"])

    # ==================================================
    def plot_data_plane(self, index, data, positionT):
        """
        Plot plane.

        Args:
            index (QModelIndex): index.
            data (dict): data list.
            positionT (numpy.ndarray): position (transformed).

        :meta private:
        """
        actor = data["name_actor"]
        normal = data["normal"]
        x_size = float(data["x_size"])
        y_size = float(data["y_size"])
        color = all_colors[data["color"]][0]  # hex
        width = float(data["width"])
        grid = data["grid_check"]
        grid_color = all_colors[data["grid_color"]][0]  # hex
        transform = not data["cartesian_check"]
        opacity = float(data["opacity"])

        normalT = convert_str_vector(vector=normal, transform=transform, A=self.A_matrix)

        obj = create_plane(normal=normalT, x_size=x_size, y_size=y_size)
        option_add = {
            "color": color,
            "opacity": opacity,
            "show_edges": grid,
            "line_width": width,
            "edge_color": grid_color,
        }

        option = self.common_option(actor=actor, positionT=positionT, obj=obj)
        option = option | option_add

        actor = self.add_mesh(**option)
        self.set_actor("plane", index, actor.name)
        self.clip_actor(data["position"], data["cell"], actor.name, data["label_actor"])

    # ==================================================
    def plot_data_circle(self, index, data, positionT):
        """
        Plot circle.

        Args:
            index (QModelIndex): index.
            data (dict): data list.
            positionT (numpy.ndarray): position (transformed).

        :meta private:
        """
        actor = data["name_actor"]
        normal = data["normal"]
        size = float(data["size"])
        color = all_colors[data["color"]][0]  # hex
        width = float(data["width"])
        edge = data["edge_check"]
        edge_color = all_colors[data["edge_color"]][0]  # hex
        transform = not data["cartesian_check"]
        opacity = float(data["opacity"])

        normalT = convert_str_vector(vector=normal, transform=transform, A=self.A_matrix)

        obj = create_circle(normal=normalT, size=size)
        option_add = {
            "color": color,
            "opacity": opacity,
            "show_edges": edge,
            "line_width": width,
            "edge_color": edge_color,
        }

        option = self.common_option(actor=actor, positionT=positionT, obj=obj)
        option = option | option_add

        actor = self.add_mesh(**option)
        self.set_actor("circle", index, actor.name)
        self.clip_actor(data["position"], data["cell"], actor.name, data["label_actor"])

    # ==================================================
    def plot_data_torus(self, index, data, positionT):
        """
        Plot torus.

        Args:
            index (QModelIndex): index.
            data (dict): data list.
            positionT (numpy.ndarray): position (transformed).

        :meta private:
        """
        actor = data["name_actor"]
        normal = data["normal"]
        size = float(data["size"])
        color = all_colors[data["color"]][0]  # hex
        width = float(data["width"])
        transform = not data["cartesian_check"]
        opacity = float(data["opacity"])

        normalT = convert_str_vector(vector=normal, transform=transform, A=self.A_matrix)

        obj = create_torus(normal=normalT, size=size, width=width)
        option_add = {"color": color, "opacity": opacity}

        option = self.common_option(actor=actor, positionT=positionT, obj=obj)
        option = option | option_add

        actor = self.add_mesh(**option)
        self.set_actor("torus", index, actor.name)
        self.clip_actor(data["position"], data["cell"], actor.name, data["label_actor"])

    # ==================================================
    def plot_data_ellipsoid(self, index, data, positionT):
        """
        Plot ellipsoid.

        Args:
            index (QModelIndex): index.
            data (dict): data list.
            positionT (numpy.ndarray): position (transformed).

        :meta private:
        """
        actor = data["name_actor"]
        normal = data["normal"]
        x_size = float(data["x_size"])
        y_size = float(data["y_size"])
        z_size = float(data["z_size"])
        color = all_colors[data["color"]][0]  # hex
        transform = not data["cartesian_check"]
        opacity = float(data["opacity"])

        normalT = convert_str_vector(vector=normal, transform=transform, A=self.A_matrix)

        obj = create_ellipsoid(normal=normalT, x_size=x_size, y_size=y_size, z_size=z_size)
        option_add = {"color": color, "opacity": opacity}

        option = self.common_option(actor=actor, positionT=positionT, obj=obj)
        option = option | option_add

        actor = self.add_mesh(**option)
        self.set_actor("ellipsoid", index, actor.name)
        self.clip_actor(data["position"], data["cell"], actor.name, data["label_actor"])

    # ==================================================
    def plot_data_toroid(self, index, data, positionT):
        """
        Plot toroid.

        Args:
            index (QModelIndex): index.
            data (dict): data list.
            positionT (numpy.ndarray): position (transformed).

        :meta private:
        """
        actor = data["name_actor"]
        normal = data["normal"]
        size = float(data["size"])
        width = float(data["width"])
        x_scale = float(data["x_scale"])
        y_scale = float(data["y_scale"])
        z_scale = float(data["z_scale"])
        ring_shape = float(data["ring_shape"])
        tube_shape = float(data["tube_shape"])
        color = all_colors[data["color"]][0]  # hex
        transform = not data["cartesian_check"]
        opacity = float(data["opacity"])

        normalT = convert_str_vector(vector=normal, transform=transform, A=self.A_matrix)

        obj = create_toroid(
            normal=normalT,
            size=size,
            width=width,
            x_scale=x_scale,
            y_scale=y_scale,
            z_scale=z_scale,
            ring_shape=ring_shape,
            tube_shape=tube_shape,
        )
        option_add = {"color": color, "opacity": opacity}

        option = self.common_option(actor=actor, positionT=positionT, obj=obj)
        option = option | option_add

        actor = self.add_mesh(**option)
        self.set_actor("toroid", index, actor.name)
        self.clip_actor(data["position"], data["cell"], actor.name, data["label_actor"])

    # ==================================================
    def plot_data_box(self, index, data, positionT):
        """
        Plot box.

        Args:
            index (QModelIndex): index.
            data (dict): data list.
            positionT (numpy.ndarray): position (transformed).

        :meta private:
        """
        actor = data["name_actor"]
        a1 = data["a1"]
        a2 = data["a2"]
        a3 = data["a3"]
        width = float(data["width"])
        edge = data["edge_check"]
        edge_color = all_colors[data["edge_color"]][0]  # hex
        wireframe = data["wireframe_check"]
        color = all_colors[data["color"]][0]  # hex
        transform = not data["cartesian_check"]
        opacity = float(data["opacity"])

        a1 = convert_str_vector(vector=a1, transform=transform, A=self.A_matrix)
        a2 = convert_str_vector(vector=a2, transform=transform, A=self.A_matrix)
        a3 = convert_str_vector(vector=a3, transform=transform, A=self.A_matrix)

        obj = create_box(a1=a1, a2=a2, a3=a3)
        if wireframe:
            option_add = {
                "color": color,
                "opacity": opacity,
                "style": "wireframe",
                "line_width": width,
            }
        else:
            option_add = {
                "color": color,
                "opacity": opacity,
                "show_edges": edge,
                "line_width": width,
                "edge_color": edge_color,
            }

        option = self.common_option(actor=actor, positionT=positionT, obj=obj)
        option = option | option_add

        actor = self.add_mesh(**option)
        self.set_actor("box", index, actor.name)
        self.clip_actor(data["position"], data["cell"], actor.name, data["label_actor"])

    # ==================================================
    def plot_data_polygon(self, index, data, positionT):
        """
        Plot polygon.

        Args:
            index (QModelIndex): index.
            data (dict): data list.
            positionT (numpy.ndarray): position (transformed).

        :meta private:
        """
        actor = data["name_actor"]
        point = data["point"]
        connectivity = data["connectivity"]
        width = float(data["width"])
        edge = data["edge_check"]
        edge_color = all_colors[data["edge_color"]][0]  # hex
        wireframe = data["wireframe_check"]
        color = all_colors[data["color"]][0]  # hex
        transform = not data["cartesian_check"]
        opacity = float(data["opacity"])

        pointT = convert_str_vector(vector=point, transform=transform, A=self.A_matrix)
        connectivity = apply(int, text_to_list(connectivity))

        obj = create_polygon(point=pointT, connectivity=connectivity)
        if wireframe:
            option_add = {
                "color": color,
                "opacity": opacity,
                "style": "wireframe",
                "line_width": width,
            }
        else:
            option_add = {
                "color": color,
                "opacity": opacity,
                "show_edges": edge,
                "line_width": width,
                "edge_color": edge_color,
            }

        option = self.common_option(actor=actor, positionT=positionT, obj=obj)
        option = option | option_add

        actor = self.add_mesh(**option)
        self.set_actor("polygon", index, actor.name)
        self.clip_actor(data["position"], data["cell"], actor.name, data["label_actor"])

    # ==================================================
    def plot_data_text3d(self, index, data, positionT):
        """
        Plot text3d (view and offset in reduced coordinate).

        Args:
            index (QModelIndex): index.
            data (dict): data list.
            positionT (numpy.ndarray): position (transformed).

        :meta private:
        """
        actor = data["name_actor"]
        text = data["text"]
        size = float(data["size"])
        view = data["view"]
        depth = float(data["depth"])
        offset = data["offset"]
        color = all_colors[data["color"]][0]  # hex
        opacity = float(data["opacity"])

        view = convert_str_vector(vector=view, transform=False)
        offset = convert_str_vector(vector=offset, transform=False)

        obj = create_text3d(
            text=text,
            size=size,
            view=view,
            depth=depth,
            offset=offset,
            A=self.A_matrix_norm,
        )
        option_add = {"color": color, "opacity": opacity}

        option = self.common_option(actor=actor, positionT=positionT, obj=obj)
        option = option | option_add

        actor = self.add_mesh(**option)
        self.set_actor("text3d", index, actor.name)
        self.clip_actor(data["position"], data["cell"], actor.name, data["label_actor"])

    # ==================================================
    def plot_data_isosurface(self, index, data, positionT):
        """
        Plot isosurface.

        Args:
            index (QModelIndex): index.
            data (dict): data list.
            positionT (numpy.ndarray): position (transformed).

        :meta private:
        """
        actor = data["name_actor"]
        data_name = data["data"]
        value = apply(float, text_to_list(data["value"]))
        surface = data["surface"]
        color = data["color"]
        color_range = apply(float, text_to_list(data["color_range"]))
        opacity = float(data["opacity"])

        if data_name == "":
            return
        elif self._isosurface_data.get(data_name) is None:
            data_name = self.set_isosurface_data(data_name)
        if data_name == "":
            return

        grid_data = self._isosurface_data[data_name]
        if surface not in grid_data["surface"].keys():
            surface = ""

        obj = create_isosurface(grid_data, value, surface)
        if len(obj.point_data.keys()) < 1:
            return

        if check_color(color):
            option_add = {"color": all_colors[color][0], "opacity": opacity}
        elif surface == "":
            option_add = {
                "cmap": color.strip("*"),
                "opacity": opacity,
                "show_scalar_bar": False,
            }
        else:
            clim = color_range
            option_add = {
                "cmap": color.strip("*"),
                "clim": clim,
                "scalars": surface,
                "opacity": opacity,
                "show_scalar_bar": False,
            }

        option = self.common_option(actor=actor, positionT=positionT, obj=obj)
        option = option | option_add

        actor = self.add_mesh(**option)
        self.set_actor("isosurface", index, actor.name)
        self.clip_actor(data["position"], data["cell"], actor.name, data["label_actor"])

    # ==================================================
    def plot_data_spline(self, index, data, positionT):
        """
        Plot spline.

        Args:
            index (QModelIndex): index.
            data (dict): data list.
            positionT (numpy.ndarray): position (transformed).

        :meta private:
        """
        actor = data["name_actor"]
        point = data["point"]
        width = float(data["width"])
        n_interp = int(data["n_interp"])
        closed = data["closed_check"]
        natural = data["natural_check"]
        arrow1 = data["arrow1_check"]
        arrow2 = data["arrow2_check"]
        tip_radius = float(data["tip R"])
        tip_length = float(data["tip length"])
        color = all_colors[data["color"]][0]
        transform = not data["cartesian_check"]
        opacity = float(data["opacity"])

        pointT = convert_str_vector(vector=point, transform=transform, A=self.A_matrix)

        obj = create_spline(
            point=pointT,
            width=width,
            n_interp=n_interp,
            closed=closed,
            natural=natural,
            arrow1=arrow1,
            arrow2=arrow2,
            tip_radius=tip_radius,
            tip_length=tip_length,
        )
        option_add = {"color": color, "opacity": opacity}

        option = self.common_option(actor=actor, positionT=positionT, obj=obj)
        option = option | option_add

        actor = self.add_mesh(**option)
        self.set_actor("spline", index, actor.name)
        self.clip_actor(data["position"], data["cell"], actor.name, data["label_actor"])

    # ==================================================
    def plot_data_spline_t(self, index, data, positionT):
        """
        Plot spline (parametric).

        Args:
            index (QModelIndex): index.
            data (dict): data list.
            positionT (numpy.ndarray): position (transformed).

        :meta private:
        """
        actor = data["name_actor"]
        point = data["point"]
        t_range = data["t_range"]
        width = float(data["width"])
        n_interp = int(data["n_interp"])
        closed = data["closed_check"]
        natural = data["natural_check"]
        arrow1 = data["arrow1_check"]
        arrow2 = data["arrow2_check"]
        tip_radius = float(data["tip R"])
        tip_length = float(data["tip length"])
        color = all_colors[data["color"]][0]
        transform = not data["cartesian_check"]
        opacity = float(data["opacity"])

        t_range = convert_str_vector(vector=t_range, transform=False)

        A = self.A_matrix if transform else np.eye(4)
        obj = create_spline_t(point, t_range, width, n_interp, closed, natural, arrow1, arrow2, tip_radius, tip_length, A)
        option_add = {"color": color, "opacity": opacity}

        option = self.common_option(actor=actor, positionT=positionT, obj=obj)
        option = option | option_add

        actor = self.add_mesh(**option)
        self.set_actor("spline_t", index, actor.name)
        self.clip_actor(data["position"], data["cell"], actor.name, data["label_actor"])

    # ==================================================
    def plot_data_caption(self, index, data, positionT):
        """
        Plot caption.

        Args:
            index (QModelIndex): index.
            data (dict): data list.
            positionT (numpy.ndarray): position (transformed).

        :meta private:
        """
        actor = data["name_actor"]
        margin = int(data["margin"])
        caption = text_to_list(data["caption"])
        size = int(data["size"])
        bold = data["bold_check"]
        color = all_colors[data["color"]][0]  # hex

        caption = [" " * margin + i for i in caption]

        option = {
            "points": positionT,
            "labels": caption,
            "font_size": size,
            "bold": bold,
            "text_color": color,
            "shape": None,
            "show_points": False,
            "always_visible": True,
        }

        if actor == "":
            actor = f"Actor2D(Counter={self._label_counter})"
            self._label_counter += 1

        actor = actor.replace("-labels", "")
        self.add_point_labels(name=actor, **option)
        self.set_actor("caption", index, actor + "-labels")
        # no implementation for clip_actor

    # ==================================================
    def plot_data_text2d(self, index, data, positionT):
        """
        Plot text 2d.

        Args:
            index (QModelIndex): index.
            data (dict): data list.
            positionT (numpy.ndarray): position (transformed).

        :meta private:
        """
        actor = data["name_actor"]
        position = data["position"]
        caption = data["caption"]
        size = int(data["size"])
        color = all_colors[data["color"]][0]  # hex
        font = data["font"]

        position = apply(float, text_to_list(position))[:2]

        option = {
            "position": position,
            "text": caption,
            "font_size": size,
            "color": color,
            "font": font,
            "viewport": True,
        }

        if actor == "":
            actor = f"Actor2D(Counter={self._label_counter})"
            self._label_counter += 1

        self.add_text(name=actor, **option)
        self.set_actor("text2d", index, actor)

    # ==================================================
    def plot_label(self, object_type, index, data, positionT):
        """
        Plot label.

        Args:
            object_type (str): object type.
            index (QModelIndex): index.
            data (dict): data list.
            positionT (numpy.ndarray): position (transformed).

        :meta private:
        """
        label = data["label"]
        actor = data["label_actor"]
        margin = int(data["margin"])

        option = self.label_option(positionT, label, margin)

        if actor == "":
            actor = f"Actor2D(Counter={self._label_counter})"
            self._label_counter += 1

        actor = actor.replace("-labels", "")
        self.add_point_labels(name=actor, **option)
        self.set_actor(object_type, index, actor + "-labels", COLUMN_LABEL_ACTOR)

    # ==================================================
    def set_isosurface_data(self, filename):
        """
        Set isosurface data.

        Args:
            filename (str): filename.

        Returns:
            - (str) -- valid file name.

        :meta private:
        """
        path_abs, path_rel, base, ext, folder = split_filename(filename)
        if os.path.exists(path_abs):
            if type(filename) != tuple:
                if ext == ".xsf":
                    grid_data = extract_data_xsf(path_abs)
                else:
                    grid_data = read_dict(path_abs)

            fname = path_rel
            self._isosurface_data[path_rel] = grid_data
        else:
            fname = ""

        return fname

    # ==================================================
    def plot_orbital_from_data(
        self,
        name,
        shape,
        surface=None,
        size=1.0,
        point_size=0.03,
        spherical_plot=False,
        color="coolwarm",
        opacity=1.0,
        position=None,
    ):
        """
        Plot orbital from data.

        Args:
            name (str): plot name.
            shape (ndarray): (x,y,z) orbital shape.
            surface (ndarray, optional): (x,y,z) orbital colormap.
            size (float, optional): orbital size.
            point_size(float, optional): point size.
            spherical_plot (bool, optional): spherical-like plot ?
            color (str, optional): orbital color or colormap.
            opacity (float, optional): opacity, [0,1].
            position (ndarray): position (transformed).

        Note:
            - if surface is None, the same one of shape is used.
            - if size is positive, max. value is equivalent to size.
            - if size is negative, abs. value is scaled by size.
            - if point_size is None, no point is shown.
            - to remove object, use remove_actor(name).
        """
        if position is None:
            position = np.zeros(3, dtype=float)

        obj = create_orbital_data(shape=shape, surface=surface, size=size, spherical_plot=spherical_plot, point_size=point_size)
        if check_color(color):
            option_add = {"color": all_colors[color][0], "opacity": opacity}
        else:
            scalars = "surface"
            if scalars in obj.array_names:
                clim = get_data_range(obj[scalars])
                option_add = {
                    "cmap": color.strip("*"),
                    "scalars": scalars,
                    "clim": clim,
                    "opacity": opacity,
                    "show_scalar_bar": False,
                }
            else:
                option_add = {
                    "cmap": color.strip("*"),
                    "opacity": opacity,
                    "show_scalar_bar": False,
                }

        option = self.common_option(actor=name, positionT=position, obj=obj)
        option = option | option_add

        self.add_mesh(**option)

    # ==================================================
    def plot_stream_from_data(
        self,
        name,
        vector,
        shape,
        surface=None,
        size=1.0,
        length=0.2,
        width=0.01,
        offset=-0.43,
        abs_scale=False,
        color="coolwarm",
        component="abs",
        spherical_plot=False,
        shaft_R=1.0,
        tip_R=2.0,
        tip_length=0.25,
        opacity=1.0,
        position=None,
    ):
        """
        Plot stream from data (vectors in cartesian coordinate).

        Args:
            name (str): object name.
            vector (ndarray): stream vector [vx(x,y,z),vy(x,y,z),vz(x,y,z)] (cartesina).
            shape (ndarray): f(x,y,z) shape on which stream put (cartesian).
            surface (ndarray, optional): (x,y,z) orbital colormap.
            size (float, optional): shape size.
            length (float, optional): stream arrow size.
            width (float, optional): stream arrow width.
            offset (float, optional): stream arrow offest.
            abs_scale (bool, optional): stream arrow scaled ?
            color (str, optional): stream arrow color or colormap.
            component (str, optional): use component or abs, "x/y/z/abs".
            spherical_plot (bool, optional): spherical-like plot ?
            shaft_R (float, optional) :shaft radius.
            tip_R (float, optional): tip radius.
            tip_length (float, optional): tip length.
            opacity (float, optional): opacity, [0,1].
            position (ndarray): position (transformed).

        Note:
            - if size is negative, shape is normalized.
            - to remove object, use remove_actor(name).
        """
        component_str = {"abs": None, "x": 0, "y": 1, "z": 2}

        if position is None:
            position = np.zeros(3, dtype=float)
        component = component_str[component]

        obj = create_stream_data(
            shape=shape,
            surface=surface,
            vector=vector,
            size=size,
            length=length,
            width=width,
            offset=offset,
            abs_scale=abs_scale,
            shaft_radius=shaft_R,
            tip_radius=tip_R,
            tip_length=tip_length,
            spherical_plot=spherical_plot,
        )

        if check_color(color):
            option_add = {
                "color": all_colors[color][0],
                "opacity": opacity,
            }
        else:
            scalars = "GlyphVector"
            if scalars in obj.array_names:
                clim = get_data_range(obj[scalars])
                option_add = {
                    "clim": clim,
                    "scalars": scalars,
                    "cmap": color.strip("*"),
                    "show_scalar_bar": False,
                    "component": component,
                    "opacity": opacity,
                }
            else:
                option_add = {
                    "cmap": color.strip("*"),
                    "show_scalar_bar": False,
                    "opacity": opacity,
                }

        option = self.common_option(actor=name, positionT=position, obj=obj)
        option = option | option_add

        self.add_mesh(**option)
