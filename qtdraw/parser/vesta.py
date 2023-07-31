from pymatgen.core import Structure
from pymatgen.core import Lattice
from pymatgen.analysis.graphs import StructureGraph
from pymatgen.analysis.local_env import MinimumDistanceNN
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

# ==================================================
vesta_key = [  # VESTA Keywords.
    "#VESTA_FORMAT_VERSION",
    "ATOMM",
    "ATOMP",
    "ATOMS",
    "ATOMT",
    "BKGRC",
    "BONDM",
    "BONDP",
    "BONDS",
    "CELLP",
    "COMPS",
    "CONTR",
    "CRYSTAL",
    "DISPF",
    "DLATM",
    "DLBND",
    "DLPLY",
    "DPTHQ",
    "FORMM",
    "FORMP",
    "FORMS",
    "GROUP",
    "HBOND",
    "HKLPM",
    "HKLPP",
    "ISURF",
    "LABEL",
    "LBLAT",
    "LBLSP",
    "LIGHT0",
    "LIGHT1",
    "LIGHT2",
    "LIGHT3",
    "LMATRIX",
    "LORIENT",
    "LTRANSL",
    "MODEL",
    "PLN2D",
    "POLYM",
    "POLYP",
    "POLYS",
    "PROJT",
    "SBOND",
    "SCENE",
    "SECCL",
    "SECTP",
    "SECTS",
    "SHAPE",
    "SITET",
    "SPLAN",
    "STRUC",
    "STYLE",
    "SURFM",
    "SURFS",
    "SYMOP",
    "TEX3P",
    "TEXCL",
    "THERI",
    "TITLE",
    "UCOLP",
    "VECTR",
    "VECTS",
    "VECTT",
]


# ==================================================
def parse_vesta(file):
    """
    parse VESTA file.

    Args:
        file (str): filename.

    Returns:
        dict: VESTA keyword - content dict.
    """
    data = []
    with open(file) as f:
        for line in f:
            d = line.split(" ")
            d = [i.replace("\n", "") for i in d if i.replace("\n", "") != ""]
            if d:
                data += [d + ["\n"]]
    data = sum(data, [])
    pos = sorted([(data.index(i), i) if i in data else (-1, i) for i in vesta_key], key=lambda x: x[0])

    dic = {}
    for i in range(len(pos) - 1):
        if pos[i][0] != -1:
            if pos[i + 1][0] - pos[i][0] != 1:
                dic[pos[i][1]] = (" ".join(data[pos[i][0] + 1 : pos[i + 1][0]])).strip()
            else:
                dic[pos[i][1]] = ""

    return dic


# ==================================================
def create_vesta_graph(vesta_dict):
    """
    create StructureGraph for VESTA.

    Args:
        vesta_dict (dict): VESTA dict.

    Returns:
        StructureGraph: pymatgen StructureGraph object.
    """
    space_group = int(vesta_dict["GROUP"].split(" ")[0])
    lattice = [float(i) for i in vesta_dict["CELLP"].split("\n")[0].split(" ") if i != ""]
    sites = [[j for j in i.split(" ") if j != ""] for i in vesta_dict["STRUC"].split("\n")[:-1:2]]
    species = [i[1] for i in sites]
    coords = [[float(i[4]), float(i[5]), float(i[6])] for i in sites]

    lattice = Lattice.from_parameters(*lattice)
    structure = Structure.from_spacegroup(space_group, lattice, species, coords)

    sga = SpacegroupAnalyzer(structure)
    symmetrized = sga.get_symmetrized_structure()
    env = MinimumDistanceNN()
    graph = StructureGraph.with_local_env_strategy(symmetrized, env)

    return graph
