"""
This file manages setting of QtDraw with MultiPie and its viewer style.
"""


# ==================================================
rcParams = {
    "group_tag": "C1",
    "show_label": False,
    "site_color": "darkseagreen",
    "bond_color1": "silver",
    "bond_color2": "iron",
    "vector_color_Q": "orange",
    "vector_color_M": "lightskyblue",
    "vector_color_T": "hotpink",
    "vector_color_G": "yellowgreen",
    "orbital_color_Q": "Wistia",
    "orbital_color_M": "GnBu",
    "orbital_color_T": "coolwarm",
    "orbital_color_G": "PiYG",
}


# ==================================================
default_style = {
    "site": [  # (color, size, opacity)
        ("darkseagreen", 1.0, 1.0),  # 1st site
        ("lightblue", 1.0, 1.0),  # 2nd site
        ("sandybrown", 1.0, 1.0),  # 9th site
        ("gold", 1.0, 1.0),  # 3rd site
        ("darkkhaki", 1.0, 1.0),  # 4th site
        ("skyblue", 1.0, 1.0),  # 7th site
        ("thistle", 1.0, 1.0),  # 6th site
        ("darkgrey", 1.0, 1.0),  # 8th site
        ("burlywood", 1.0, 1.0),  # 5th site
        ("ghostwhite", 1.0, 1.0),  # other sites
    ],
    "bond": [  # ((tail-color, head-color), width, opacity)
        (("snow", "silver"), 1.0, 1.0),  # 1st neighbor
        (("lightcyan", "lightsteelblue"), 1.0, 1.0),  # 2nd neighbor
        (("antiquewhite", "burlywood"), 1.0, 1.0),  # 3rd neighbor
        (("palegoldenrod", "darkseagreen"), 1.0, 1.0),  # 4th neighbor
        (("mistyrose", "lightpink"), 1.0, 1.0),  # 5th neighbor
        (("aliceblue", "lightblue"), 1.0, 1.0),  # 6th neighbor
        (("wheat", "sandybrown"), 1.0, 1.0),  # 7th neighbor
        (("seashell", "thistle"), 1.0, 1.0),  # 8th neighbor
        (("cornsilk", "peachpuff"), 1.0, 1.0),  # 9th neighbor
        (("whitesmoke", "darkkhaki"), 1.0, 1.0),  # other neighbors
    ],
}
