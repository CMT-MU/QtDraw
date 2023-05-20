IMAGEFILE = __file__[: __file__.rfind("/")] + "/fig.jpg"


test_data1 = {
    "test": (
        ["name", "number", "number-col", "image", "math", "color", "colormap", "radioH", "radioV", "combo", "D", "check", "D1"],
        [
            ("check", "D", "", "test"),  # check-status column, actor-column, default
            ("text", 1.0),
            ("text", "r_column", [1.0, 2.0, 3.0]),
            ("image", IMAGEFILE),
            ("math", "1"),
            ("color", "red"),
            ("colormap", "coolwarm"),
            ("radio", ["a", "b", "c"], "H", 0),
            ("radio", ["A", "B", "C"], "V", 0),
            ("combo", ["c1", "c2", "c3"], 0),
            ("text", True),
            ("check_edit", "D1", "", "chk"),
            ("text", True),
        ],
        [["name1", 1 + 2j, [1, 2, 3], IMAGEFILE, "1/3", "strawberry", "coolwarm", 1, 2, 1, True, "show", False]],
    ),
}

test_data2 = {
    "site": (
        ["name", "math", "D"],
        [("check", "D", "", "site"), ("math", "x y"), ("check", True)],
        [
            [
                "Te",
                r"\frac{\partial^2 u}{\partial t^2}=c^2\left(\frac{\partial^2 u}{\partial x^2}+\frac{\partial^2 u}{\partial y^2}\right)",
                True,
            ],
            ["Te", "x y z", False],
            ["Sn", r"\begin{pmatrix} a & b \\ c & d \end{pmatrix}", False],
            ["Sn", r"\sqrt{3}", False],
            ["U", r"\sqrt{3}", True],
        ],
    ),
    "orbital": (
        ["name", "position", "shape", "D", "scale"],
        [
            ("check", "D", "", "orbital"),
            ("text", "r_vector", [0.0, 0.0, 0.0]),
            ("math", "s_scalar", "sin(x)"),
            ("hide", True),
            ("check", "scale", "", False),
        ],
        [["dv", [0, 1, 2], "cos(y)", False, False]],
    ),
}
