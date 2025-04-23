"""
Multipie plugin.

This module provides MultiPie plugin.
"""

import logging
import numpy as np
import sympy as sp
from gcoreutils.nsarray import NSArray
from multipie import __version__, get_binary
from multipie.const import __def_dict__
from multipie.tag.tag_group import TagGroup
from multipie.group.point_group import PointGroup
from multipie.group.space_group import SpaceGroup
from qtdraw.multipie.plugin_multipie_setting import plugin_detail as detail
from qtdraw.multipie.plugin_multipie_setting import default_status
from qtdraw.multipie.dialog_multipie import MultiPieDialog
from qtdraw.multipie.util import check_get_site_bond, check_get_site, check_get_bond, combined_format, create_samb_object


# ==================================================
def _mapping_str(mp):
    """
    Convert mapping No. to those start from one.

    Args:
        mp (list): mapping.

    Returns:
        - (list) -- converted mapping.
    """
    m = [i - 1 if i < 0 else i + 1 for i in mp]
    return str(m).replace(" ", "")


# ==================================================
class MultiPiePlugin:
    # ==================================================
    def __init__(self, parent):
        """
        MultiPie plugin.

        Args:
            parent (QWidget): parent.
        """
        self.parent = parent
        self._pvw = parent.pyvista_widget
        self._core = get_binary()

        multipie_status = default_status
        multipie_status["plus"] = {}
        for key, value in self._pvw._status["multipie"].items():
            if type(value) == dict:
                multipie_status[key].update(value)
        self._pvw._status["multipie"] = multipie_status
        self._pvw._status["multipie"]["version"] = self.version

        self._pvw.update_preference("label", "default_check", detail["general"]["label"])

        self.set_group()

        self.dialog = MultiPieDialog(self)
        self.dialog.show()

    # ==================================================
    @property
    def version(self):
        """
        Version.
        """
        return __version__

    # ==================================================
    @property
    def group(self):
        """
        Group status dict.
        """
        return self._pvw._status["multipie"]["group"]

    # ==================================================
    @property
    def obj(self):
        """
        Object status dict.
        """
        return self._pvw._status["multipie"]["object"]

    # ==================================================
    @property
    def basis(self):
        """
        Basis status dict.
        """
        return self._pvw._status["multipie"]["basis"]

    # ==================================================
    @property
    def plus(self):
        """
        Plus status dict.
        """
        return self._pvw._status["multipie"]["plus"]

    # ==================================================
    def counter(self, name):
        """
        Counter number and increment.

        Args:
            name (str): name of counter.

        Returns:
            - (int) -- counter.
        """
        n = self._pvw._status["multipie"]["counter"][name]
        self._pvw._status["multipie"]["counter"][name] = n + 1
        return n

    # ==================================================
    def clear_counter(self):
        """
        Clear counter.
        """
        for key in self._pvw._status["multipie"]["counter"].keys():
            self._pvw._status["multipie"]["counter"][key] = 0

    # ==================================================
    def set_group(self):
        """
        Set group and plus dict.
        """
        tag = TagGroup(self.group["group"])

        pg = tag.is_point_group()
        self.plus["point_group"] = pg
        if pg:
            self._group = PointGroup(tag, self._core)
            self._point_group = self._group
            self.plus["n_pset"] = 1
            self.plus["pset"] = "{[0,0,0]}"
        else:
            self._group = SpaceGroup(tag, self._core)
            self._point_group = self._group.pg
            self.plus["n_pset"] = len(self._group.symmetry_operation.plus_set)
            self.plus["pset"] = str(self._group.symmetry_operation.plus_set)

        self.plus["crystal"] = self._group.tag.crystal
        self.plus["wyckoff"] = list(map(str, self._point_group.wyckoff.keys()))[::-1]
        self.plus["irrep"] = list(map(str, self._point_group.character.irrep_list))
        self.plus["n_op"] = len(self._group.symmetry_operation)

        # for old QtDraw version.
        if type(self.group["irrep1"]) == int:
            self.group["irrep1"] = self.plus["irrep"][self.group["irrep1"]]
        if type(self.group["irrep2"]) == int:
            self.group["irrep2"] = self.plus["irrep"][self.group["irrep2"]]
        if type(self.group["irrep"]) == int:
            self.group["irrep"] = self.plus["irrep"][self.group["irrep"]]
        if type(self.group["vc_wyckoff"]) == int:
            self.group["vc_wyckoff"] = self.plus["wyckoff"][self.group["vc_wyckoff"]]

        # empty basis.
        self.plus["site_cluster"] = ""
        self.plus["site_z_samb"] = {}
        self.plus["site_c_samb"] = {}

        self.plus["bond_cluster"] = ""
        self.plus["bond_z_samb"] = {}
        self.plus["bond_c_samb"] = {}

        self.plus["vector_cluster"] = ""
        self.plus["vector_z_samb"] = {}
        self.plus["vector_c_samb"] = {}

        self.plus["orbital_cluster"] = ""
        self.plus["orbital_z_samb"] = {}
        self.plus["orbital_c_samb"] = {}

    # ==================================================
    def get_product_decomp(self, irrep1, irrep2, irrep):
        """
        Set product decomposition.

        Args:
            irrep1 (str): irrep1 for symmetric product.
            irrep2 (str): irrep2 for symmetric product.
            irrep (str): irerp for anti symmetric product.

        Returns:
            - (str) -- symmetric decomposition.
            - (str) -- anti symmetric decomposition.
        """

        def remove_latex(s):
            s = (
                s.replace("_{", "")
                .replace("}", "")
                .replace("^{", "")
                .replace(r"\prime", "'")
                .replace("(", "")
                .replace(")", "")
                .replace("0", "-")
            )
            return s

        s = self._point_group.character.symmetric_product_decomposition((irrep1, irrep2), ret_ex=True)
        a = self._point_group.character.anti_symmetric_product_decomposition(irrep, ret_ex=True)

        s = remove_latex(str(s))
        a = remove_latex(str(a))

        return s, a

    # ==================================================
    def get_harmonics_irrep(self):
        """
        Get harmonics irrep.

        Returns:
            - (list) -- harmonics name list.
        """
        h_type = self.obj["harmonics_type"]
        rank = self.obj["harmonics_rank"]
        h_type1 = h_type.replace("T", "Q").replace("M", "G")

        hs = self._point_group.harmonics.select(rank=rank, head=h_type1)
        lst = [h_type + str(i)[2:] for i in hs]

        return lst

    # ==================================================
    def get_harmonics(self):
        """
        Get harmonics.

        Returns:
            - (str) -- harmonics expression (in LaTeX).
        """
        h_type = self.obj["harmonics_type"]
        rank = self.obj["harmonics_rank"]
        irrep = self.obj["harmonics_irrep"]
        h_type = h_type.replace("T", "Q").replace("M", "G")
        hs = self._point_group.harmonics.select(rank=rank, head=h_type)
        h = hs[irrep]
        ex = h.expression(v=NSArray.vector3d("Q"))
        if self.obj["harmonics_latex"]:
            ex = ex.latex()
        else:
            ex = str(ex)

        return ex

    # ==================================================
    def find_wyckoff(self):
        """
        Find Wyckoff position.

        Returns:
            - (str) -- Wyckoff position.
            - (str) -- site symmetry.
        """
        wyckoff = self.obj["wyckoff"]
        r_site = check_get_site_bond(wyckoff, ret_site=True)
        if r_site is None:
            logging.error(f"cannot find Wyckoff position, {wyckoff}")
            return None, None

        wp = self._group.find_wyckoff_position(r_site)
        sym = self._group.wyckoff.site_symmetry(wp)
        wp = str(wp)

        return wp, sym

    # ==================================================
    def add_equivalent_site(self, site, scale=1.0, color=None):
        """
        Add equivalent sites.

        Args:
            site (str): representative site.
            scale (float, optional): size scale.
            color (str, optional): color.

        Returns:
            - (str) -- representative site.
        """
        n_pset = self.plus["n_pset"]
        r_site = check_get_site(site)
        if r_site is None:
            logging.error(f"format error, {site}")
            return None

        if self.plus["point_group"]:
            site = self._group.site_mapping(r_site)
        else:
            site = self._group.site_mapping(r_site, plus_set=True)

        count = self.counter("site") + 1
        name0 = f"S{count:02}"
        if color is None:
            color = detail["general"]["site_color"]
        size = detail["object"]["site_size"]
        primitive_num = len(site) // n_pset

        for no, (s, mp) in enumerate(site.items()):
            s = NSArray(s)
            mp = _mapping_str(mp)
            idx = no % primitive_num
            pset = no // primitive_num
            name = name0
            if n_pset > 1:
                name += f"({pset+1})"
            label = f"s{idx+1:02}:{mp}"
            self._pvw.add_site(position=s.value(), size=size * scale, color=color, name=name, label=label)

        return str(r_site)

    # ==================================================
    def add_equivalent_bond(self, bond, scale=1.0, color=None, color2=None):
        """
        Add equivalent bonds.

        Args:
            bond (str): representative bond.
            scale (float, optional): size scale.
            color (str, optional): color.
            color2 (str, optional): color2.

        Returns:
            - (str) -- representative bond.
        """
        n_pset = self.plus["n_pset"]
        r_bond = check_get_bond(bond)
        if r_bond is None:
            logging.error(f"format error, {bond}")
            return None

        if self.plus["point_group"]:
            bond, nondirectional = self._group.bond_mapping(r_bond)
        else:
            bond, nondirectional = self._group.bond_mapping(r_bond, plus_set=True)

        count = self.counter("bond") + 1
        name0 = f"B{count:02}"
        if color is None:
            color1 = detail["general"]["bond_color1"]
        else:
            color1 = color
        if nondirectional:
            color2 = color1
        else:
            if color2 is None:
                color2 = detail["general"]["bond_color2"]
        primitive_num = len(bond) // n_pset
        width = detail["object"]["bond_width"]

        for no, (b, mp) in enumerate(bond.items()):
            b = NSArray(b)
            v, c = b.convert_bond("bond")
            mp = _mapping_str(mp)
            idx = no % primitive_num
            pset = no // primitive_num
            name = name0
            if n_pset > 1:
                name += f"({pset+1})"
            label = f"b{idx+1:02}:{mp}"
            self._pvw.add_bond(
                position=c.value(), direction=v.value(), color=color1, color2=color2, width=width * scale, name=name, label=label
            )

        return str(r_bond)

    # ==================================================
    def add_vector_equivalent_site(self, v_type, pos, scale=1.0):
        """
        Add vectors at equivalent sites.

        Args:
            v_type (str): vector type.
            pos (str): vector # position.
            scale (float, optional): length scale.

        Returns:
            - (str) -- vector # position.
        """
        n_pset = self.plus["n_pset"]

        txt = pos.split("#")
        if len(txt) != 2:
            logging.error(f"format error, {pos}")
            return None
        vector, r_site_bond = txt
        vector = check_get_site(vector)
        if vector is None:
            logging.error(f"format error, {pos}")
            return None
        r_site = check_get_site_bond(r_site_bond, ret_site=True)
        if r_site is None:
            logging.error(f"format error, {pos}")
            return None

        if self.plus["point_group"]:
            site = self._group.site_mapping(r_site)
        else:
            site = self._group.site_mapping(r_site, plus_set=True)
        site = NSArray.from_str(site.keys())

        count = self.counter("vector") + 1
        name0 = f"V{count:02}"
        color = detail["general"]["vector_color_" + v_type]
        primitive_num = len(site) // n_pset
        length = detail["object"]["vector_length"]

        for no, s in enumerate(site):
            idx = no % primitive_num
            pset = no // primitive_num
            name = name0
            if n_pset > 1:
                name += f"({pset+1})"
            label = f"v{idx+1:02}"
            self._pvw.add_vector(position=s.value(), direction=vector, length=length * scale, color=color, name=name, label=label)

        return str(vector) + "#" + str(r_site)

    # ==================================================
    def add_orbital_equivalent_site(self, o_type, pos, scale=1.0):
        """
        Add orbitals at equivalent sites.

        Args:
            o_type (str): orbital type.
            pos (str): orbital # position.
            scale (float, optional): size scale.

        Returns:
            - (str) -- orbital # position.
        """
        n_pset = self.plus["n_pset"]

        txt = pos.split("#")
        if len(txt) != 2:
            logging.error(f"format error, {pos}")
            return None
        orbital, r_site_bond = txt
        r_site = check_get_site_bond(r_site_bond, ret_site=True)
        if r_site is None:
            logging.error(f"format error, {pos}")
            return None

        if self.plus["point_group"]:
            site = self._group.site_mapping(r_site)
        else:
            site = self._group.site_mapping(r_site, plus_set=True)
        site = NSArray.from_str(site.keys())

        count = self.counter("orbital") + 1
        name0 = f"O{count:02}"
        color = detail["general"]["orbital_color_" + o_type]
        primitive_num = len(site) // n_pset
        size = detail["object"]["orbital_size"]

        for no, s in enumerate(site):
            idx = no % primitive_num
            pset = no // primitive_num
            name = name0
            if n_pset > 1:
                name += f"({pset+1})"
            label = f"o{idx+1:02}"
            self._pvw.add_orbital(position=s.value(), shape=orbital, size=size * scale, color=color, name=name, label=label)

        return str(orbital) + "#" + str(r_site)

    # ==================================================
    def create_combined(self, site_bond, rank, head, ret_bond=False):
        """
        Create combined SAMB.

        Args:
            site_bond (str): site or bond.
            rank (str): harmonics rank.
            head (str): harmonics type.
            ret_bond (bool, optional): return bond ?

        Returns:
            - (dict) -- cluster SAMB.
            - (NSArray) -- site or bond.
            - (dict) -- combined SAMB.
        """
        t_rev = {"Q": "Q", "G": "G", "T": "Q", "M": "G"}

        if site_bond.style == "vector":
            c_samb, site = self._group.site_cluster_samb(site_bond)
        else:
            c_samb, bond = self._group.bond_cluster_samb(site_bond)
            if ret_bond:
                site = bond
            else:
                site = bond.convert_bond("bond")[1]

        x_tag = self._point_group.harmonics.key_list().select(rank=int(rank), head=t_rev[head])
        if head in ["T", "M"]:
            x_tag = [tag.reverse_t_type() for tag in x_tag]
        y_tag = list(c_samb.keys())

        z_samb_all = self._group.z_samb(x_tag, y_tag)
        z_samb = {"Q": [], "G": [], "T": [], "M": []}
        for tag, c in z_samb_all.items():
            tag_str = combined_format(tag)
            z_samb[tag[0].head].append((tag_str, c))
        for k in z_samb.keys():
            z_samb[k] = list(sorted(z_samb[k], key=lambda i: i[0]))

        return c_samb, site, z_samb

    # ==================================================
    def gen_site_samb(self, pos):
        """
        Generate site cluster SAMB.

        Args:
            pos (str): site.

        Returns:
            - (str) -- position.
        """
        pos = check_get_site(pos)
        if pos is None:
            logging.error(f"format error, {pos}")
            self.plus["site_cluster"] = ""
            self.plus["site_z_samb"] = {}
            self.plus["site_c_samb"] = {}
            return ""

        combined_info = self.create_combined(pos, 0, "Q")
        c_samb, cluster, z_samb = combined_info
        self.plus["site_cluster"] = cluster
        self.plus["site_z_samb"] = z_samb
        self.plus["site_c_samb"] = c_samb
        return str(pos)

    # ==================================================
    def gen_bond_samb(self, pos):
        """
        Generate bond cluster SAMB.

        Args:
            pos (str): bond.

        Returns:
            - (str) -- position.
        """
        pos = check_get_bond(pos)
        if pos is None:
            logging.error(f"format error, {pos}")
            self.plus["bond_cluster"] = ""
            self.plus["bond_z_samb"] = {}
            self.plus["bond_c_samb"] = {}
            return ""

        combined_info = self.create_combined(pos, 0, "Q", ret_bond=True)
        c_samb, cluster, z_samb = combined_info
        self.plus["bond_cluster"] = cluster
        self.plus["bond_z_samb"] = z_samb
        self.plus["bond_c_samb"] = c_samb
        return str(pos)

    # ==================================================
    def gen_vector_samb(self, pos, v_type):
        """
        Generate vector cluster SAMB.

        Args:
            pos (str): vector # position.
            v_type (str): vector type.

        Returns:
            - (str) -- position.
        """
        pos = check_get_site_bond(pos)
        if pos is None:
            logging.error(f"format error, {pos}")
            self.plus["vector_cluster"] = ""
            self.plus["vector_z_samb"] = {}
            self.plus["vector_c_samb"] = {}
            return ""

        combined_info = self.create_combined(pos, 1, v_type)
        c_samb, cluster, z_samb = combined_info
        self.plus["vector_cluster"] = cluster
        self.plus["vector_z_samb"] = z_samb
        self.plus["vector_c_samb"] = c_samb
        return str(pos)

    # ==================================================
    def gen_orbital_samb(self, pos, o_type, rank):
        """
        Generate orbital cluster SAMB.

        Args:
            pos (str): orbital # position.
            o_type (str): orbital type.
            rank (str): orbital rank.

        Returns:
            - (str) -- position.
        """
        pos = check_get_site_bond(pos)
        if pos is None:
            logging.error(f"format error, {pos}")
            self.plus["orbital_cluster"] = ""
            self.plus["orbital_z_samb"] = {}
            self.plus["orbital_c_samb"] = {}
            return ""

        combined_info = self.create_combined(pos, rank, o_type)
        c_samb, cluster, z_samb = combined_info
        self.plus["orbital_cluster"] = cluster
        self.plus["orbital_z_samb"] = z_samb
        self.plus["orbital_c_samb"] = c_samb
        return str(pos)

    # ==================================================
    def gen_hopping_samb(self, pos):
        """
        Generate hopping SAMB.

        Args:
            pos (str): bond.

        Returns:
            - (str) -- position.
        """
        pos = check_get_bond(pos)
        if pos is None:
            logging.error(f"format error, {pos}")
            return ""
        return str(pos)

    # ==================================================
    def create_hopping_direction(self, bond):
        """
        Create normal bond direction.

        Args:
            bond (str): bond.

        Returns:
            - (NSArray) -- a set of bonds (no plus_set).
        """
        pg = self.plus["point_group"]
        bond = NSArray(bond)

        site = bond.convert_bond("bond_th")[0]
        if pg:
            sites = list(self._group.site_mapping(site).keys())
        else:
            sites = list(self._group.site_mapping(site, plus_set=True).keys())
        bonds = NSArray.from_str(list(self._group.bond_mapping(bond)[0].keys()))
        new_bonds = []
        for i in range(len(bonds)):
            t = bonds[i].convert_bond("bond_th")[0]
            if not pg:
                t = t.shift()
            if str(t) not in sites:
                new_bonds.append(str(bonds[i].reverse_direction()))
            else:
                new_bonds.append(str(bonds[i]))

        new_bonds = NSArray.from_str(new_bonds)

        return new_bonds

    # ==================================================
    def add_site_samb(self, site, obj, label, scale=1.0):
        """
        Add site cluster SAMB.

        Args:
            site (NSArray): equivalent sites.
            obj (NSArray): SAMB weight.
            label (str): label.
            scale (float, optional): size scale.
        """
        pset = NSArray(self.plus["pset"])
        pg = self.plus["point_group"]

        color = []
        for w in obj:
            if w > 0:
                c = "salmon"
            elif w < 0:
                c = "aqua"
            else:
                c = "silver"
            color.append(c)

        obj /= np.abs(obj).max()
        n_pset = len(pset)
        size = detail["samb"]["site_size"]
        if scale is None or type(scale) == bool:
            scale = detail["samb"]["site_scale"]

        count = self.counter("site_samb") + 1
        name = f"Z_{count:03}"
        for no, p in enumerate(pset):
            name1 = name
            if n_pset != 1:
                name1 += f"({no+1})"
            for s, w, cl in zip(site, obj, color):
                if not pg:
                    s = (s + p).shift()
                if cl == "silver":
                    w = 1
                self._pvw.add_site(position=s.value(), size=size * abs(w) * scale, color=cl, name=name1, label=label)

    # ==================================================
    def add_bond_samb(self, bond, obj, label, z_type, scale=1.0):
        """
        Add bond cluster SAMB.

        Args:
            bond (NSArray): equivalent bonds.
            obj (NSArray): SAMB weight.
            label (str): label.
            z_type (str): SAMB type.
            scale (float, optional): width scale.
        """
        pset = NSArray(self.plus["pset"])
        pg = self.plus["point_group"]
        A = NSArray(self._pvw.A_matrix, "matrix")

        color = []
        if z_type == "Q":
            for w in obj:
                if w > 0:
                    c = "salmon"
                elif w < 0:
                    c = "aqua"
                else:
                    c = "silver"
                color.append(c)
        else:
            for w in obj:
                if w == 0:
                    c = "silver"
                else:
                    c = "salmon"
                color.append(c)

        obj /= np.abs(obj).max()
        n_pset = len(pset)
        width = detail["samb"]["bond_width"]
        if scale is None or type(scale) == bool:
            scale = detail["samb"]["bond_scale"]

        count = self.counter("bond_samb") + 1
        name = f"Z_{count:02}"
        if z_type == "Q":
            for no, p in enumerate(pset):
                name1 = name
                if n_pset != 1:
                    name1 += f"({no+1})"
                for s, w, cl in zip(bond, obj, color):
                    v, c = s.convert_bond("bond")
                    if not pg:
                        c = (c + p).shift()
                    if cl == "silver":
                        w = 1
                    self._pvw.add_bond(
                        position=c.value(),
                        direction=v.value(),
                        color=cl,
                        color2=cl,
                        width=width * abs(w) * scale,
                        name=name1,
                        label=label,
                    )
        else:
            for no, p in enumerate(pset):
                name1 = name
                if n_pset != 1:
                    name1 += f"({no+1})"
                for s, w, cl in zip(bond, obj, color):
                    v, c = s.convert_bond("bond")
                    if not pg:
                        c = (c + p).shift()
                    if cl == "silver":
                        w = 1
                        self._pvw.add_bond(
                            position=c.value(),
                            direction=v.value(),
                            color=cl,
                            color2=cl,
                            width=width * abs(w) * scale,
                            name=name1,
                            label=label,
                        )
                    else:
                        v = v.transform(A, inplace=True)
                        if w < 0:
                            v = -v
                        norm = v.norm() * scale
                        self._pvw.add_vector(
                            position=c.value(),
                            direction=v.value(),
                            color=cl,
                            width=width * abs(w) * scale,
                            length=norm,
                            offset=-0.5,
                            name=name1,
                            label=label,
                        )

    # ==================================================
    def add_vector_samb(self, site, obj, label, z_type, v, scale=1.0):
        """
        Add vector cluster SAMB.

        Args:
            site (NSArray): equivalent sites.
            obj (NSArray): SAMB weight.
            label (str): label.
            z_type (str): SAMB type.
            v (NSArray): vector variable.
            scale (float, optional): length scale.
        """
        pset = NSArray(self.plus["pset"])
        pg = self.plus["point_group"]

        rep = {
            v[0]: sp.Matrix([1, 0, 0]),
            v[1]: sp.Matrix([0, 1, 0]),
            v[2]: sp.Matrix([0, 0, 1]),
        }
        color = detail["general"]["vector_color_" + z_type]
        count = self.counter("vector_samb") + 1
        name = f"Z_{count:03}"
        n_pset = len(pset)
        width = detail["samb"]["vector_width"]

        for no, p in enumerate(pset):
            name1 = name
            if n_pset != 1:
                name1 += f"({no+1})"
            for s, c in zip(site, obj):
                if not pg:
                    s = (s + p).shift()
                if c != 0:
                    c = str(c.subs(rep).T[:])
                    c = NSArray(c)
                    d = c.norm()
                    self._pvw.add_vector(
                        position=s.value(),
                        direction=c.value(),
                        width=width,
                        length=d.value() * scale,
                        color=color,
                        name=name1,
                        label=label,
                    )

    # ==================================================
    def add_orbital_samb(self, site, obj, label, z_type, scale=1.0):
        """
        Add orbital cluster SAMB.

        Args:
            site (NSArray): equivalent sites.
            obj (NSArray): SAMB weight.
            label (str): label.
            z_type (str): SAMB type.
            scale (float, optional): size scale.
        """
        pset = NSArray(self.plus["pset"])
        pg = self.plus["point_group"]

        color = detail["general"]["orbital_color_" + z_type]
        count = self.counter("orbital_samb") + 1
        name = f"Z_{count:03}"
        n_pset = len(pset)
        size = detail["samb"]["orbital_size"]

        for no, p in enumerate(pset):
            name1 = name
            if n_pset != 1:
                name1 += f"({no+1})"
            for s, orb in zip(site, obj):
                if not pg:
                    s = (s + p).shift()
                self._pvw.add_orbital(
                    position=s.value(),
                    shape=orb,
                    size=size * scale,
                    color=color,
                    name=name1,
                    label=label,
                )

    # ==================================================
    def add_vector_modulation(self, obj, igrid, head, v):
        """
        Add vector SAMB modulation.

        Args:
            obj (list): SAMB weight at (cell,pset).
            igrid (NSArray): cell grid.
            head (str): multipole type.
            v (NSArray): vector variable.
        """
        rep = {
            v[0]: sp.Matrix([1, 0, 0]),
            v[1]: sp.Matrix([0, 1, 0]),
            v[2]: sp.Matrix([0, 0, 1]),
        }
        color = detail["general"]["vector_color_" + head]
        pset = NSArray(self.plus["pset"])
        n_pset = self.plus["n_pset"]
        cluster = self.plus["vector_cluster"]

        count = self.counter("vector") + 1
        name = f"mod{count:02}"
        for i_no, i in enumerate(igrid):
            for p_no, p in enumerate(pset):
                label = ""
                if n_pset != 1:
                    label = f"({p_no+1})"
                for no, (s, c) in enumerate(zip(cluster, obj[i_no][p_no])):
                    s = (s + p).shift()
                    label1 = f"s{no+1}" + label
                    if c != 0:
                        c = str(c.subs(rep).T[:])
                        c = NSArray(c)
                        d = c.norm().value()
                        self._pvw.add_vector(
                            position=s.value() + np.array(i), direction=c.value(), length=d, color=color, name=name, label=label1
                        )

    # ==================================================
    def add_orbital_modulation(self, obj, igrid, head):
        """
        Add orbitl SAMB modulation.

        Args:
            obj (list): SAMB weight at (cell,pset).
            igrid (NSArray): cell grid.
            head (str): multipole type.
        """
        color = detail["general"]["orbital_color_" + head]
        pset = NSArray(self.plus["pset"])
        n_pset = self.plus["n_pset"]
        cluster = self.plus["orbital_cluster"]
        size = detail["samb"]["orbital_mod"]

        count = self.counter("orbital") + 1
        name = f"mod{count:02}"
        for i_no, i in enumerate(igrid):
            for p_no, p in enumerate(pset):
                label = ""
                if n_pset != 1:
                    label += f"({p_no+1})"
                for no, (s, orb) in enumerate(zip(cluster, obj[i_no][p_no])):
                    s = (s + p).shift()
                    label1 = f"s{no+1}" + label
                    self._pvw.add_orbital(
                        position=s.value() + np.array(i),
                        shape=str(orb),
                        surface="",
                        size=size,
                        color=color,
                        name=name,
                        label=label1,
                    )

    # ==================================================
    def add_hopping_samb(self, bond, label, scale=1.0):
        """
        Add normal hopping direction.

        Args:
            bond (NSArray): equivalent bonds.
            label (str): label.
            scale (float, optional): length scale.
        """
        pset = NSArray(self.plus["pset"])
        pg = self.plus["point_group"]

        color = "salmon"
        n_pset = len(pset)

        count = self.counter("hopping") + 1
        name = f"Z_{count:02}"
        A = NSArray(self._pvw.A_matrix, "matrix")
        for no, p in enumerate(pset):
            name1 = name
            if n_pset != 1:
                name1 += f"({no+1:02})"
            for s in bond:
                v, c = s.convert_bond("bond")
                if not pg:
                    c = (c + p).shift()
                v = v.transform(A, inplace=True)
                norm = v.norm() * scale
                self._pvw.add_vector(
                    position=c.value(),
                    direction=v.value(),
                    color=color,
                    length=norm * scale,
                    offset=-0.5,
                    name=name1,
                    label=label,
                )

    # ==================================================
    def add_harmonics_set(self, head, rank):
        """
        Add harmonics set.

        Args:
            head (str): harmonics type.
            rank (int): harmonics rank.
        """
        color = detail["general"]["orbital_color_" + head]
        count = self.counter("orbital") + 1
        pname = f"{head}{rank:02}({count:02})"
        size = detail["group"]["harmonics_size"]

        pgh = self._point_group.harmonics
        head = head.replace("T", "Q").replace("M", "G")
        hs = pgh.select(rank=rank, head=head)
        n = len(hs)

        pos = NSArray(
            [[np.cos(2 * np.pi * i / n), np.sin(2 * np.pi * i / n), 0.0] for i in range(n)],
            "vector",
            "value",
        )
        for i in range(n):
            self._pvw.add_orbital(
                position=pos[i].value(),
                shape=str(hs[i].expression(v=NSArray.vector3d())),
                size=size,
                color=color,
                name=pname,
                label=f"{i+1:02}",
            )

    # ==================================================
    def add_virtual_cluster(self, wp, bond):
        """
        Add virtual cluster.

        Args:
            wp (str): Wyckoff position.
            bond (str): bond neighbor list.
        """
        _, site = self._group.virtual_cluster_basis(wyckoff=wp)

        pname = wp
        color = detail["general"]["site_color"]
        for i in range(len(site)):
            self._pvw.add_site(
                position=site[i].value(),
                color=color,
                name=pname,
                label=f"{i+1:02}",
            )

        bond = bond.strip("[]")
        bond = list(map(int, bond.split(",")))
        G = NSArray(self._pvw.G_matrix[0:3, 0:3], style="matrix")
        d = NSArray.distance(site, site, G)
        dkey = list(d.keys())
        for i in bond:
            name = f"b{i:02}"
            if i < len(d):
                for idxs in d[dkey[i]]:
                    t, h = site[idxs[0]], site[idxs[1]]
                    c = (t + h) / 2
                    v = h - t
                    self._pvw.add_bond(position=c.value(), direction=v.value(), name=name)

    # ==================================================
    def create_samb_modulation(self, samb_type, v, head, modulation, repeat, offset):
        """
        Create SAMB modulation object.

        Args:
            v (NSArray): vector variable.
            head (str): _description_
            modulation (list): modulation info.
            repeat (list): repeat.
            offset (list): offset.

        Returns:
            - (list) -- [(xyz)-polynomial at each cluster site.] [cell][pset].
            - (list) -- cell grid.
        """
        phase_dict, igrid = self.create_phase_factor(modulation, repeat, offset)
        n_pset = self.plus["n_pset"]

        cluster = self.plus[samb_type + "_cluster"]
        z_samb = self.plus[samb_type + "_z_samb"]
        c_samb = self.plus[samb_type + "_c_samb"]

        obj = NSArray.zeros((len(igrid) * n_pset, len(cluster)), "vector")
        for p_no in range(n_pset):
            for basis, coeff, k, n in modulation:
                z_head = basis[0]
                irrep = int(basis[1:]) - 1
                t_odd = head.replace("M", "T").replace("G", "Q") != z_head.replace("M", "T").replace("G", "Q")
                phase = phase_dict[(k, n, p_no)]
                coeff = NSArray(coeff, fmt="value")
                cluster_obj = create_samb_object(
                    z_samb,
                    cluster,
                    c_samb,
                    z_head,
                    irrep,
                    self._point_group,
                    v,
                    t_odd,
                )
                for i_no in range(len(igrid)):
                    obj[i_no * n_pset + p_no] += coeff * phase[i_no] * cluster_obj

        obj = obj.numpy().reshape((len(igrid), n_pset, len(cluster))).tolist()

        return obj, igrid

    # ==================================================
    def create_phase_factor(self, modulation, repeat, offset):
        """
        Create phase factor.

        Args:
            modulation (list): modulation info. [(basis, coeff, k, n)].
            repeat (list): repeat.
            offset (list): offset.

        Returns:
            - (dict) -- {(k(str),n(int),plus_set no(int)): [phase at each grid(float)]}.
            - (list) -- cell grid.
        """
        pset = NSArray(self.plus["pset"])
        igrid = NSArray.igrid(repeat, offset)

        phase_dict = {}
        for _, _, k, n in modulation:
            kvec = np.array(NSArray(k).tolist(), dtype=float)
            for p_no, p in enumerate(pset):
                lst = []
                for i in igrid:
                    kr = 2.0 * np.pi * kvec @ (i.value() + p.value())
                    phase = np.cos(kr) if n == "cos" else np.sin(kr)
                    lst.append(phase)
                phase_dict[(k, n, p_no)] = lst

        return phase_dict, igrid.numpy().astype(int).tolist()
