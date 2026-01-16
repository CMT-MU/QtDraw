"""
Default setting for MultiPie plugin.
"""

# ==================================================
default_status = {
    "group": {
        "tag": "C1",
        "find_wyckoff": "[0,0,0]",
    },
    "object": {
        "site": "[1/3,2/3,0]",
        "bond": "[0,0,0];[1,0,0]",
        "vector_type": "Q",
        "vector": "[0,0,1] # [1/3,2/3,0]",
        "vector_average": False,
        "vector_cartesian": True,
        "orbital_type": "Q",
        "orbital": "x # [0,0,0];[1,0,0]",
        "orbital_average": False,
    },
    "basis": {
        "bond_definition": "[0,0,0];[1,0,0]",
        "site": "[1/3,2/3,0]",
        "bond": "[0,0,0];[1,0,0]",
        "vector_type": "Q",
        "vector": "[1/3,2/3,0]",
        "vector_lc": "Q01",
        "vector_modulation": "",
        "orbital_type": "Q",
        "orbital_rank": 0,
        "orbital": "[0,0,0];[1,0,0]",
        "orbital_lc": "Q01",
        "orbital_modulation": "",
    },
    "counter": {},
}


# ==================================================
setting_detail = {
    "site": {"size": 0.05, "color": "silver", "opacity": 1.0, "width": 0.01},
    "bond": {"width": 0.01, "color1": "silver", "color2": "iron", "opacity": 1.0},
    "vector": {
        "length": 0.3,
        "width": 0.02,
        "color": {"Q": "orange", "M": "lightskyblue", "T": "hotpink", "G": "yellowgreen"},
        "opacity": 1.0,
    },
    "orbital": {"size": 0.2, "color": {"Q": "Wistia", "M": "GnBu", "T": "coolwarm", "G": "PiYG"}, "opacity": 1.0},
    "site_samb": {"color": "silver", "color_neg": "aqua", "color_pos": "salmon", "zero_size": 0.5, "size_ratio": 0.2},
    "bond_samb": {
        "length": 0.2,
        "width": 0.03,
        "width_ratio": 0.07,
        "opacity": 0.7,
        "color": "white",
        "color_neg": "aqua",
        "color_pos": "salmon",
        "arrow_color": "black",
        "arrow_color_rep": "red",
        "arrow_ratio": 0.7,
    },
}
