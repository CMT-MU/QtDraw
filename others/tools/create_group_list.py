from multipie import Group
import numpy as np


def create_group_mapping_data():
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


mapping = create_group_mapping_data()
print(mapping)
