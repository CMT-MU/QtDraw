"""
Create group list and group index.

Copy output of this to "multipie/multipie_group_list.py".
"""

from multipie import Group
import numpy as np


# ==================================================
def create_group_list():
    dic = {}
    for c in Group.global_info()["id_set"]["PG"]["crystal"].keys():
        dic[c] = {"PG": [], "SG": [], "MPG": [], "MSG": []}
        for i in Group.global_info()["id_set"]["PG"]["crystal"][c]:
            info = Group(i).info
            tag = f"#{info.no}: {info.tag} ({info.international})"
            dic[c]["PG"].append((i, tag))
        for i in Group.global_info()["id_set"]["SG"]["crystal"][c]:
            info = Group(i).info
            tag = f"#{info.no}: {info.tag} ({info.international})"
            dic[c]["SG"].append((i, tag))
        for i in Group.global_info()["id_set"]["MPG"]["crystal"][c]:
            info = Group(i).info
            tag = f"#{info.no}: {info.international}"
            dic[c]["MPG"].append((i, tag))
        for i in Group.global_info()["id_set"]["MSG"]["crystal"][c]:
            info = Group(i).info
            tag = f"#{info.no}: {info.BNS} (#{info.BNS_id})"
            dic[c]["MSG"].append((i, tag))
    dic = {c: {t: np.array(lst, dtype=object).T.tolist() for t, lst in v.items()} for c, v in dic.items()}
    return dic


# ==================================================
def create_group_list_index(group_list):
    dic = {}
    for tp in ["PG", "SG", "MPG", "MSG"]:
        for c, v in group_list.items():
            for no, i in enumerate(v[tp][1]):
                gno, g = i.split(" ")[:2]
                gno = int(gno[1:-1])
                if tp in ["PG", "SG"]:
                    dic[g] = (c, tp, no)
                else:
                    dic["M:" + g] = (c, tp, no)
                if tp == "SG":
                    dic[gno] = (c, tp, no)
                dic[f"{tp}:{gno}"] = (c, tp, no)

    return dic


# ==================================================
group_list = create_group_list()
group_list_index = create_group_list_index(group_list)

print("group_list =", group_list)
print()
print("group_list_index =", group_list_index)
