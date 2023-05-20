import sympy as sp
import numpy as np
from gcoreutils.nsarray import NSArray
from gcoreutils.list_util import list_to_table
from multipie.tag.tag_irrep import TagIrrep
from multipie.tag.tag_multipole import TagMultipole
from qtdraw.core.table_dialog import TableDialog
from qtdraw.multipie.setting import rcParams


# ==================================================
def show_group_info(group, name, header, role, align, data, vheader=None, width=1024, height=600, parent=None):
    no, _, IS, setting = group.tag.info()
    s = f"No.{no}: {str(group)}, {IS}"
    if setting:
        s += " (" + setting + " setting)"
    title = name + " - " + s

    table = TableDialog(
        data, title=title, header=header, vheader=vheader, role=role, align=align, width=width, height=height, parent=parent
    )
    table.show()


# ==================================================
def create_harmonics(group, rank, head, qtdraw, parent):
    pgh = group.harmonics
    head = head.replace("T", "Q").replace("M", "G")
    hs = pgh.select(rank=rank, head=head)
    n = len(hs)

    name = head + "_harmonics"
    header = ["symbol", "rank", "irrep.", "mul.", "comp.", "expression", "definition"]
    role = ["math", "text", "math", "text", "text", "math", "math"]
    align = ["center", "center", "center", "center", "center", "left", "left"]
    vheader = [str(i + 1) for i in range(n)]

    data = []
    for h in hs:
        mul = h.tag.mul
        comp = h.tag.comp
        irrep = h.tag.tag_irrep()
        dim = irrep.dim
        if mul < 1:
            mul = ""
        if dim == 1:
            comp = ""
        data.append(
            [h.latex(), rank, irrep.latex(), mul, comp, h.expression(v=NSArray.vector3d(head)).latex(), h.definition().latex()]
        )

    show_group_info(group, name, header, role, align, data, vheader=vheader, parent=parent)

    pos = NSArray([[np.cos(2 * np.pi * i / n), np.sin(2 * np.pi * i / n), 0.0] for i in range(n)], "vector", "value")
    color = rcParams["orbital_color_" + head]
    pname = qtdraw._get_name("orbital")
    for i in range(n):
        qtdraw.plot_orbital(
            pos[i],
            str(hs[i].expression(v=NSArray.vector3d())),
            size=0.8 / (rank + 1),
            color=color,
            name=pname,
            label=f"{i+1}",
            show_lbl=rcParams["show_label"],
        )
    qtdraw._plot_all_object()


# ==================================================
def create_harmonics_decomp(group, rank, head, to_pg, parent):
    pgh = group.harmonics
    to_pg = to_pg.split(".")[1][1:]  # remove space at top.
    head = head.replace("T", "Q").replace("M", "G")
    axial = head == "G"
    hs = pgh.select(rank=rank, head=head)
    decomp = group.irrep_decomposition(to_pg, rank, axial)
    n = len(hs)

    name = head + "_harmonics decomposition to " + to_pg
    header = ["symbol [" + str(group) + "]", "decomp. expression [" + to_pg + "]"]
    role = ["math", "math"]
    align = ["center", "center"]
    vheader = [str(i + 1) for i in range(n)]

    data = []
    for h, d in zip(hs, decomp):
        ex = sp.S(0)
        for c, b in d[1]:
            ex += c * TagMultipole(b).symbol()
        data.append([h.latex(), sp.latex(ex)])

    show_group_info(group, name, header, role, align, data, vheader=vheader, parent=parent)


# ==================================================
def create_character_table(group, parent):
    name = "character"
    ch = group.character
    n = len(ch.symmetry_operation())
    header = ["irrep."] + [f"SO{i+1}" for i in range(n)]
    role = ["math"] * (n + 1)
    align = ["center"] * (n + 1)

    data = []
    data.append([""] + [i.latex() for i in ch.symmetry_operation()])
    for r in ch.irrep_list:
        data.append([r.latex()] + [sp.latex(j) for j in ch.character(r)])

    show_group_info(group, name, header, role, align, data, parent=parent)


# ==================================================
def create_wyckoff(group, parent):
    name = "wyckoff_position"
    wp = group.wyckoff
    so = group.symmetry_operation
    n = list(wp.keys())[-1].n
    if not group.tag.is_point_group():
        ns = len(so.plus_set)
        n = n // ns
    n = min(10, n)
    header = ["position"] + [str(i + 1) for i in range(n)]
    role = ["text"] + ["math"] * n
    align = ["center"] * (n + 1)

    data = []
    if not group.tag.is_point_group():
        ps = ["+" + i for i in so.plus_set.latex()]
        data.append(["plus set"] + ps + [""] * (n - len(ps)))
        data.append([""] * (n - len(ps) + 2))

    for w in wp.keys():
        row = list_to_table(wp.position(w).latex(), n, "")
        for i, r in enumerate(row):
            if i == 0:
                data.append([str(w)] + r)
            else:
                data.append([""] + r)

    show_group_info(group, name, header, role, align, data, parent=parent)


# ==================================================
def create_product_table(group, parent):
    name = "product_table"
    so = group.symmetry_operation
    op = [i.latex() for i in so.keys()]
    header = ["SO"] + [f"SO{i+1}" for i in range(len(op))]
    role = ["math"] * (len(op) + 1)
    align = ["center"] * (len(op) + 1)
    vheader = [""] + [str(i + 1) for i in range(len(so))]

    data = []
    data.append([""] + op)
    for i in so.keys():
        data.append([i.latex()] + [so.product(i, j).latex() for j in so.keys()])

    show_group_info(group, name, header, role, align, data, vheader=vheader, parent=parent)


# ==================================================
def create_symmetry_operation(group, parent):
    so = group.symmetry_operation

    name = "symmetry_operation"
    header = ["symbol", "polar vector", "axial vector", "det"]
    role = ["math", "math", "math", "math"]
    align = ["center", "center", "center", "center"]
    vheader = [str(i + 1) for i in range(len(so))]

    data = []
    if not group.tag.is_point_group():
        ps = ["+" + i for i in so.plus_set.latex()]
        data.append(ps + [""] * (4 - len(ps)))
        data.append(["", "", "", ""])
        vheader = ["plus set", ""] + vheader

    pso = so.mat(axial=False)
    aso = so.mat(axial=True)
    for no in range(len(so)):
        p = pso[no][0:3, :]
        a = aso[no][0:3, :]
        data.append([so.full[no].latex(), p.latex(), a.latex(), p[0:3, 0:3].det().latex()])

    show_group_info(group, name, header, role, align, data, vheader=vheader, parent=parent)


# ==================================================
def create_v_cluster(group, wp, bond, qtdraw, parent):
    basis, site = group.virtual_cluster_basis(wyckoff=wp)
    n = min(10, len(site))

    name = "virtual cluster"
    header = ["symbol"] + [f"S{i+1}" for i in range(n)]
    role = ["math"] * (n + 1)
    align = ["center"] * (n + 1)

    data = []
    row = list_to_table(site.latex(), n, "")
    for i, r in enumerate(row):
        if i == 0:
            data.append([r"\text{site (r.c.)}"] + r)
        else:
            data.append([""] + r)
    for tag, v in basis.items():
        row = list_to_table(NSArray(v.tolist(), "scalar").latex(), n, "")
        for i, r in enumerate(row):
            if i == 0:
                t = tag.latex()
            else:
                t = ""
            data.append([t] + r)

    show_group_info(group, name, header, role, align, data, parent=parent)

    pname = qtdraw._get_name("site")
    color = rcParams["site_color"]
    for i in range(len(site)):
        qtdraw.plot_site(site[i], size=1.0, color=color, name=pname, label=f"{i+1}", show_lbl=rcParams["show_label"])

    if bond == "":
        bond = "1"
    bond = list(map(int, bond.split(" ")))
    d = NSArray.distance(site, site, qtdraw._G[0:3, 0:3])
    dkey = list(d.keys())
    for i in bond:
        name = f"b{i}"
        if i < len(d):
            for idxs in d[dkey[i]]:
                t, h = site[idxs[0]], site[idxs[1]]
                c = (t + h) / 2
                v = h - t
                qtdraw.plot_bond(c, v, name=name)

    qtdraw._plot_all_object()


# ==================================================
def create_response(group, rank, i_type, t_type, parent):
    dic = {("polar", "E"): "Q", ("polar", "M"): "T", ("axial", "E"): "G", ("axial", "M"): "M"}
    pgr = group.response
    head = dic[(i_type, t_type)]
    rt = pgr.select(rank=rank, head=head)

    name = i_type + "_response"
    header = ["symbol", "tensor"]
    role = ["math", "math"]
    align = ["center", "center"]

    data = []
    for tag in rt.keys():
        M = rt[tag]
        data.append([tag.latex(), M.latex()])

    data.append(["", ""])
    data.append([r"\text{component}", r"\text{multipole}"])
    for tag in rt.keys():
        def_mul = rt.definition[tag]
        for t, d in def_mul.items():
            data.append([sp.latex(t), sp.latex(d)])

    show_group_info(group, name, header, role, align, data, parent=parent)


# ==================================================
def create_atomic_mp(group, bra, ket, am, parent):
    name = "atomic multipole"
    header = ["symbol", "rank", "irrep.", "s", "k", "basis"]
    role = ["math", "text", "math", "text", "text", "math"]
    align = ["center"] * 6
    vheader = ["", ""] + [str(i + 1) for i in range(am.active_num())]

    data = []
    s = r"\langle " + str(bra) + r"|" + str(ket) + r"\rangle"
    data.append([""] * 5 + [s])
    data.append([""] * 6)
    for am1 in am.values():
        for tag, m in am1.items():
            data.append([tag.latex(), tag.rank, TagIrrep(tag.irrep).latex(), tag.s, tag.k, NSArray(m.tolist(), "matrix").latex()])

    show_group_info(group, name, header, role, align, data, vheader=vheader, parent=parent)
