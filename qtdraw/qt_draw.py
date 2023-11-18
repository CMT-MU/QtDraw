"""
Qt Draw
"""
import os
from math import floor, ceil
import numpy as np
from qtpy.QtWidgets import QMessageBox, QFileDialog
from qtpy.uic import loadUi
import pyvista as pv
import pandas as pd
from gcoreutils.io_util import write_dict, read_dict
from gcoreutils.nsarray import NSArray
from gcoreutils.dataset import DataSet
from gcoreutils.crystal_util import cell_transform_matrix
from gcoreutils.latex_util import check_latex_installed, latex_cmd
from qtdraw.qt_draw_base import QtDrawBase
from qtdraw.core.setting import rcParams, preference
from qtdraw.core.util import (
    create_unit_cell,
    plot_axis,
    view_vectors,
    create_application,
)
from qtdraw.core.dialog_about import DialogAbout
from qtdraw.core.dialog_preference import DialogPreference
from qtdraw.core.line_edit import LineEditor
from qtdraw.core.group_tab import GroupTab
from qtdraw.core.basic_object import (
    create_sphere,
    create_bond,
    create_vector,
    create_orbital,
    create_stream_vector,
    create_plane,
    create_box,
    create_polygon,
    create_text,
    create_spline,
)
from qtdraw.core.color_palette import all_colors, custom_colormap, check_color
from qtdraw.parser.read_cif_vesta import plot_cif, plot_vesta
from qtdraw import __version__

from qtdraw.core.qt_logging import UncaughtHook

CHOP = 1e-5
qt_exception_hook = UncaughtHook()
global QT_EXCEPTION_HOOK
QT_EXCEPTION_HOOK = qt_exception_hook


# ==================================================
def to_chopped_list(a):
    a[np.abs(a) < CHOP] = 0.0
    return a.tolist()


# ==================================================
class QtDrawWidget(QtDrawBase):
    """
    QtDraw widget.
    """

    # ==================================================
    def __init__(
        self,
        title=None,
        model=None,
        cell=None,
        origin=None,
        view=None,
        size=None,
        axis_type=None,
        view_range=None,
        repeat=False,
        clip=True,
        cluster=False,
        background=False,
        parent=None,
    ):
        """
        initialize the class.

        Args:
            title (str, optional): window title of plotter.
            model (str, optioanl): name of model.
            cell (dict or str, optional): cell information (a/b/c/alpha/beta/gamma) or "hexagonal/trigonal".
            origin (list, optional): cell origin.
            view (list, optional): view with respect to the axes (a,b,c).
            size (list, optional): window size, (width, height).
            axis_type (str, optional): axis type, "xyz/abc/abc*".
            view_range (list, optional): display range ([x0,y0,z0],[x1,y1,z1]) (reduced).
            repeat (bool, optional): repeat plot ?
            clip (bool, optional): clip objects out of view_range ?
            cluster (bool, optional): cluster without repeat ?
            background (bool, optional): background run ?
            parent (QWidget, optional): parent.
        """
        self.preference = preference
        self.background = background
        # set qtdraw base.
        UI = os.path.dirname(__file__) + "/core/" + rcParams["plotter.ui"]
        UI = UI.replace(os.sep, "/")
        theme = rcParams["plotter.theme"]
        line = rcParams["detail.smooth.line"]
        point = rcParams["detail.smooth.point"]
        polygon = rcParams["detail.smooth.polygon"]
        shading = rcParams["detail.smooth.shading"]
        sample = rcParams["detail.smooth.samples"]
        super().__init__(
            parent=parent,
            panel=UI,
            theme=theme,
            smooth_line=line,
            smooth_point=point,
            smooth_polygon=polygon,
            smooth_shading=shading,
            sampling=sample,
        )

        # delete key event.
        for key in ["q", "b", "v", "C", "plus", "minus"]:
            self._layer.clear_events_for_key(key)

        # set anti aliasing.
        anti_aliasing = rcParams["detail.smooth.anti_aliasing"]
        self._set_anti_aliasing(anti_aliasing)

        # home folder.
        self._homedir = os.path.expanduser("~")
        os.chdir(self._homedir)

        # initialize.
        self._connect_slot()

        # set parameters.
        self._init_setting(
            title,
            model,
            cell,
            origin,
            view,
            size,
            axis_type,
            view_range,
            repeat,
            clip,
            cluster,
        )

        self._create_panel()
        self._init_all()
        self.set_view()

    # ==================================================
    def _init_all(self):
        self._init_dataset()
        self._init_counter()
        self._init_panel()
        self._set_light()
        self._init_actor()

    # ==================================================
    def _init_setting(
        self,
        title=None,
        model=None,
        cell=None,
        origin=None,
        view=None,
        size=None,
        axis_type=None,
        view_range=None,
        repeat=False,
        clip=True,
        cluster=False,
    ):
        """
        Notes:
            - setting dict.
                - title: str
                - model: str
                - cell: (dict) a, b, c, alpha, beta, gamma
                - origin: [float, float, float]
                - view: [int, int, int]
                - size: [int, int]
                - axis.type: str
                - view_range: [ [float,float,float], [float,float,float] ]
                - repeat: bool
                - clip: bool
                - cluster: bool
        """
        if title is None:
            title = rcParams["init.title"]
        if model is None:
            model = rcParams["init.model"]
        if origin is None:
            origin = rcParams["init.origin"]
        if view is None:
            view = rcParams["init.view"]
        if size is None:
            size = rcParams["init.size"]
        if axis_type is None:
            axis_type = self.preference["axis.type"]
        if view_range is None:
            view_range = rcParams["init.view_range"]

        cell = cell_transform_matrix(cell)[0]
        lower = NSArray(view_range[0], "vector", "value").tolist()
        upper = NSArray(view_range[1], "vector", "value").tolist()

        # set Plotter setting.
        self.setting = {}
        self.setting["title"] = str(title)
        self.setting["model"] = str(model)
        self.setting["cell"] = cell
        self.setting["origin"] = NSArray(origin, "vector", "value").tolist()
        self.setting["view"] = NSArray(view, "vector", "value").astype(int).tolist()
        self.setting["size"] = NSArray(size, "vector", "value").astype(int).tolist()
        self.preference["axis.type"] = str(axis_type)
        self.setting["view_range"] = [lower, upper]
        self.setting["repeat"] = bool(repeat)
        self.setting["clip"] = bool(clip)
        self.setting["cluster"] = bool(cluster)
        self.setting[
            "crystal"
        ] = ""  # triclinic, monoclinic, orthorhombic, tetragonal, trigonal, hexagonal, cubic

        self.setting["axis_mode"] = 0
        self.setting["cell_mode"] = 2 if self.setting["cluster"] else 0

    # ==================================================
    def _create_panel(self):
        # model.
        self.edit_model_o = LineEditor(
            validator="string", callback=self._set_model, parent=self
        )
        self.layout_model.replaceWidget(self.edit_model, self.edit_model_o)

        # origin.
        self.edit_origin_o = LineEditor(
            "Origin:",
            validator="r_vector",
            decimal=2,
            callback=self.set_origin,
            parent=self,
        )
        self.layout_cell.replaceWidget(self.edit_origin, self.edit_origin_o)

        # a, b, c, alpha, beta, gamma.
        self.edit_a_o = LineEditor(
            "a:", validator="real_positive", callback=self._set_a, parent=self
        )
        self.layout_cell.replaceWidget(self.edit_a, self.edit_a_o)
        self.edit_b_o = LineEditor(
            "b:", validator="real_positive", callback=self._set_b, parent=self
        )
        self.layout_cell.replaceWidget(self.edit_b, self.edit_b_o)
        self.edit_c_o = LineEditor(
            "c:", validator="real_positive", callback=self._set_c, parent=self
        )
        self.layout_cell.replaceWidget(self.edit_c, self.edit_c_o)
        self.edit_alpha_o = LineEditor(
            "α:",
            validator="real_positive",
            decimal=2,
            callback=self._set_alpha,
            parent=self,
        )
        self.layout_cell.replaceWidget(self.edit_alpha, self.edit_alpha_o)
        self.edit_beta_o = LineEditor(
            "β:",
            validator="real_positive",
            decimal=2,
            callback=self._set_beta,
            parent=self,
        )
        self.layout_cell.replaceWidget(self.edit_beta, self.edit_beta_o)
        self.edit_gamma_o = LineEditor(
            "γ:",
            validator="real_positive",
            decimal=2,
            callback=self._set_gamma,
            parent=self,
        )
        self.layout_cell.replaceWidget(self.edit_gamma, self.edit_gamma_o)

        # lower, upper.
        self.edit_lower_o = LineEditor(
            "lower:",
            validator="r_vector",
            decimal=2,
            callback=self._set_lower,
            parent=self,
        )
        self.layout_view.replaceWidget(self.edit_lower, self.edit_lower_o)
        self.edit_upper_o = LineEditor(
            "upper:",
            validator="r_vector",
            decimal=2,
            callback=self._set_upper,
            parent=self,
        )
        self.layout_view.replaceWidget(self.edit_upper, self.edit_upper_o)

        if self.setting["cluster"]:
            self.button_repeat.hide()

    # ==================================================
    def _set_light(self):
        if self.preference["light.eye_dome_lighting"]:
            self._layer.enable_eye_dome_lighting()
        else:
            self._layer.disable_eye_dome_lighting()
        self._layer.remove_all_lights()
        intensity = self.preference["light.intensity"]
        if self.preference["light.pbr"]:
            self._layer.add_light(pv.Light(light_type="headlight"))
            self._layer.add_light(pv.Light(light_type="headlight"))
        else:
            self._layer.add_light(pv.Light(light_type="headlight", intensity=0.55))
        self._layer.add_light(pv.Light(light_type="headlight", intensity=intensity))

    # ==================================================
    def _init_panel(self):
        # window size.
        self.set_window_size(*self.setting["size"])

        # axis object.
        self.button_object.setChecked(False)

        # set parallel projection.
        projection = rcParams["init.parallel_projection"]
        self.button_parallel.setChecked(projection)
        self._toggle_parallel_projection(projection)

        # repeat status.
        self.button_repeat.setChecked(self.setting["repeat"])

        # clip status.
        self.button_clip.setChecked(self.setting["clip"])

        # set grid.
        self._grid_actor = self._layer.show_grid()
        grid_status = rcParams["init.grid"]
        self.button_grid.setChecked(grid_status)
        self._toggle_grid(grid_status)

        self._set_model(self.setting["model"])
        self.set_range(self.setting["view_range"])
        self.set_origin(self.setting["origin"])
        self.set_crystal(self.setting["crystal"])

        self._change_axis(self.setting["axis_mode"])
        self._change_cell(self.setting["cell_mode"])

    # ==================================================
    def _load_plus_panel(self, fname, current=None):
        if current is None:
            current = ""
        else:
            current = current.replace(os.sep, "/")
            current = current[: current.rfind("/")]

        loadUi(current + "/" + fname, self.plus_panel)
        self._set_plus_panel()

    # ==================================================
    def set_crystal(self, crystal):
        """
        set crystal.

        Args:
            crystal (str): crystal, "triclinic/monoclinic/orthorhombic/tetragonal/trigonal/hexagonal/cubic".
        """
        if crystal == "monoclinic":
            ro = [False, False, False, True, False, True]
        elif crystal == "orthorhombic":
            ro = [False, False, False, True, True, True]
        elif crystal in ["tetragonal", "trigonal", "hexagonal"]:
            ro = [False, True, False, True, True, True]
        elif crystal == "cubic":
            ro = [False, True, True, True, True, True]
        elif crystal in ["", "triclinic"]:
            ro = [False, False, False, False, False, False]
            crystal = ""
        else:
            raise KeyError(f"{crystal} is invalid.")

        self.edit_a_o.editor.setReadOnly(ro[0])
        self.edit_b_o.editor.setReadOnly(ro[1])
        self.edit_c_o.editor.setReadOnly(ro[2])
        self.edit_alpha_o.editor.setReadOnly(ro[3])
        self.edit_beta_o.editor.setReadOnly(ro[4])
        self.edit_gamma_o.editor.setReadOnly(ro[5])
        self.setting["crystal"] = crystal
        self._set_axis_cell(self.setting["cell"])

    # ==================================================
    def set_range(self, view_range=None):
        """
        set display range.

        Args:
            view_range (list, optional): display range, [ [x0,y0,z0], [x1,y1,z1] ] (reduced).

        Notes:
            - if view_range is None, default, [[0,0,0],[1,1,1]] is used.
        """
        if view_range is None:
            view_range = ["[0.0,0.0,0.0]", "[1.0,1.0,1.0]"]

        if type(view_range) is not list:
            raise KeyError(f"{type(view_range)} is invalid.")

        lower, upper = view_range
        lower = NSArray(lower, "vector", "value").tolist()
        upper = NSArray(upper, "vector", "value").tolist()
        self.setting["view_range"] = [lower, upper]
        self.edit_lower_o.setText(str(lower))
        self.edit_upper_o.setText(str(upper))

        i1 = [floor(lower[0]), floor(lower[1]), floor(lower[2])]
        i2 = [ceil(upper[0]), ceil(upper[1]), ceil(upper[2])]
        dims = [i2[0] - i1[0], i2[1] - i1[1], i2[2] - i1[2]]

        self._ilower = i1
        self._dims = dims

        if dims[0] * dims[1] * dims[2] == 0:
            self._igrid = NSArray("[0,0,0]", fmt="value").astype(int).tolist()
        else:
            self._igrid = NSArray.igrid(dims, i1).value().astype(int).tolist()

        self._set_axis_cell(self.setting["cell"])

    # ==================================================
    def set_origin(self, origin=None):
        """
        set origin.

        Args:
            origin (list, optional): origin (reduced).

        Notes:
            - if origin is None, default, [0,0,0] is used.
        """
        if origin is None:
            origin = "[0,0,0]"

        origin = NSArray(origin, "vector", "value").tolist()
        self.setting["origin"] = origin
        self._set_axis_cell(self.setting["cell"])
        self.edit_origin_o.setText(str(origin))

    # ==================================================
    def set_view(self, view=None):
        """
        set view point.

        Args:
            view (list, optional): view point with respect to the axes (a,b,c)

        Notes:
            - if view is None, current view is used.
        """
        if view is None:
            view = self.setting["view"]
        else:
            view = NSArray(view, "vector", "value").astype(int).tolist()

        self.setting["view"] = view

        v, u = view_vectors(self._A_norm, view)
        if v is not None:
            a, b, c = view
            self.combo_a.setCurrentIndex(a + 9)
            self.combo_b.setCurrentIndex(b + 9)
            self.combo_c.setCurrentIndex(c + 9)
            self._layer.view_vector(v, u)

    # ==================================================
    def set_axis(self, mode):
        """
        set axis mode.

        Args:
            mode (str): mode, "on/only/off".
        """
        mode_idx = {"on": 0, "only": 1, "off": 2}

        if mode not in mode_idx.keys():
            return

        self._change_axis(mode_idx[mode])

    # ==================================================
    def set_cell(self, mode):
        """
        set cell mode.

        Args:
            mode (str): mode, "single/all/off".
        """
        mode_idx = {"single": 0, "all": 1, "off": 2}

        if mode not in mode_idx.keys():
            return

        self._change_cell(mode_idx[mode])

    # ==================================================
    def _regularize_position(self, position):
        if not isinstance(position, (str, list, np.ndarray)):
            raise KeyError(f"{type(position)} is invalid.")

        position = NSArray(position, "vector", "value")
        if position.lst:
            position = position.tolist()
        else:
            position = [position.tolist()]

        return position

    # ==================================================
    def plot_site(
        self,
        position,
        size=None,
        color=None,
        opacity=None,
        space=None,
        name=None,
        label="",
        show_lbl=False,
        cell=[0, 0, 0],
    ):
        """
        plot site.

        Args:
            position (str or list or ndarray or NSArray): position(s) to plot site (reduced).
            size (float, optional): size of site.
            color (str, optional): color of site.
            opacity (float, optional): opacity of site.
            space (int, optional): pre-space of label.
            name (str, optional): group name of object.
            label (str, optional): label of object.
            show_lbl (bool, optional): show label ?
            cell (list, optional): cell position.

        Notes:
            - if argument is None, default value is used.
        """
        position = self._regularize_position(position)

        if size is None:
            size = self.def_value["site"][5]
        if color is None:
            color = self.def_value["site"][6]
        if opacity is None:
            opacity = self.def_value["site"][7]
        if space is None:
            space = self.def_value["site"][8]

        if size < CHOP:
            return
        if space < 0:
            return

        info = [float(size), color, float(opacity), int(space)]
        self._plot_to_data("site", name, position, info, label, show_lbl, cell)

    # ==================================================
    def plot_bond(
        self,
        position,
        vector=None,
        width=None,
        color=None,
        color2="",
        opacity=None,
        space=None,
        name=None,
        label="",
        show_lbl=False,
        cell=[0, 0, 0],
    ):
        """
        plot bond.

        Args:
            position (str or list or ndarray or NSArray): position(s) to plot bond center (reduced).
            vector (str or list or ndarray or NSArray, optional): bond vector (reduced).
            width (float, optional): width of bond.
            color (str, optional): color of bond.
            color2 (str, optional): color of bond for half tail.
            opacity (float, optional): opacity of bond.
            space (int, optional): pre-space of label.
            name (str, optional): group name of object.
            label (str, optional): label of object.
            show_lbl (bool, optional): show label ?
            cell (list, optional): cell position.

        Notes:
            - if argument is None, default value is used.
            - if color2 is "", same color is used.
        """
        position = self._regularize_position(position)

        if vector is None:
            vector = self.def_value["bond"][5]
        if width is None:
            width = self.def_value["bond"][6]
        if color is None:
            color = self.def_value["bond"][7]
        if color2 is None:
            color2 = self.def_value["bond"][8]
        if opacity is None:
            opacity = self.def_value["bond"][9]
        if space is None:
            space = self.def_value["bond"][10]

        if space < 0:
            return

        if color2 == "":
            color2 = color

        v = NSArray(vector, "vector", "value")
        if v.norm() < CHOP or width < CHOP:
            return

        info = [
            to_chopped_list(v),
            float(width),
            color,
            color2,
            float(opacity),
            int(space),
        ]
        self._plot_to_data("bond", name, position, info, label, show_lbl, cell)

    # ==================================================
    def plot_vector(
        self,
        position,
        vector=None,
        length=None,
        width=None,
        offset=None,
        color=None,
        opacity=None,
        space=None,
        name=None,
        label="",
        show_lbl=False,
        cell=[0, 0, 0],
    ):
        """
        plot vector.

        Args:
            position (str or list or ndarray or NSArray): position(s) to plot vector (reduced).
            vector (str or list or ndarray or NSArray, optional): vector direction (cartesian).
            length (float, optional): length of vector.
            width (float, optional): width of vector.
            offset (float, optional): offset of vector end (ratio).
            color (str, optional): color of vector.
            opacity (float, optional): opacity of vector.
            space (int, optional): pre-space of label.
            name (str, optional): group name of object.
            label (str, optional): label of object.
            show_lbl (bool, optional): show label ?
            cell (list, optional): cell position.

        Notes:
            - if argument is None, default value is used.
            - vector is not necessary to be normalized.
        """
        position = self._regularize_position(position)

        if vector is None:
            vector = self.def_value["vector"][5]
        if length is None:
            length = self.def_value["vector"][6]
        if width is None:
            width = self.def_value["vector"][7]
        if offset is None:
            offset = self.def_value["vector"][8]
        if color is None:
            color = self.def_value["vector"][9]
        if opacity is None:
            opacity = self.def_value["vector"][10]
        if space is None:
            space = self.def_value["vector"][11]

        if space < 0:
            return

        v = NSArray(vector, "vector", "value")
        if v.norm() < CHOP or length < CHOP or width < CHOP:
            return

        info = [
            to_chopped_list(v),
            float(length),
            float(width),
            float(offset),
            color,
            float(opacity),
            int(space),
        ]
        self._plot_to_data("vector", name, position, info, label, show_lbl, cell)

    # ==================================================
    def plot_orbital(
        self,
        position,
        shape=None,
        surface="",
        size=None,
        theta_range=None,
        phi_range=None,
        color=None,
        opacity=None,
        space=None,
        scale=True,
        name=None,
        label="",
        show_lbl=False,
        cell=[0, 0, 0],
    ):
        """
        plot orbital.

        Args:
            position (str or list or ndarray or NSArray): position(s) to plot orbital (reduced).
            shape (str, optional): (x,y,z) shape of orbital in terms of (x,y,z) (cartesian).
            surface (str, optional): surface color in terms of (x,y,z) (cartesian).
            size (float, optional): size of orbital.
            theta_range (str or list or ndarray or NSArray, optional): theta range, default=[0,180].
            phi_range (str or list or ndarray or NSArray, optional): phi range, default=[0,360].
            color (str, optional): color/colormap of surface.
            opacity (float, optional): opacity of orbital.
            space (int, optional): pre-space of label.
            scale (bool, optional): if False, absolute size is used.
            name (str, optional): group name of object.
            label (str, optional): label of object.
            show_lbl (bool, optional): show label ?
            cell (list, optional): cell position.

        Notes:
            - if surface is "", surface is same as shape.
            - if argument is None, default value is used.
        """
        position = self._regularize_position(position)

        if shape is None:
            shape = self.def_value["orbital"][5]
        if surface is None:
            surface = self.def_value["orbital"][6]
        if size is None:
            size = self.def_value["orbital"][7]
        if scale is None:
            scale = self.def_value["orbital"][8]
        if theta_range is None:
            theta_range = [self.def_value["orbital"][9], self.def_value["orbital"][10]]
        if phi_range is None:
            phi_range = [self.def_value["orbital"][11], self.def_value["orbital"][12]]
        if color is None:
            color = self.def_value["orbital"][13]
        if opacity is None:
            opacity = self.def_value["orbital"][14]
        if space is None:
            space = self.def_value["orbital"][15]

        if size < CHOP:
            return

        if space < 0:
            return

        if type(shape) is not str:
            shape = str(shape)
        if surface == "":
            surface = shape
        if type(surface) is not str:
            surface = str(surface)

        theta_range = NSArray(theta_range, "vector", "value").tolist()
        phi_range = NSArray(phi_range, "vector", "value").tolist()

        info = [
            shape,
            surface,
            float(size),
            bool(scale),
            int(theta_range[0]),
            int(theta_range[1]),
            int(phi_range[0]),
            int(phi_range[1]),
            color,
            float(opacity),
            int(space),
        ]
        self._plot_to_data("orbital", name, position, info, label, show_lbl, cell)

    # ==================================================
    def plot_stream_vector(
        self,
        position,
        shape=None,
        vector=None,
        size=None,
        v_size=None,
        width=None,
        scale=None,
        theta=None,
        phi=None,
        theta_range=None,
        phi_range=None,
        color=None,
        component=None,
        opacity=None,
        space=None,
        name=None,
        label="",
        show_lbl=False,
        cell=[0, 0, 0],
    ):
        """
        plot stream vector with center orbital.

        Args:
            position (str or list or ndarray or NSArray): position(s) to plot stream vector (reduced).
            shape (str, optional): shape of center orbital in terms of (x,y,z) (cartesian).
            vector (str or list or ndarray or NSArray, optional): vector components in terms of (x,y,z) [str]/str (cartesian).
            size (float, optional): size of orbital.
            v_size (float, optional): ratio of vector size to orbital.
            width (float, optional): width of vector.
            scale (bool, optional): scale vector size by value ?
            theta (int, optional): resolution in theta direction.
            phi (int, optional): resolution in phi direction.
            theta_range (str or list or ndarray or NSArray, optional): theta range, default=[0,180].
            phi_range (str or list or ndarray or NSArray, optional): phi range, default=[0,360].
            color (str, optional): color of vector.
            component (int, optional): component of vector to use for colormap (0,1,2,None = x,y,z,abs.).
            opacity (float, optional): opacity of center orbital.
            space (int, optional): pre-space of label.
            name (str, optional): group name of object.
            label (str, optional): label of object.
            show_lbl (bool, optional): show label ?
            cell (list, optional): cell position.

        Notes:
            - if shape is None, "1" is used.
            - if argument is None, default value is used.
        """
        position = self._regularize_position(position)

        if shape is None:
            shape = self.def_value["stream"][5]
        if vector is None:
            vector = self.def_value["stream"][6]
        if size is None:
            size = self.def_value["stream"][7]
        if v_size is None:
            v_size = self.def_value["stream"][8]
        if width is None:
            width = self.def_value["stream"][9]
        if scale is None:
            scale = self.def_value["stream"][10]
        if theta is None:
            theta = self.def_value["stream"][11]
        if phi is None:
            phi = self.def_value["stream"][12]
        if theta_range is None:
            theta_range = [self.def_value["stream"][13], self.def_value["stream"][14]]
        if phi_range is None:
            phi_range = [self.def_value["stream"][15], self.def_value["stream"][16]]
        if color is None:
            color = self.def_value["stream"][17]
        if component is None:
            component = self.def_value["stream"][18]
        if opacity is None:
            opacity = self.def_value["stream"][19]
        if space is None:
            space = self.def_value["stream"][20]

        if space < 0:
            return

        if type(shape) is not str:
            shape = str(shape)

        vector = NSArray(vector, "vector").str()
        theta_range = NSArray(theta_range, "vector", "value").tolist()
        phi_range = NSArray(phi_range, "vector", "value").tolist()

        info = [
            shape,
            vector,
            float(size),
            float(v_size),
            float(width),
            bool(scale),
            int(theta),
            int(phi),
            int(theta_range[0]),
            int(theta_range[1]),
            int(phi_range[0]),
            int(phi_range[1]),
            color,
            component,
            float(opacity),
            int(space),
        ]
        self._plot_to_data("stream", name, position, info, label, show_lbl, cell)

    # ==================================================
    def plot_plane(
        self,
        position,
        normal=None,
        x=None,
        y=None,
        color=None,
        opacity=None,
        space=None,
        name=None,
        label="",
        show_lbl=False,
        cell=[0, 0, 0],
    ):
        """
        plot plane.

        Args:
            position (str or list or ndarray or NSArray): position(s) to plot plane (reduced).
            normal (str or list or ndarray or NSArray, optional): normal vector of plane (reduced).
            x (float, optional): x size of plane.
            y (float, optional); y size of plane.
            color (str, optional): color of plane.
            opacity (float, optional): opacity of plane.
            space (int, optional): pre-space of label.
            name (str, optional): group name of object.
            label (str, optional): label of object.
            show_lbl (bool, optional): show label ?
            cell (list, optional): cell position.

        Notes:
            - position is for center of plane.
            - if argument is None, default value is used.
            - normal is not necessary to be normalized.
        """
        position = self._regularize_position(position)

        if normal is None:
            normal = self.def_value["plane"][5]
        if x is None:
            x = self.def_value["plane"][6]
        if y is None:
            y = self.def_value["plane"][7]
        if color is None:
            color = self.def_value["plane"][8]
        if opacity is None:
            opacity = self.def_value["plane"][9]
        if space is None:
            space = self.def_value["plane"][10]

        if space < 0:
            return

        v = NSArray(normal, "vector", "value")
        if v.norm() < CHOP or x < CHOP or y < CHOP:
            return

        info = [
            to_chopped_list(v),
            float(x),
            float(y),
            color,
            float(opacity),
            int(space),
        ]
        self._plot_to_data("plane", name, position, info, label, show_lbl, cell)

    # ==================================================
    def plot_box(
        self,
        position,
        a1=None,
        a2=None,
        a3=None,
        edge=None,
        wireframe=None,
        width=None,
        color=None,
        opacity=None,
        space=None,
        name=None,
        label="",
        show_lbl=False,
        cell=[0, 0, 0],
    ):
        """
        plot box.

        Args:
            position (str or list or ndarray or NSArray): position(s) to plot box (reduced).
            a1 (str or list or ndarray or NSArray, optional): 1st direction of box (reduced).
            a2 (str or list or ndarray or NSArray, optional): 2nd direction of box (reduced).
            a3 (str or list or ndarray or NSArray, optional): 3rd direction of box (reduced).
            edge (bool, optional): show edge of box ?
            wireframe (bool, optional): draw box by wireframe ?
            width (float, optional): line width of box for wireframe plot.
            color (str, optional): color of box.
            opacity (float, optional): opacity of box.
            space (int, optional): pre-space of label.
            name (str, optional): group name of object.
            label (str, optional): label of object.
            show_lbl (bool, optional): show label ?
            cell (list, optional): cell position.

        Notes:
            - if argument is None, default value is used.
        """
        position = self._regularize_position(position)

        if a1 is None:
            a1 = self.def_value["box"][5]
        if a2 is None:
            a2 = self.def_value["box"][6]
        if a3 is None:
            a3 = self.def_value["box"][7]
        if edge is None:
            edge = self.def_value["box"][8]
        if wireframe is None:
            wireframe = self.def_value["box"][9]
        if width is None:
            width = self.def_value["box"][10]
        if color is None:
            color = self.def_value["box"][11]
        if opacity is None:
            opacity = self.def_value["box"][12]
        if space is None:
            space = self.def_value["box"][13]

        if space < 0:
            return

        a1 = NSArray(a1, "vector", "value")
        a2 = NSArray(a2, "vector", "value")
        a3 = NSArray(a3, "vector", "value")
        if a1.norm() < CHOP or a2.norm() < CHOP or a3.norm() < CHOP or width < CHOP:
            return

        info = [
            to_chopped_list(a1),
            to_chopped_list(a2),
            to_chopped_list(a3),
            bool(edge),
            bool(wireframe),
            float(width),
            color,
            float(opacity),
            int(space),
        ]
        self._plot_to_data("box", name, position, info, label, show_lbl, cell)

    # ==================================================
    def plot_polygon(
        self,
        position,
        point=None,
        connection=None,
        edge=None,
        wireframe=None,
        width=None,
        color=None,
        opacity=None,
        space=None,
        name=None,
        label="",
        show_lbl=False,
        cell=[0, 0, 0],
    ):
        """
        plot polygon.

        Args:
            position (str or list or ndarray or NSArray): position(s) to plot polygon (reduced).
            point (str or list or ndarray or NSArray, optional): vertices of polygon (reduced).
            connection (str or list or ndarray or NSArray, optional): list of connected vectices for each plane.
            edge (bool, optional): show edge of box ?
            wireframe (bool, optional): draw box by wireframe ?
            width (float, optional): line width of box for wireframe plot.
            color (str, optional): color of box.
            opacity (float, optional): opacity of box.
            space (int, optional): pre-space of label.
            name (str, optional): group name of object.
            label (str, optional): label of object.
            show_lbl (bool, optional): show label ?
            cell (list, optional): cell position.

        Notes:
            - if argument is None, default value is used.
        """
        position = self._regularize_position(position)

        if point is None:
            point = self.def_value["polygon"][5]
        if connection is None:
            connection = self.def_value["polygon"][6]
        if edge is None:
            edge = self.def_value["polygon"][7]
        if wireframe is None:
            wireframe = self.def_value["polygon"][8]
        if width is None:
            width = self.def_value["polygon"][9]
        if color is None:
            color = self.def_value["polygon"][10]
        if opacity is None:
            opacity = self.def_value["polygon"][11]
        if space is None:
            space = self.def_value["polygon"][12]

        if space < 0:
            return

        point = to_chopped_list(NSArray(point, "vector", "value"))
        connection = NSArray(connection, "vector", "value").astype(int).tolist()

        info = [
            point,
            connection,
            bool(edge),
            bool(wireframe),
            float(width),
            color,
            float(opacity),
            int(space),
        ]
        self._plot_to_data("polygon", name, position, info, label, show_lbl, cell)

    # ==================================================
    def plot_text3d(
        self,
        position,
        text=None,
        size=None,
        depth=None,
        normal=None,
        offset=None,
        color=None,
        opacity=None,
        space=None,
        name=None,
        label="",
        show_lbl=False,
        cell=[0, 0, 0],
    ):
        """
        plot 3d text.

        Args:
            position (str or list or ndarray or NSArray): position(s) to plot 3d text (reduced).
            text (str, optional): text.
            size (float, optional): size of text.
            depth (float, optional): depth of text.
            normal (str or list or ndarray or NSArray, optional): normal vector of text (reduced).
            offset (str or list or ndarray or NSArray, optional): offset of text.
            color (str, optional): color of text.
            opacity (float, optional): opacity of text.
            space (int, optional): pre-space of label.
            name (str, optional): group name of object.
            label (str, optional): label of object.
            show_lbl (bool, optional): show label ?
            cell (list, optional): cell position.

        Notes:
            - if argument is None, default value is used.
            - normal is not necessary to be normalized.
        """
        position = self._regularize_position(position)

        if text is None:
            text = self.def_value["text3d"][5]
        if size is None:
            size = self.def_value["text3d"][6]
        if depth is None:
            depth = self.def_value["text3d"][7]
        if normal is None:
            normal = self.def_value["text3d"][8]
        if offset is None:
            offset = self.def_value["text3d"][9]
        if color is None:
            color = self.def_value["text3d"][10]
        if opacity is None:
            opacity = self.def_value["text3d"][11]
        if space is None:
            space = self.def_value["text3d"][12]

        if space < 0:
            return

        if text == "" or size < CHOP:
            return
        n = NSArray(normal, "vector", "value")
        if n.norm() < CHOP:
            return

        offset = to_chopped_list(NSArray(offset, "vector", "value"))

        info = [
            text,
            float(size),
            float(depth),
            to_chopped_list(n),
            offset,
            color,
            float(opacity),
            int(space),
        ]
        self._plot_to_data("text3d", name, position, info, label, show_lbl, cell)

    # ==================================================
    def plot_spline(
        self,
        position,
        point=None,
        width=None,
        n_interp=None,
        closed=None,
        natural=None,
        color=None,
        opacity=None,
        space=None,
        name=None,
        label="",
        show_lbl=False,
        cell=[0, 0, 0],
    ):
        """
        plot spline curve.

        Args:
            position (str or list or ndarray or NSArray): position(s) to plot spline curve (reduced).
            point (str or list or ndarray or NSArray, optional): points to be interpolated (reduced).
            width (float, optioanl): width of spline curve.
            n_interp (int, optional): number of interpolation points.
            closed (bool, optional): closed spline ?
            natural (bool, optional): natural boundary ?
            color (str, optional): color of spline curve.
            opacity (float, optional): opacity of spline curve.
            space (int, optional): pre-space of label.
            name (str, optional): group name of object.
            label (str, optional): label of object.
            show_lbl (bool, optional): show label ?
            cell (list, optional): cell position.

        Notes:
            - if argument is None, default value is used.
        """
        position = self._regularize_position(position)

        if point is None:
            point = self.def_value["spline"][5]
        if width is None:
            width = self.def_value["spline"][6]
        if n_interp is None:
            n_interp = self.def_value["spline"][7]
        if closed is None:
            closed = self.def_value["spline"][8]
        if natural is None:
            natural = self.def_value["spline"][9]
        if color is None:
            color = self.def_value["spline"][10]
        if opacity is None:
            opacity = self.def_value["spline"][11]
        if space is None:
            space = self.def_value["spline"][12]

        if width < CHOP:
            return

        if space < 0:
            return

        point = to_chopped_list(NSArray(point, "vector", "value"))

        info = [
            point,
            float(width),
            int(n_interp),
            bool(closed),
            bool(natural),
            color,
            float(opacity),
            int(space),
        ]
        self._plot_to_data("spline", name, position, info, label, show_lbl, cell)

    # ==================================================
    def plot_spline_t(
        self,
        position,
        expression=None,
        t_range=None,
        width=None,
        n_interp=None,
        closed=None,
        natural=None,
        color=None,
        opacity=None,
        space=None,
        name=None,
        label="",
        show_lbl=False,
        cell=[0, 0, 0],
    ):
        """
        plot spline curve.

        Args:
            position (str or list or ndarray or NSArray): position(s) to plot spline curve (reduced).
            expression (str or list or ndarray or NSArray, optional): component function of "t" to create interpolated points (reduced).
            t_range (str or list or ndarray or NSArray, optional): range of "t", [start, stop, step].
            width (float, optioanl): width of spline curve.
            n_interp (int, optional): number of interpolation points.
            closed (bool, optional): closed spline ?
            natural (bool, optional): natural boundary ?
            color (str, optional): color of spline curve.
            opacity (float, optional): opacity of spline curve.
            space (int, optional): pre-space of label.
            name (str, optional): group name of object.
            label (str, optional): label of object.
            show_lbl (bool, optional): show label ?
            cell (list, optional): cell position.

        Notes:
            - if argument is None, default value is used.
        """
        position = self._regularize_position(position)

        if expression is None:
            expression = self.def_value["spline_t"][5]
        if t_range is None:
            t_range = self.def_value["spline_t"][6]
        if width is None:
            width = self.def_value["spline_t"][7]
        if n_interp is None:
            n_interp = self.def_value["spline_t"][8]
        if closed is None:
            closed = self.def_value["spline_t"][9]
        if natural is None:
            natural = self.def_value["spline_t"][10]
        if color is None:
            color = self.def_value["spline_t"][11]
        if opacity is None:
            opacity = self.def_value["spline_t"][12]
        if space is None:
            space = self.def_value["spline_t"][13]

        if width < CHOP:
            return

        if space < 0:
            return

        expression = NSArray(expression, "vector").str()
        t_range = to_chopped_list(NSArray(t_range, "vector", "value"))

        info = [
            expression,
            t_range,
            float(width),
            int(n_interp),
            bool(closed),
            bool(natural),
            color,
            float(opacity),
            int(space),
        ]
        self._plot_to_data("spline_t", name, position, info, label, show_lbl, cell)

    # ==================================================
    def plot_caption(
        self,
        position,
        caption=None,
        space=None,
        size=None,
        color=None,
        bold=None,
        name=None,
        cell=[0, 0, 0],
    ):
        """
        plot caption.

        Args:
            position (str or list or ndarray or NSArray): position(s) to plot labels (reduced).
            caption (str or list, optional): label or list of labels.
            space (int, optional): pre-space of label.
            size (int, optional): font size.
            color (str, optional): text color.
            bold (bool, optional): bold face ?
            name (str, optional): group name.
            cell (list, optional): cell position.

        Notes:
            - if caption is None, simple number is used.
            - if argument is None, default value is used.
            - list size of caption must be equal to that of position.
        """
        position = self._regularize_position(position)

        if caption is None:
            caption = [str(i) for i in range(len(position))]
        if space is None:
            space = self.def_value["caption"][4]
        if size is None:
            size = self.def_value["caption"][5]
        if color is None:
            color = self.def_value["caption"][6]
        if bold is None:
            bold = self.def_value["caption"][7]

        if space < 0:
            return

        if type(caption) == str:
            caption = [caption] * len(position)

        if len(position) != len(caption):
            return

        info = [caption, int(space), int(size), bool(bold), color]
        self._plot_to_data("caption", name, position, info, cell=cell)

    # ==================================================
    def plot_text(
        self,
        position,
        caption=None,
        relative=None,
        size=None,
        color=None,
        font=None,
        name=None,
    ):
        """
        plot text.

        Args:
            position (str or list or ndarray or NSArray): position to plot caption, [x,y].
            caption (str, optional): label.
            relative (bool, optional): relative position ?
            size (int, optional): font size.
            color (str, optional): text color.
            font (str, optional): font, "arial/times/courier".
            name (str, optional): group name.

        Notes:
            - if argument is None, default value is used.
        """
        position = self._regularize_position(position)[0]

        if relative is None:
            relative = self.def_value["text"][2]
        if caption is None:
            caption = self.def_value["text"][3]
        if size is None:
            size = self.def_value["text"][4]
        if color is None:
            color = self.def_value["text"][5]
        if font is None:
            font = self.def_value["text"][6]

        info = [relative, caption, int(size), color, font]
        self._plot_to_data("text", name, position, info)

    # ==================================================
    def show(self):
        """
        show the plot.

        Notes:
            - this must be called at the end of plots.
        """
        self._plot_all_object()
        if not self.background:
            super().show()

    # ==================================================
    def _connect_slot(self):
        self.button_x.clicked.connect(self._view_x)
        self.button_y.clicked.connect(self._view_y)
        self.button_z.clicked.connect(self._view_z)
        self.button_default.clicked.connect(self._view_d)
        self.button_screenshot.clicked.connect(lambda _: self._screenshot())
        self.button_list.clicked.connect(self._view_dataset)
        self.button_clear.clicked.connect(self._clear)
        self.button_load.clicked.connect(self._load)
        self.button_save.clicked.connect(self._save)

        self.button_repeat.toggled["bool"].connect(self._toggle_repeat)
        self.button_clip.toggled["bool"].connect(self._toggle_clip)
        self.button_parallel.toggled["bool"].connect(self._toggle_parallel_projection)
        self.button_grid.toggled["bool"].connect(self._toggle_grid)
        self.button_object.toggled["bool"].connect(self._toggle_axis_object)

        self.combo_a.currentIndexChanged["int"].connect(self._change_a)
        self.combo_b.currentIndexChanged["int"].connect(self._change_b)
        self.combo_c.currentIndexChanged["int"].connect(self._change_c)
        self.combo_axis.currentIndexChanged["int"].connect(self._change_axis)
        self.combo_cell.currentIndexChanged["int"].connect(self._change_cell)

        self.button_preference.clicked.connect(self._set_preference)
        self.button_about.clicked.connect(self._about)

        try:
            from multipie import __version__

            self.button_multipie.clicked.connect(self._multipie)
            self._multipie_loaded = __version__
        except ImportError:
            self._multipie_loaded = False
            self.button_multipie.hide()

    # ==================================================
    def _init_dataset(self):
        # dataset panel status.
        self._dialog_dataset = False

        # dataset.
        self.dataset = DataSet(rcParams["detail.dataset.property"])

        # default value.
        self.def_value = {
            group: [
                self.dataset.role[group][i][-1]
                for i in range(len(self.dataset.role[group]))
            ]
            for group in self.dataset.keys()
        }

    # ==================================================
    def _init_counter(self):
        # init counter.
        self._counter = {i: 0 for i in self.dataset.keys()}

    # ==================================================
    def _init_actor(self):
        self._actorset = {}
        self._counter["actor"] = 0
        self._spotlight_actor = []

    # ==================================================
    def _set_model(self, model):
        self.setting["model"] = model
        title = self.setting["title"]
        self.set_window_title(f"{title} - {model}")
        self.edit_model_o.setText(model)

    # ==================================================
    def _set_axis_cell(self, cell=None):
        """
        Notes:
            - assume origin and range (ilower and dims) are already set.
        """
        if cell is None:
            cell = {}

        cell, self._volume, self._A, self._G, self._A_norm = cell_transform_matrix(
            cell, crystal=self.setting["crystal"]
        )
        origin = self.setting["origin"]

        self.setting["cell"] = cell

        # set axis.
        self._draw_axis()

        # set volume.
        self.label_volume.setText(f"Volume: {self._volume:.6f}")

        # set cell.
        self.uc = create_unit_cell(self._A, origin, self._ilower, self._dims)
        self._draw_cell()

        self.edit_a_o.setText(str(self.setting["cell"]["a"]))
        self.edit_b_o.setText(str(self.setting["cell"]["b"]))
        self.edit_c_o.setText(str(self.setting["cell"]["c"]))
        self.edit_alpha_o.setText(str(self.setting["cell"]["alpha"]))
        self.edit_beta_o.setText(str(self.setting["cell"]["beta"]))
        self.edit_gamma_o.setText(str(self.setting["cell"]["gamma"]))

    # ==================================================
    def _draw_axis(self, mode=None):
        if mode is None:
            mode = self.combo_axis.currentIndex()

        self._screen_off()
        self._axis_actor = plot_axis(
            self._layer,
            self._A_norm,
            rcParams["detail.axis.label"][self.preference["axis.type"]],
            size=self.preference["axis.size"],
            bold=self.preference["axis.bold"],
            italic=self.preference["axis.italic"],
            position=self.preference["axis.position"],
        )
        self._axis_actor[2].SetVisibility(False)
        self._change_axis(mode)
        self._screen_on()

    # ==================================================
    def _draw_cell(self, mode=None):
        if mode is None:
            mode = self.combo_cell.currentIndex()

        self._screen_off()
        cell_actor = self._layer.add_mesh(
            self.uc[0],
            line_width=self.preference["cell.width"],
            color=all_colors[self.preference["cell.color"]][0],  # hex
            opacity=self.preference["cell.opacity"],
            smooth_shading=self.shading,
            name="uc",
        )

        if self.uc[1].n_points > 0:
            cell_actor1 = self._layer.add_mesh(
                self.uc[1],
                line_width=self.preference["cell.width"],
                color=all_colors[self.preference["cell.color"]][0],  # hex
                opacity=self.preference["cell.opacity"],
                smooth_shading=self.shading,
                name="uc1",
            )
        else:
            cell_actor1 = None

        self._cell_actor = [cell_actor, cell_actor1]
        self._change_cell(mode)
        self._screen_on()

    # ==================================================
    def _set_lower(self, lower):
        self.set_range([lower, self.setting["view_range"][1]])
        self._set_repeat()

    # ==================================================
    def _set_upper(self, upper):
        self.set_range([self.setting["view_range"][0], upper])
        self._set_repeat()

    # ==================================================
    def _set_a(self, a):
        self.setting["cell"]["a"] = float(a)
        self._set_axis_cell(self.setting["cell"])
        self._plot_all_object()

    # ==================================================
    def _set_b(self, b):
        self.setting["cell"]["b"] = float(b)
        self._set_axis_cell(self.setting["cell"])
        self._plot_all_object()

    # ==================================================
    def _set_c(self, c):
        self.setting["cell"]["c"] = float(c)
        self._set_axis_cell(self.setting["cell"])
        self._plot_all_object()

    # ==================================================
    def _set_alpha(self, alpha):
        self.setting["cell"]["alpha"] = float(alpha)
        self._set_axis_cell(self.setting["cell"])
        self._plot_all_object()

    # ==================================================
    def _set_beta(self, beta):
        self.setting["cell"]["beta"] = float(beta)
        self._set_axis_cell(self.setting["cell"])
        self._plot_all_object()

    # ==================================================
    def _set_gamma(self, gamma):
        self.setting["cell"]["gamma"] = float(gamma)
        self._set_axis_cell(self.setting["cell"])
        self._plot_all_object()

    # ==================================================
    def _toggle_repeat(self, flag):
        self.setting["repeat"] = flag
        self._close_dialog()
        self._repeat_data()
        if self.setting["repeat"]:
            self._change_cell(1)
        else:
            self._change_cell(0)

    # ==================================================
    def _toggle_clip(self, flag):
        self.setting["clip"] = flag
        self._plot_all_object()

    # ==================================================
    def _view_x(self):
        self.set_view([1, 0, 0])

    # ==================================================
    def _view_y(self):
        self.set_view([0, 1, 0])

    # ==================================================
    def _view_z(self):
        self.set_view([0, 0, 1])

    # ==================================================
    def _view_d(self):
        self.set_view(rcParams["init.view"])

    # ==================================================
    def _toggle_grid(self, flag):
        self._grid_actor.SetVisibility(flag)

    # ==================================================
    def _change_a(self, val):
        _, b, c = self.setting["view"]
        self.set_view([val - 9, b, c])

    # ==================================================
    def _change_b(self, val):
        a, _, c = self.setting["view"]
        self.set_view([a, val - 9, c])

    # ==================================================
    def _change_c(self, val):
        a, b, _ = self.setting["view"]
        self.set_view([a, b, val - 9])

    # ==================================================
    def _toggle_parallel_projection(self, flag):
        self._set_parallel_projection(flag)

    # ==================================================
    def _change_axis(self, val):
        ax = {0: (True, True), 1: (True, False), 2: (False, False)}

        show = ax[val]
        self._axis_actor[0].SetEnabled(show[0])
        self._axis_actor[1].SetEnabled(show[1])
        self.combo_axis.setCurrentIndex(val)

    # ==================================================
    def _toggle_axis_object(self, flag):
        self._axis_actor[2].SetVisibility(flag)
        if flag:
            self.axis_vis = self.combo_axis.currentIndex()
            self.cell_vis = self.combo_cell.currentIndex()
            self._hide_all_object()
            self._change_axis(2)
            self._change_cell(2)
        else:
            self._change_axis(self.axis_vis)
            self._change_cell(self.cell_vis)
            self._show_all_object()

    # ==================================================
    def _change_cell(self, val):
        uc = {0: (True, False), 1: (False, True), 2: (False, False)}
        self._cell_actor[0].SetVisibility(uc[val][0])
        if self._cell_actor[1] is not None:
            self._cell_actor[1].SetVisibility(uc[val][1])
        self.combo_cell.setCurrentIndex(val)

    # ==================================================
    def _set_repeat(self, repeat=None):
        if repeat is None:
            repeat = self.setting["repeat"]

        self._toggle_repeat(repeat)

    # ==================================================
    def _set_clip(self, clip=None):
        if clip is None:
            clip = self.setting["clip"]

        self._toggle_clip(clip)

    # ==================================================
    def _close_dialog(self):
        if self._dialog_dataset:
            self.tab.close()
            self._dialog_dataset = False
            self.set_status("")
            self._garbage_collection()

    # ==================================================
    def _view_dataset(self):
        def spot(n, r):
            if n != "caption":
                self._plot_spotlight(n, r)

        if not self._dialog_dataset:
            self._dialog_dataset = True
            self.tab = GroupTab(
                ds=self.dataset, title="DataSet - " + self.setting["model"], parent=self
            )
            self.tab.rawDataChanged.connect(self._plot_object)
            self.tab.textMessage.connect(self.set_status)
            self.tab.selectedData.connect(spot)
            self.tab.deselectedData.connect(self._remove_spotlight)
            self.tab.finished["int"].connect(self._close_dialog)
            self.tab.show()

    # ==================================================
    def _load(self):
        default_ext = rcParams["plotter.ext"]
        loadable_ext = rcParams["plotter.cif"] + " " + rcParams["plotter.vesta"]
        default_file = os.getcwd()
        ext_str = default_ext + " " + loadable_ext
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Load QtDraw",
            default_file,
            "QtDraw file (" + ext_str.replace(".", "*.") + ")",
        )
        if filename:
            _, ext = os.path.splitext(filename)
            if ext == "":
                ext = default_ext
                filename += ext
            if ext in ext_str.split(" "):
                self._close_dialog()
                self._load_file(filename, ext)
                self.set_status(f"loaded {filename}.")
            else:
                self.set_status(f"{ext} is unsupported, use {default_ext}.")

    # ==================================================
    def _load_file(self, filename, ext):
        self._homedir = os.path.dirname(filename)
        os.chdir(self._homedir)

        if ext == rcParams["plotter.cif"]:
            plot_cif(self, filename)
            return
        elif ext == rcParams["plotter.vesta"]:
            plot_vesta(self, filename)
            return

        load_dict = read_dict(filename)

        self.preference = load_dict["preference"]
        self.setting = load_dict["setting"]
        self._remove_all_actor()
        self._init_all()
        self.set_view()

        if self.setting["cluster"]:
            self.button_repeat.hide()

        for key in self.dataset.keys():
            if key in load_dict.keys():
                for item in load_dict[key]:
                    self.dataset.append(key, item)

        for key in rcParams["detail.dataset.property"].keys():
            self._counter[key] = len(set(self.dataset[key].iloc[:, 0]))

        self._plot_all_object()
        self._layer.set_viewup(self.setting["camera.up"])
        self._layer.set_focus(self.setting["camera.focus"])
        self._layer.set_position(self.setting["camera.position"], reset=True)

        if "multipie" in load_dict.keys():
            if not hasattr(self, "group_panel"):
                self._multipie()
            self.group_panel.load_dict(load_dict["multipie"])

    # ==================================================
    def _save(self):
        default_ext = rcParams["plotter.ext"]
        default_file = os.getcwd() + "/" + self.setting["model"] + default_ext
        default_file = default_file.replace(os.sep, "/")
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save QtDraw", default_file, "QtDraw file (*" + default_ext + ")"
        )
        if filename:
            _, ext = os.path.splitext(filename)
            if ext == "":
                ext = default_ext
                filename += ext
            if ext == default_ext:
                self._close_dialog()
                self._save_file(filename)
                self._homedir = os.path.dirname(filename)
                os.chdir(self._homedir)
                self.set_status(f"saved: {filename}.")
            else:
                self.set_status(f"{ext} is unsupported, use {default_ext}.")

    # ==================================================
    def create_dict(self, name):
        """
        create model dict for save.

        Args:
            name (str): model name.

        Returns:
            dict: model dict for save.
        """
        self._set_model(name)
        self.setting["axis_mode"] = self.combo_axis.currentIndex()
        self.setting["cell_mode"] = self.combo_cell.currentIndex()
        self.setting["camera.position"] = self._layer.camera.position
        self.setting["camera.up"] = self._layer.camera.up
        self.setting["camera.focus"] = self._layer.camera.focal_point

        save_dict = {
            "version": __version__,
            "setting": self.setting,
            "preference": self.preference,
        }

        self._garbage_collection()

        for key, df in self.dataset.items():
            df0 = df.copy()
            if key in ["caption", "text"]:
                df0.loc[:, "AD"] = ""
            else:
                df0.loc[:, "AD"] = ""
                df0.loc[:, "AL"] = ""
            save_dict[key] = df0.to_dict(orient="split")["data"]

        if hasattr(self, "group_panel"):
            save_dict["multipie"] = self.group_panel.save_dict()

        return save_dict

    # ==================================================
    def _save_file(self, filename):
        base = os.path.splitext(os.path.basename(filename))[0]
        save_dict = self.create_dict(base)
        write_dict(filename, save_dict, "\nQtDraw data file in Python dict format.\n")

    # ==================================================
    def _clear(self):
        ret = QMessageBox.question(
            self, "", "Are you sure ?", QMessageBox.Ok, QMessageBox.Cancel
        )
        if ret == QMessageBox.Ok:
            self._close_dialog()
            self._remove_all_actor()
            self._init_dataset()
            self._init_counter()
            self._init_actor()
            self._init_setting(
                title=self.setting["title"],
                size=self.setting["size"],
                axis_type=self.preference["axis.type"],
                clip=self.setting["clip"],
                cluster=self.setting["cluster"],
            )
            self._init_panel()
            self._set_light()
            self.set_view()
            self.set_status("removed all objects.")

    # ==================================================
    def _garbage_collection(self):
        for df in self.dataset.values():
            idx = df.index[df.iloc[:, 0] == ""]
            df.drop(idx, inplace=True)
            df.reset_index(drop=True, inplace=True)

    # ==================================================
    def _actor_id(self):
        c = self._counter["actor"]
        s = f"L{c}"
        self._counter["actor"] = c + 1

        return s

    # ==================================================
    def _show_actor(self, name, show):
        self._actorset[name].SetVisibility(show)

    # ==================================================
    def _remove_actor(self, name):
        self._screen_off()
        if name in self._actorset.keys():
            obj_actor = self._actorset[name]
            self._layer.remove_actor(obj_actor)
            del self._actorset[name]
        self._screen_on()

    # ==================================================
    def _remove_all_actor(self):
        names = list(self._actorset.keys())
        for name in names:
            self._remove_actor(name)

    # ==================================================
    def _get_name(self, name):
        c = self._counter[name]
        s = f"{self.def_value[name][0]}{c}"
        self._counter[name] = c + 1
        return s

    # ==================================================
    def _hide_all_object(self):
        """
        hide all object.
        """
        for i in self._actorset.values():
            i.SetVisibility(False)

    # ==================================================
    def _show_all_object(self):
        """
        show all object.
        """
        for group in self.dataset.keys():
            for row_idx in range(len(self.dataset[group])):
                self._show_object(group, row_idx)

    # ==================================================
    def _show_object(self, group, row_idx):
        """
        show object.

        Args:
            group (str): type of object.
            row_idx (int): row index of dataframe to show.
        """
        row = self.dataset[group].iloc[row_idx, :]

        if row[0] == "":
            return

        if group in ["caption", "text"]:
            obj_show, obj_id = row[-2:]
        else:
            obj_show, obj_id, lbl_id = row[-3:]
            lbl_show = row[1]
            self._show_actor(lbl_id, lbl_show)
        self._show_actor(obj_id, obj_show)

    # ==================================================
    def _plot_spotlight(self, group, row_idx):
        size = self.preference["spotlight.size"]
        size *= self._volume ** (1 / 3)
        opt = {
            "color": all_colors[self.preference["spotlight.color"]][0],  # hex
            "opacity": self.preference["spotlight.opacity"],
            "smooth_shading": self.shading,
            "name": f"spotlight_{row_idx}",
        }
        if group == "text":
            return

        th_phi = (rcParams["plot.orbital.theta"], rcParams["plot.orbital.phi"])

        cell = self.dataset[group].loc[row_idx, "cell"]
        position = self.dataset[group].loc[row_idx, "position"]
        cell = NSArray(cell, "vector", "value").astype(int)
        position = NSArray(position, "vector", "value")
        pos = (cell + position).transform(self._A)
        obj = create_sphere(size, th_phi, (0, 180), (0, 360)).translate(
            pos, inplace=True
        )
        actor = self._layer.add_mesh(obj, **opt)
        self._spotlight_actor.append((actor, group, row_idx))

    # ==================================================
    def _replot_spotlight(self):
        sp = self._spotlight_actor.copy()
        self._spotlight_actor = []
        for i in sp:
            self._plot_spotlight(i[1], i[2])

    # ==================================================
    def _remove_spotlight(self):
        for i in self._spotlight_actor:
            self._layer.remove_actor(i[0])
        self._spotlight_actor = []

    # ==================================================
    def _plot_to_data(
        self, group, name, position, info, label="", show_lbl=False, cell=[0, 0, 0]
    ):
        """
        store plot data.

        Args:
            group (str): type of object.
            name (str): name of object.
            position (list): position of object (reduced), [x, y, z].
            info (list): other options such as size, opacity etc.
            label (str, optional): label of object.
            show_lbl (bool, optional): show label ?
            cell (list, optional): cell position.
        """
        if name is None:  # default name.
            name = self._get_name(group)

        if type(cell) == str:
            cell = NSArray(cell).tolist()

        if group == "caption":
            info1 = [name, cell, position] + info + [True, ""]
            self.dataset.append(group, info1)
        elif group == "text":
            info1 = [name, position] + info + [True, ""]
            self.dataset.append(group, info1)
        else:
            if label == "":
                label = name
            for i in position:
                info1 = [name, show_lbl, label, cell, i] + info + [True, "", ""]
                self.dataset.append(group, info1)

    # ==================================================
    def _plot_all_object(self):
        """
        plot all object.
        """
        for group in self.dataset.keys():
            for row_idx in range(len(self.dataset[group])):
                self._plot_object(group, row_idx)

    # ==================================================
    def _plot_object(self, group, row_idx):
        """
        plot object.

        Args:
            group (str): type of object.
            row_idx (int): row index of dataframe to plot.
        """
        row = self.dataset[group].iloc[row_idx, :]

        if row[0] == "":
            if group in ["caption", "text"]:
                obj_id = row[-1]
            else:
                obj_id, lbl_id = row[-2:]
            if obj_id != "":
                self._remove_actor(obj_id)
            if group not in ["caption", "text"] and lbl_id != "":
                self._remove_actor(lbl_id)
            return

        self._screen_off()
        if group == "caption":
            opt, obj_id, obj_show = self._data_to_object(group, row)
            if obj_id == "":
                obj_id = self._actor_id()
                self.dataset[group].iat[row_idx, -1] = obj_id
            obj_actor = self._layer.add_point_labels(name=obj_id, **opt)
            self._actorset[obj_id] = obj_actor
            self._show_actor(obj_id, obj_show)
        elif group == "text":
            opt, obj_id, obj_show = self._data_to_object(group, row)
            if obj_id == "":
                obj_id = self._actor_id()
                self.dataset[group].iat[row_idx, -1] = obj_id
            obj_actor = self._layer.add_text(name=obj_id, **opt)
            self._actorset[obj_id] = obj_actor
            self._show_actor(obj_id, obj_show)
        else:
            opt, obj_id, obj_show, lbl_opt, lbl_id, lbl_show = self._data_to_object(
                group, row
            )
            if obj_id == "":
                obj_id = self._actor_id()
                self.dataset[group].iat[row_idx, -2] = obj_id
            obj_actor = self._layer.add_mesh(name=obj_id, **opt)
            self._actorset[obj_id] = obj_actor
            self._show_actor(obj_id, obj_show)

            if lbl_id == "":
                lbl_id = self._actor_id()
                self.dataset[group].iat[row_idx, -1] = lbl_id
            lbl_actor = self._layer.add_point_labels(name=lbl_id, **lbl_opt)
            self._actorset[lbl_id] = lbl_actor
            self._show_actor(lbl_id, lbl_show)
        self._screen_on()

    # ==================================================
    def _check_in_view_range(self, obj):
        """
        check if object is in view range.

        Args:
            obj (NSArray): object.

        Returns:
            bool: True if in range.
        """
        if not self.setting["clip"]:
            return True

        sft = NSArray("[0.001,0.001,0.001]", "vector", "value")
        lower, upper = self.setting["view_range"]
        lower = (NSArray(lower, "vector", "value") - sft).tolist()
        upper = (NSArray(upper, "vector", "value") + sft).tolist()
        idx = obj.clip(lower, upper)

        return len(idx) > 0

    # ==================================================
    def _data_to_object(self, group, row):
        """
        convert string data to object.

        Args:
            group (str): type of object.
            row (list): row of data frame.

        Returns: tuple:
            - (option, object_ID, object_show) for caption and text.
            - (option, object_ID, object_show, label_option, label_ID, label_show) for others.
        """
        if group == "caption":
            igrid, position = row[1:3]
            info = row[3:-2]
            obj_show, obj_id = row[-2:]
        elif group == "text":
            position = eval(str(row[1]))
            info = row[2:-2]
            obj_show, obj_id = row[-2:]
        else:
            label, igrid, position = row[2:5]
            info = row[5:-3]
            obj_show, obj_id, lbl_id = row[-3:]
            lbl_show = row[1]

        if group == "text":
            position = NSArray(position, "scalar", "value")
        else:
            igrid = NSArray(igrid, "vector", "value").astype(int)
            t = f"[[1,0,0,{igrid[0]}],[0,1,0,{igrid[1]}],[0,0,1,{igrid[2]}],[0,0,0,1]]"
            t = NSArray(t, "matrix", "value")
            position = NSArray(position, "vector", "value")
            pos = position.transform(t)
            pos = pos.transform(self._A)

        if group == "caption":
            caption, space, size, bold, color = info
            space = int(space)
            size = int(size)
            bold = bool(bold)
            color = all_colors[color][0]  # hex

            caption = [" " * space + i for i in caption]

            opt = {
                "points": pos.numpy(),
                "labels": caption,
                "font_size": size,
                "bold": bold,
                "text_color": color,
                "shape": None,
                "show_points": False,
                "always_visible": True,
            }

            return opt, obj_id, obj_show

        if group == "text":
            relative, caption, size, color, font = info
            size = int(size)
            color = all_colors[color][0]  # hex
            font = rcParams["detail.dataset.property"]["text"][1][6][1][int(font)]
            relative = bool(relative)

            opt = {
                "position": position.numpy(),
                "text": caption,
                "font_size": size,
                "color": color,
                "font": font,
                "viewport": relative,
            }

            return opt, obj_id, obj_show

        if not self._check_in_view_range(igrid + position):
            obj_show = False
            lbl_show = False

        if group == "site":
            size, color, opacity, space = info
            size = float(size)
            opacity = float(opacity)
            space = int(space)
            color = all_colors[color][0]  # hex

            th_phi = (rcParams["plot.orbital.theta"], rcParams["plot.orbital.phi"])

            obj = create_sphere(0.07 * size, th_phi, (0, 180), (0, 360))
            opt = {"color": color, "opacity": opacity}

        elif group == "bond":
            v, width, color, color2, opacity, space = info
            v = NSArray(v, "vector", "value")
            vec = v.transform(self._A)
            width = float(width)
            opacity = float(opacity)
            space = int(space)

            if color2 != color:
                obj = create_bond(vec, width, True)
                cmap = custom_colormap([color, color2])
                opt = {"show_scalar_bar": False, "cmap": cmap, "opacity": opacity}
            else:
                obj = create_bond(vec, width, False)
                opt = {"color": all_colors[color][0], "opacity": opacity}

            if not (
                self._check_in_view_range(igrid + position - v / 2)
                and self._check_in_view_range(igrid + position + v / 2)
            ):
                obj_show = False
                lbl_show = False

        elif group == "vector":
            v, length, width, offset, color, opacity, space = info
            v = NSArray(v, "vector", "value")
            length = float(length)
            width = float(width)
            offset = float(offset)
            color = all_colors[color][0]  # hex
            opacity = float(opacity)
            space = int(space)

            tip_l = self.preference["vector.tip.length"]
            shaft_r = self.preference["vector.shaft.radius"]
            tip_r = self.preference["vector.tip.radius"]

            obj = create_vector(v, length, width, offset, tip_l, shaft_r, tip_r)
            opt = {"color": color, "opacity": opacity}

        elif group == "orbital":
            (
                shape,
                surface,
                size,
                scale,
                th0,
                th1,
                phi0,
                phi1,
                color,
                opacity,
                space,
            ) = info
            size = float(size)
            scale = bool(scale)
            opacity = float(opacity)
            space = int(space)
            th_range = [int(th0), int(th1)]
            phi_range = [int(phi0), int(phi1)]

            th_phi = (rcParams["plot.orbital.theta"], rcParams["plot.orbital.phi"])

            obj = create_orbital(
                shape, surface, size, th_phi, scale, th_range, phi_range
            )
            if check_color(color):
                opt = {"color": all_colors[color][0], "opacity": opacity}
            else:
                opt = {
                    "cmap": color.strip("*"),
                    "scalars": "surface",
                    "clim": [-1, 1],
                    "opacity": opacity,
                    "show_scalar_bar": False,
                }

        elif group == "stream":
            (
                shape,
                vector,
                size,
                v_size,
                width,
                scale,
                theta,
                phi,
                th0,
                th1,
                phi0,
                phi1,
                color,
                component,
                opacity,
                space,
            ) = info
            size = float(size)
            v_size = float(v_size)
            width = float(width)
            scale = bool(scale)
            theta = int(theta)
            phi = int(phi)
            th_range = [int(th0), int(th1)]
            phi_range = [int(phi0), int(phi1)]
            if component == 3:
                component = None
            opacity = float(opacity)
            space = int(space)

            tip_l = self.preference["vector.tip.length"]
            shaft_r = self.preference["vector.shaft.radius"]
            tip_r = self.preference["vector.tip.radius"]

            v = create_stream_vector(
                shape, vector, size, (theta, phi), th_range, phi_range
            )
            g = create_vector("[1, 0, 0]", 1.0, width, -0.43, tip_l, shaft_r, tip_r)
            if scale:
                obj = v.glyph(
                    orient="vector", scale="vector_abs", factor=v_size, geom=g
                )
            else:
                obj = v.glyph(orient="vector", scale=None, factor=v_size, geom=g)

            if check_color(color):
                opt = {
                    "clim": [-1, 1],
                    "color": all_colors[color][0],
                    "opacity": opacity,
                }
            else:
                opt = {
                    "clim": [-1, 1],
                    "scalars": "GlyphVector",
                    "cmap": color.strip("*"),
                    "show_scalar_bar": False,
                    "component": component,
                    "opacity": opacity,
                }

        elif group == "plane":
            v, x, y, color, opacity, space = info
            v = NSArray(v, "vector", "value")
            vec = v.transform(self._A)
            x = float(x)
            y = float(y)
            color = all_colors[color][0]  # hex
            opacity = float(opacity)
            space = int(space)
            obj = create_plane(vec, x, y)
            opt = {"color": color, "opacity": opacity}

        elif group == "box":
            a1, a2, a3, edge, wireframe, width, color, opacity, space = info
            a1 = NSArray(a1, "vector", "value")
            a2 = NSArray(a2, "vector", "value")
            a3 = NSArray(a3, "vector", "value")
            a1A = a1.transform(self._A)
            a2A = a2.transform(self._A)
            a3A = a3.transform(self._A)
            edge = bool(edge)
            wireframe = bool(wireframe)
            width = float(width)
            color = all_colors[color][0]  # hex
            opacity = float(opacity)
            space = int(space)
            obj = create_box(a1A, a2A, a3A)
            if wireframe:
                opt = {
                    "color": color,
                    "opacity": opacity,
                    "style": "wireframe",
                    "line_width": width,
                }
            else:
                opt = {
                    "color": color,
                    "opacity": opacity,
                    "show_edges": edge,
                    "line_width": width,
                }

        elif group == "polygon":
            point, cnt, edge, wireframe, width, color, opacity, space = info
            point = NSArray(point, "vector", "value")
            pointA = point.transform(self._A)
            edge = bool(edge)
            wireframe = bool(wireframe)
            width = float(width)
            color = all_colors[color][0]  # hex
            opacity = float(opacity)
            space = int(space)
            obj = create_polygon(pointA, cnt)
            if wireframe:
                opt = {
                    "color": color,
                    "opacity": opacity,
                    "style": "wireframe",
                    "line_width": width,
                }
            else:
                opt = {
                    "color": color,
                    "opacity": opacity,
                    "show_edges": edge,
                    "line_width": width,
                }

        elif group == "text3d":
            text, size, depth, n, offset, color, opacity, space = info
            size = float(size)
            depth = float(depth)
            n = NSArray(n, "vector", "value")
            offset = NSArray(offset, "vector", "value")
            color = all_colors[color][0]  # hex
            opacity = float(opacity)
            space = int(space)
            obj = create_text(text, 0.04 * size, n, self._A_norm, offset, 0.3 * depth)
            opt = {"color": color, "opacity": opacity}

        elif group == "spline":
            point, width, n_interp, closed, natural, color, opacity, space = info
            point = NSArray(point, "vector", "value")
            pointA = point.transform(self._A)
            width = float(width)
            n_interp = int(n_interp)
            closed = bool(closed)
            natural = bool(natural)
            color = all_colors[color][0]
            opacity = float(opacity)
            space = int(space)
            obj = create_spline(pointA, n_interp, width, closed, natural)
            opt = {"color": color, "opacity": opacity}

        elif group == "spline_t":
            (
                expression,
                t_range,
                width,
                n_interp,
                closed,
                natural,
                color,
                opacity,
                space,
            ) = info
            expression = NSArray(expression, "vector")
            t_range = NSArray(t_range, "vector", "value")
            f = expression.lambdify()
            tp = np.arange(t_range[0], t_range[1], t_range[2])
            point = f(tp)
            pointA = point.transform(self._A)
            width = float(width)
            n_interp = int(n_interp)
            closed = bool(closed)
            natural = bool(natural)
            color = all_colors[color][0]
            opacity = float(opacity)
            space = int(space)
            obj = create_spline(pointA, n_interp, width, closed, natural)
            opt = {"color": color, "opacity": opacity}

        else:
            raise ValueError(f"unknown group {group} is given.")

        pos = (igrid + position).transform(self._A)
        g = obj.copy()
        g = g.translate(pos, inplace=True)
        opt["mesh"] = g
        opt["smooth_shading"] = self.shading

        opt["pbr"] = self.preference["light.pbr"]
        opt["metallic"] = self.preference["light.metallic"]
        opt["roughness"] = self.preference["light.roughness"]

        lbl_opt = {
            "points": pos.numpy(),
            "labels": [" " * space + label],
            "font_family": self.preference["label.font"],
            "font_size": self.preference["label.size"],
            "bold": self.preference["label.bold"],
            "italic": self.preference["label.italic"],
            "text_color": all_colors[self.preference["label.color"]][0],
            "shape": None,
            "show_points": False,
            "always_visible": True,
        }
        return opt, obj_id, obj_show, lbl_opt, lbl_id, lbl_show

    # ==================================================
    def _repeat_data(self):
        # create single cell.
        dataset0 = {}
        for group, df in self.dataset.items():
            if len(df) > 0:
                if group != "text":
                    df0 = (
                        df[df["cell"].apply(lambda x: str(x)) == "[0, 0, 0]"]
                        .copy()
                        .reset_index(drop=True)
                    )
                    for i in range(len(df0)):
                        df0.at[i, "cell"] = [0, 0, 0]
                else:
                    df0 = df.copy()
                if group in ["caption", "text"]:
                    df0.loc[:, "AD"] = ""
                else:
                    df0.loc[:, "AD"] = ""
                    df0.loc[:, "AL"] = ""
                dataset0[group] = df0
        self._remove_all_actor()
        self._init_dataset()
        self._init_actor()

        # repeat cells.
        if self.setting["repeat"]:
            for group, df in dataset0.items():
                if group == "text":
                    self.dataset[group] = df.reset_index(drop=True)
                else:
                    for grid in self._igrid:
                        df0 = df.reset_index(drop=True)
                        for i in range(len(df0)):
                            df0.at[i, "cell"] = grid
                        self.dataset[group] = pd.concat(
                            [self.dataset[group], df0], ignore_index=True, axis=0
                        )
        else:
            for group, df in dataset0.items():
                self.dataset[group] = df.reset_index(drop=True)

        self._plot_all_object()

        if self.setting["repeat"]:
            self.set_status("repeated all objects.")
        else:
            self.set_status("unrepeated all objects.")

    # ==================================================
    def _set_preference(self):
        def apply():
            self._set_light()
            self.set_crystal(self.setting["crystal"])
            self._draw_axis()
            self._draw_cell()
            self._plot_all_object()
            self._replot_spotlight()

        preference = DialogPreference(self.preference, self.setting, apply, self)
        preference.show()

    # ==================================================
    def _about(self):
        about = DialogAbout(self)
        about.exec()

    # ==================================================
    def _multipie(self):
        """
        MultiPie extension.
        """
        from multipie import get_binary

        self.button_clear.hide()
        self.button_multipie.hide()
        self.layout_dataset.removeWidget(self.button_clear)
        self.preference["axis.type"] = "abc"
        self._draw_axis()
        self._core = get_binary(load=True)
        self._create_group_panel()

    # ==================================================
    def _create_group_panel(self):
        from qtdraw.multipie.dialog_group import DialogGroup

        self.group_panel = DialogGroup(core=self._core, qtdraw=self, parent=self)
        self.group_panel.force_close = False
        self.group_panel.show()

    # ==================================================
    def closeEvent(self, event):
        if self.background:
            self.close()
            return
        ret = QMessageBox.question(
            self, "", "Quit QtDraw ?", QMessageBox.Ok, QMessageBox.Cancel
        )
        if ret != QMessageBox.Ok:
            event.ignore()
        else:
            if hasattr(self, "group_panel"):
                self.group_panel.force_close = True
                self.group_panel.close()
            self.close()

    # ==================================================
    def close(self):
        super().close()


# ==================================================
class QtDraw(QtDrawWidget):
    """
    Draw application.
    """

    # ==================================================
    def __init__(
        self,
        title=None,
        model=None,
        cell=None,
        origin=None,
        view=None,
        size=None,
        axis_type=None,
        view_range=None,
        repeat=False,
        clip=True,
        cluster=False,
        background=False,
        filename=None,
    ):
        """
        initialize the class.

        Args:
            title (str, optional): window title of plotter.
            model (str, optioanl): name of model.
            cell (dict or str, optional): cell information or "hexagonal/trigonal".
            origin (list, optional): cell origin.
            view (list, optional): view with respect to the axes (a,b,c).
            size (tuple, optional): window size, (width, height).
            axis_type (str, optional): axis type, "xyz/abc/abc*".
            view_range (list, optional): display range ([x0,y0,z0],[x1,y1,z1]) (reduced).
            repeat (bool, optional): repeat plot ?
            clip (bool, optional): clip objects out of view_range ?
            cluster (bool, optional): cluster without repeat ?
            background (bool, optional): background run ?
            filename (str, optional): if not None, load filename.
        """
        style = rcParams["plotter.style"]
        font = rcParams["plotter.font.family"]
        font_size = rcParams["plotter.font.size"]
        self.app = create_application(style=style, font=font, font_size=font_size)
        super().__init__(
            title,
            model,
            cell,
            origin,
            view,
            size,
            axis_type,
            view_range,
            repeat,
            clip,
            cluster,
            background,
        )
        if not check_latex_installed():
            QMessageBox.critical(
                None,
                "Error",
                f"LaTeX command, '{latex_cmd}', cannot be found.",
                QMessageBox.Yes,
            )
            exit()
        if filename is not None and os.path.isfile(filename):
            _, ext = os.path.splitext(filename)
            self._load_file(filename, ext)
            self.set_status(f"loaded {filename}.")

    # ==================================================
    def show(self):
        """
        show the plot.
        """
        super().show()
        self.app.exec()
        del self.app


# ==================================================
class QtMultiDraw(dict):
    """
    MultiPlotter application.
    """

    # ==================================================
    def __init__(
        self,
        n=1,
        title=None,
        model=None,
        cell=None,
        origin=None,
        view=None,
        size=None,
        axis_type=None,
        view_range=None,
        repeat=None,
        clip=None,
        cluster=None,
        background=None,
    ):
        """
        initialize the class.

        Args:
            n (int, optional): number of plotters.
            title ([str], optional): window title of each plotter.
            model ([str], optioanl): name of model of each plotter.
            cell ([dict or str], optional): cell information or "hexagonal/trigonal" of each plotter.
            origin ([list], optional): cell origin of each plotter.
            view ([list], optional): view with respect to the axes (a,b,c) of each plotter.
            size ([tuple], optional): window size, (width, height) of each plotter.
            axis_type ([str], optional): axis type, "xyz/abc/abc*" of each plotter.
            view_range ([list], optional): display range ([x0,y0,z0],[x1,y1,z1]) (reduced) of each plotter.
            repeat ([bool], optional): repeat plot of each plotter ?
            clip (bool, optional): clip objects out of view_range ?
            cluster (bool, optional): cluster without repeat ?
            background (bool, optional): background run ?

        Notes:
            - number of list content must be equal to n.
        """
        style = rcParams["plotter.style"]
        font = rcParams["plotter.font.family"]
        font_size = rcParams["plotter.font.size"]
        self.app = create_application(style=style, font=font, font_size=font_size)
        if not check_latex_installed():
            QMessageBox.critical(
                None,
                "Error",
                f"LaTeX command, '{latex_cmd}', cannot be found.",
                QMessageBox.Yes,
            )
            exit()

        if title is None:
            t = rcParams["init.title"]
            title = [f"{t} {i}" for i in range(n)]
        if model is None:
            model = [f"untitled_{i}" for i in range(n)]
        if cell is None:
            cell = [None] * n
        if origin is None:
            origin = [None] * n
        if view is None:
            view = [None] * n
        if size is None:
            size = [None] * n
        if axis_type is None:
            axis_type = [None] * n
        if view_range is None:
            view_range = [None] * n
        if repeat is None:
            repeat = [False] * n
        if clip is None:
            clip = [True] * n
        if cluster is None:
            cluster = [False] * n
        if background is None:
            background = [False] * n

        for i in range(n):
            self[i] = QtDrawWidget(
                title=title[i],
                model=model[i],
                cell=cell[i],
                origin=origin[i],
                view=view[i],
                size=size[i],
                axis_type=axis_type[i],
                view_range=view_range[i],
                repeat=repeat[i],
                clip=clip[i],
                cluster=cluster[i],
                background=background[i],
            )

    # ==================================================
    def show(self):
        """
        show all plotter.
        """
        for p in self.values():
            p.show()
        self.app.exec()
        del self.app
