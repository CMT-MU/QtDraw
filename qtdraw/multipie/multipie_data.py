"""
Multipie data.

This module provides a data manager for MultiPie.
"""

import numpy as np
import sympy as sp
import copy

from multipie import __version__, Group
from qtdraw.multipie.multipie_group_list import group_list, group_list_index
from qtdraw.multipie.multipie_setting import default_status
from qtdraw.multipie.multipie_plot import (
    plot_cell_site,
    plot_cell_bond,
    plot_cell_vector,
    plot_cell_multipole,
    plot_bond_definition,
    plot_site_cluster,
    plot_bond_cluster,
    plot_vector_cluster,
    plot_orbital_cluster,
)
from qtdraw.multipie.multipie_util import check_linear_combination, convert_vector_object, create_samb_modulation, phase_factor


# ==================================================
class MultiPieData:
    # ==================================================
    def __init__(self, parent):
        """
        MultiPie data manager.
        """
        self.pvw = parent  # PyVista Widget.

        self._crystal_list = {crystal: {tp: i[1] for tp, i in v.items()} for crystal, v in group_list.items()}
        self._to_tag = {}
        self._to_name = {}
        for v in group_list.values():
            for i in v.values():
                for a, b in zip(i[0], i[1]):
                    self._to_tag[b] = a
                    self._to_name[a] = b

        self._crystal = "triclinic"
        self._type = "PG"
        self._idx = 0

        self.set_status()
        self.status["version"] = __version__
        self.clear_data()

    # ==================================================
    @property
    def group(self):
        if self._group is None:
            self._group = Group(self.status["group"]["tag"])

        return self._group

    # ==================================================
    @property
    def ps_group(self):
        if self.group.group_type in ["PG", "SG"]:
            return self.group
        if self._ps_group is None:
            ps = self.group.info.PG if self.group.group_type in ["MPG"] else self.group.info.SG
            self._ps_group = Group(ps)

        return self._ps_group

    # ==================================================
    @property
    def p_group(self):
        if self.group.group_type in ["PG"]:
            return self.group
        if self._p_group is None:
            self._p_group = Group(self.group.info.PG)

        return self._p_group

    # ==================================================
    @property
    def mp_group(self):
        if self.group.group_type in ["MPG"]:
            return self.group
        if self._mp_group is None:
            self._mp_group = Group(self.group.info.MPG)

        return self._mp_group

    # ==================================================
    def _get_group_list(self, crystal=None, tp=None):
        if crystal is None:
            crystal = self._crystal
        if tp is None:
            tp = self._type
        return self._crystal_list[crystal][tp]

    # ==================================================
    def _get_group_name(self):
        info = self.group.info
        name = {
            "PG": self._to_name[info.PG],
            "SG": self._to_name[info.SG],
            "MPG": self._to_name[info.MPG],
            "MSG": self._to_name[info.MSG],
        }
        return name

    # ==================================================
    @property
    def _type_list(self):
        return {"Point Group": "PG", "Space Group": "SG", "Magnetic Point Group": "MPG", "Magnetic Space Group": "MSG"}

    # ==================================================
    def set_crystal_type(self, crystal):
        group_list = self._get_group_list(crystal)
        group = group_list[0]  #  top.
        self.set_group(group)
        return group_list, group

    # ==================================================
    def set_group_type(self, group_type):
        if group_type.count(" "):
            group_type = self._type_list[group_type]
        group = self._get_group_name()[group_type]
        self.set_group(group)
        group_list = self._get_group_list(tp=group_type)
        return group_list, group

    # ==================================================
    def set_group(self, group):
        if group.count("#"):
            group = self._to_tag[group]

        self._crystal, self._type, self._idx = group_list_index[group]
        self.status["group"]["tag"] = group

        self._group = None
        self._p_group = None
        self._ps_group = None
        self._mp_group = None

        self.set_axis()

    # ==================================================
    def set_status(self, status=None, group=None):
        self.status = copy.deepcopy(default_status)

        if status is not None or status:
            self.status.update(status)

        if group is None:
            self.set_group(self.status["group"]["tag"])
        else:
            self.set_group(group)

    # ==================================================
    def set_axis(self):
        if self._type in ["PG", "MPG"]:
            self.pvw.set_cell("off")
            self.pvw.set_axis("full")
        else:
            self.pvw.set_cell("single")
            self.pvw.set_axis("on")
        self.pvw.set_view()

    # ==================================================
    def clear_data(self):
        self.status["counter"] = {}

        # basis.
        self._site_list = []
        self._site_wp = ""
        self._sites = [[]]
        self._site_mp = [[]]
        self._site_samb = {}
        self._site_samb_list = {}

        self._bond_list = []
        self._bond_wp = ""
        self._bonds = [[]]
        self._bond_mp = [[]]
        self._bond_samb = {}
        self._bond_samb_list = {}

        self._vector_list = {"Q": [], "G": [], "T": [], "M": []}
        self._vector_wp = ""
        self._vector_samb_site = [[]]
        self._vector_mp = [[]]
        self._vector_n_pset = 1
        self._vector_samb = {}
        self._vector_samb_list = {}
        self._vector_samb_var = {"Q": [], "G": [], "T": [], "M": []}

        self._orbital_list = {"Q": [], "G": [], "T": [], "M": []}
        self._orbital_wp = ""
        self._orbital_samb_site = [[]]
        self._orbital_mp = [[]]
        self._orbital_n_pset = 1
        self._orbital_samb = {}
        self._orbital_samb_list = {}
        self._orbital_samb_var = {"Q": [], "G": [], "T": [], "M": []}

    # ==================================================
    def _set_counter(self, name):
        cnt = self.status["counter"].get(name, 0) + 1
        self.status["counter"][name] = cnt
        return cnt

    # ==================================================
    def _get_index_list(self, lst):
        idx = [(Group.tag_multipole(i), i) for i in lst]
        tag_lst = [n for v, _ in idx for n in v]
        idx_comp = [(i, no) for v, i in idx for no, _ in enumerate(v)]

        return tag_lst, idx_comp

    # ==================================================
    def set_group_find_wyckoff(self, find_wyckoff):
        self.status["group"]["find_wyckoff"] = find_wyckoff

    # ==================================================
    def add_site(self, site, size=None, color=None, opacity=None):
        self.status["object"]["site"] = site

        sites, mp, wp = self.group.create_cell_site(site)
        plot_cell_site(self, sites, wp=wp, label=mp, size=size, color=color, opacity=opacity)

    # ==================================================
    def add_bond(self, bond, width=None, color=None, color2=None, opacity=None):
        self.status["object"]["bond"] = bond

        bonds, mp, wp = self.group.create_cell_bond(bond)
        plot_cell_bond(self, bonds, wp=wp, label=mp, width=width, color=color, color2=color2, opacity=opacity)

    # ==================================================
    def add_vector(self, vector, tp="Q", cartesian=True, average=False, length=None, width=None, color=None, opacity=None):
        self.status["object"]["vector_type"] = tp
        self.status["object"]["vector"] = vector
        self.status["object"]["vector_average"] = average
        self.status["object"]["vector_cartesian"] = cartesian

        vectors, sites, mp, wp = self.group.create_cell_vector(vector, tp, average, cartesian)
        plot_cell_vector(
            self,
            vectors,
            sites,
            tp,
            wp=wp,
            label=mp,
            average=average,
            cartesian=cartesian,
            length=length,
            width=width,
            color=color,
            opacity=opacity,
        )

    # ==================================================
    def add_orbital(self, orbital, tp="Q", average=False, size=None, color=None, opacity=None):
        self.status["object"]["orbital_type"] = tp
        self.status["object"]["orbital"] = orbital
        self.status["object"]["orbital_average"] = average

        orbitals, sites, mp, wp = self.group.create_cell_multipole(orbital, tp, average)
        plot_cell_multipole(self, orbitals, sites, tp, wp=wp, label=mp, average=average, size=size, color=color, opacity=opacity)

    # ==================================================
    def add_bond_definition(self, bond, length=None, width=None, color=None, opacity=None):
        self.status["basis"]["bond_definition"] = bond

        group = self.ps_group
        wp, bonds = group.find_wyckoff_bond(bond)
        mp = group.wyckoff["bond"][wp]["mapping"]
        if len(bonds) != len(mp):
            mp = mp * (len(bonds) // len(mp))

        plot_bond_definition(self, bonds, wp=wp, label=mp, length=length, width=width, color=color, opacity=opacity)

    # ==================================================
    def site_samb_list(self, site):
        self.status["basis"]["site"] = site

        group = self.ps_group

        self._site_wp, self._sites = group.find_wyckoff_site(site)
        self._site_mp = group.wyckoff["site"][self._site_wp]["mapping"]
        self._site_samb = group.cluster_samb(self._site_wp)
        if len(self._site_mp) != len(self._sites):
            self._site_mp = self._site_mp * (len(self._sites) // len(self._site_mp))

        self._site_list, self._site_samb_list = self._get_index_list(self._site_samb.keys())

        return self._site_list

    # ==================================================
    def add_site_samb(self, tag, size=None, p_color=None, n_color=None, z_color=None, z_size=None):
        if tag not in self._site_list:
            return
        samb, comp = self._site_samb_list[self._site_list.index(tag)]
        samb = self._site_samb[samb][0][comp]
        mp = self._site_mp
        if len(samb) != len(self._sites):
            samb = np.tile(samb, len(self._sites) // len(samb))

        plot_site_cluster(
            self,
            self._sites,
            samb,
            wp=self._site_wp,
            label=mp,
            color=z_color,
            color_neg=n_color,
            color_pos=p_color,
            zero_size=z_size,
            size_ratio=size,
        )

    # ==================================================
    def bond_samb_list(self, bond):
        self.status["basis"]["bond"] = bond

        group = self.ps_group

        self._bond_wp, self._bonds = group.find_wyckoff_bond(bond)
        self._bond_mp = group.wyckoff["bond"][self._bond_wp]["mapping"]
        self._bond_samb = group.cluster_samb(self._bond_wp, "bond")
        if len(self._bond_mp) != len(self._bonds):
            self._bond_mp = self._bond_mp * (len(self._bonds) // len(self._bond_mp))

        self._bond_list, self._bond_samb_list = self._get_index_list(self._bond_samb.keys())

        return self._bond_list

    # ==================================================
    def add_bond_samb(self, tag, width=None, p_color=None, n_color=None, z_color=None, z_width=None, a_size=None):
        if tag not in self._bond_list:
            return
        samb, comp = self._bond_samb_list[self._bond_list.index(tag)]
        sym = samb[0] in ["Q", "G"]

        samb = self._bond_samb[samb][0][comp]
        mp = self._bond_mp
        if len(samb) != len(self._bonds):
            samb = np.tile(samb, len(self._bonds) // len(samb))
        plot_bond_cluster(
            self,
            self._bonds,
            samb,
            wp=self._bond_wp,
            label=mp,
            sym=sym,
            color=z_color,
            color_neg=n_color,
            color_pos=p_color,
            width=z_width,
            arrow_ratio=a_size,
            width_ratio=width,
        )

    # ==================================================
    def vector_samb_list(self, vector, tp="Q"):
        self.status["basis"]["vector_type"] = tp
        self.status["basis"]["vector"] = vector

        group = self.ps_group

        samb, self._vector_wp, self._vector_samb_site = group.multipole_cluster_samb(tp, 1, vector)
        self._vector_mp = (
            group.wyckoff["bond"][self._vector_wp]["mapping"]
            if "@" in self._vector_wp
            else group.wyckoff["site"][self._vector_wp]["mapping"]
        )
        if len(self._vector_mp) != len(self._vector_samb_site):
            self._vector_n_pset = len(self._vector_samb_site) // len(self._vector_mp)
            self._vector_mp = self._vector_mp * self._vector_n_pset
        else:
            self._vector_n_pset = 1

        self._vector_samb = {}
        self._vector_samb_list = {}
        self._vector_samb_var = {}
        for tp in ["Q", "G", "T", "M"]:
            self._vector_samb[tp] = samb.select(X=tp)
            self._vector_list[tp], self._vector_samb_list[tp] = self._get_index_list(self._vector_samb[tp].keys())
            self._vector_list[tp] = [f"{tp}{no+1:02d}: {i}" for no, i in enumerate(self._vector_list[tp])]
            self._vector_samb_var[tp] = [f"{tp}{i+1:02d}" for i in range(len(self._vector_list[tp]))]

        return self._vector_list

    # ==================================================
    def add_vector_samb(self, lc, length=None, width=None, color=None, opacity=None):
        ex, var = check_linear_combination(lc, self._vector_samb_var)
        if ex is None:
            return

        self.status["basis"]["vector_lc"] = lc

        X = self.status["basis"]["vector_type"]
        wp = self._vector_wp
        site = self._vector_samb_site
        mp = self._vector_mp

        lc_obj = {}
        for i in var:
            tp = i[0]
            idx = int(i[1:]) - 1
            samb, comp = self._vector_samb_list[tp][idx]
            samb = self._vector_samb[tp][samb][0][comp]
            obj1 = self.ps_group.combined_object(wp, tp, samb)
            obj1 = np.tile(obj1, self._vector_n_pset)
            lc_obj[i] = sp.Matrix(convert_vector_object(obj1))

        obj = np.array(ex.subs(lc_obj))

        plot_vector_cluster(self, site, obj, X, wp=wp, label=mp, length=length, width=width, color=color, opacity=opacity)

    # ==================================================
    def add_vector_samb_modulation(self, modulation_range, length=None, width=None, color=None, opacity=None):
        modulation, rng = modulation_range.split(":")
        mod_list, is_magnetic = self._parse_modulation(modulation)
        if not mod_list:
            return

        self.status["basis"]["vector_modulation"] = modulation_range

        rng, upper = self._parse_range(rng)
        pset = self.ps_group.symmetry_operation["plus_set"].astype(float)
        phase_dict, igrid = phase_factor(mod_list, rng, pset)

        X = self.status["basis"]["vector_type"]
        wp = self._vector_wp
        site = self._vector_samb_site

        obj, site_idx, full_site = create_samb_modulation(
            self.ps_group, mod_list, phase_dict, igrid, pset, self._vector_samb, self._vector_samb_list, wp, site
        )
        obj = convert_vector_object(obj)

        self.pvw.set_range([0, 0, 0], upper)
        self.pvw.set_repeat(True)
        self.pvw.set_nonrepeat()
        self.pvw.set_repeat(False)

        plot_vector_cluster(
            self, full_site, obj, X, wp=wp, label=site_idx, length=length, width=width, color=color, opacity=opacity
        )

    # ==================================================
    def orbital_samb_list(self, orbital, tp="Q", rank=0):
        rank = int(rank)
        self.status["basis"]["orbital_type"] = tp
        self.status["basis"]["orbital_rank"] = rank
        self.status["basis"]["orbital"] = orbital

        group = self.ps_group

        samb, self._orbital_wp, self._orbital_samb_site = group.multipole_cluster_samb(tp, rank, orbital)
        self._orbital_mp = (
            group.wyckoff["bond"][self._orbital_wp]["mapping"]
            if "@" in self._orbital_wp
            else group.wyckoff["site"][self._orbital_wp]["mapping"]
        )
        if len(self._orbital_mp) != len(self._orbital_samb_site):
            self._orbital_n_pset = len(self._orbital_samb_site) // len(self._orbital_mp)
            self._orbital_mp = self._orbital_mp * self._orbital_n_pset
        else:
            self._orbital_n_pset = 1

        self._orbital_samb = {}
        self._orbital_samb_list = {}
        self._orbital_samb_var = {}
        for tp in ["Q", "G", "T", "M"]:
            self._orbital_samb[tp] = samb.select(X=tp)
            self._orbital_list[tp], self._orbital_samb_list[tp] = self._get_index_list(self._orbital_samb[tp].keys())
            self._orbital_list[tp] = [f"{tp}{no+1:02d}: {i}" for no, i in enumerate(self._orbital_list[tp])]
            self._orbital_samb_var[tp] = [f"{tp}{i+1:02d}" for i in range(len(self._orbital_list[tp]))]

        return self._orbital_list

    # ==================================================
    def add_orbital_samb(self, lc, size=None, color=None, opacity=None):
        ex, var = check_linear_combination(lc, self._orbital_samb_var)
        if ex is None:
            return

        self.status["basis"]["orbital_lc"] = lc

        X = self.status["basis"]["orbital_type"]
        wp = self._orbital_wp
        site = self._orbital_samb_site
        mp = self._orbital_mp

        lc_obj = {}
        for i in var:
            tp = i[0]
            idx = int(i[1:]) - 1
            samb, comp = self._orbital_samb_list[tp][idx]
            samb = self._orbital_samb[tp][samb][0][comp]
            obj1 = self.ps_group.combined_object(wp, tp, samb)
            lc_obj[i] = sp.Matrix(np.tile(obj1, self._orbital_n_pset))

        obj = np.array(ex.subs(lc_obj)).reshape(-1)

        plot_orbital_cluster(self, site, obj, X, wp=wp, label=mp, size=size, color=color, opacity=opacity)

    # ==================================================
    def add_orbital_samb_modulation(self, modulation_range, size=None, color=None, opacity=None):
        modulation, rng = modulation_range.split(":")
        mod_list, is_magnetic = self._parse_modulation(modulation)
        if not mod_list:
            return

        self.status["basis"]["orbital_modulation"] = modulation_range

        rng, upper = self._parse_range(rng)
        pset = self.ps_group.symmetry_operation["plus_set"].astype(float)
        phase_dict, igrid = phase_factor(mod_list, rng, pset)

        X = self.status["basis"]["orbital_type"]
        wp = self._orbital_wp
        site = self._orbital_samb_site

        obj, site_idx, full_site = create_samb_modulation(
            self.ps_group, mod_list, phase_dict, igrid, pset, self._orbital_samb, self._orbital_samb_list, wp, site
        )

        self.pvw.set_range([0, 0, 0], upper)
        self.pvw.set_repeat(True)
        self.pvw.set_nonrepeat()
        self.pvw.set_repeat(False)

        plot_orbital_cluster(self, full_site, obj, X, wp=wp, label=site_idx, size=size, color=color, opacity=opacity)

    # ==================================================
    @staticmethod
    def _parse_modulation(s):
        """
        Parse modulation list.

        Args:
            s (str): modulation list in str, [[basis,coeff,k,cos/sin]].

        Returns:
            - (list) -- modulation list.
            - (bool) -- magnetic ?
        """
        rows = []
        row, token, depth = None, "", 0
        for c in s:
            try:
                if c == "[":
                    depth += 1
                    if depth == 2:
                        row, token = [], ""
                    continue

                if c == "]":
                    if depth == 2:
                        row.append(token.strip())
                        rows.append(row)
                        token = ""
                    depth -= 1
                    if depth < 0:
                        return []
                    continue

                if c == "," and depth == 2:
                    row.append(token.strip())
                    token = ""
                    continue

                if depth >= 2:
                    token += c

            except Exception as e:
                return []

        if depth != 0:
            return []

        rows = [[r[0], r[1], "[" + r[2] + "]", r[3]] for r in rows]

        if rows:
            is_magnetic = all(row[1].startswith(("T", "M")) for row in rows)
        else:
            is_magnetic = False

        return rows, is_magnetic

    # ==================================================
    @staticmethod
    def _parse_range(r):
        """
        Parse range.

        Args:
            r (str): range, [r1,r2,r3].

        Returns:
            - (list) -- integer range.
            - (list) -- upper bound.
        """
        eps = 0.001
        rng = list(map(int, r.strip(" [] ").split(",")))
        upper = [rng[0] - eps, rng[1] - eps, rng[2] - eps]
        return rng, upper
