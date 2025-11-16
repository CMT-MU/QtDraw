"""
Test for utility.

This module provides a test for utility.
"""

from qtdraw.sandbox.util import str_to_sympy, to_latex


# ==================================================
def test_str_to_sympy():
    print("=== test_str_to_sympy ===")
    test = ["x+y", "a", "1.3", "2 sqrt(3)/3", "sin(x)", "0.5cos(y)", "3+x"]
    var = ["x", "y", "z", "a"]
    for i in test:
        s1 = str_to_sympy(i, var, rational=False)
        s2 = str_to_sympy(i, var, rational=True)
        s3 = str_to_sympy(i, var, subs={"x": 0.1})
        print(f"{i} => {s1}, {s2}, {s3}")


# ==================================================
def test_to_latex():
    print("=== test_to_latex ===")
    test = ["x+y", "a", "1.3", "2 sqrt(3)/3", "sin(x)", "0.5cos(y)", "3+x"]
    for i in test:
        s1 = to_latex(str_to_sympy(i))
        print(f"{i} => {s1}")


# ==================================================
test_str_to_sympy()
test_to_latex()
