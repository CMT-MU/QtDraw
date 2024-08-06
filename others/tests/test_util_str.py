"""
Test for utility.

This module provides a test for utility.
"""

import numpy as np
from qtdraw.util.util_str import (
    str_to_list,
    is_regular_list,
    apply_to_list,
    apply_to_numpy,
    to_fraction,
    str_to_sympy,
    get_variable,
    affine_trans,
)

# ==================================================
# test
list_0d = "normal string."
list_1d = "[normal string.]"
vector_1d = "[a b, d, def g]"
matrix_2d = "[[a b, d, def g],[4, i j, 6],[7, 8, 9]]"
cube_3d = "[[[1, 2, 3],[4, 5, 6],[7, 8, 9]],[[10, 11, 12],[13, 14, 15],[16, 17, 18]],[[19, 20, 21],[22, 23, 24],[25, 26, 27]]]"
rectangle_2d = "[[1, 2, 3],[4, 5, 6]]"
rectangle_3d = "[[[1, 2],[3, 4]],[[5, 6],[7, 8]]]"
test1 = [list_0d, list_1d, vector_1d, matrix_2d, cube_3d, rectangle_2d, rectangle_3d]

irregular_list = "[[apple pen,  what is orange, banana],[, , pear a],[  grape, [   kiwi s, , a pineapple, this is watermelon]] ]"
non_square_matrix_2d = "[[1, 2, 3],[4, 5],[6, 7, 8, 9]]"
non_cube_3d = "[[[1, 2, 3],[4, 5, 6],[7, 8, 9]],[[10, 11, 12],[13, 14],[15, 16, 17]],[[18, 19],[20, 21, 22],[23, 24, 25]]]"
different_rows_2d = "[[1, 2, 3],[4, 5],[6, 7, 8]]"
different_columns_2d = "[[1, 2],[3, 4, 5],[6, 7]]"
test2 = [irregular_list, non_square_matrix_2d, non_cube_3d, different_rows_2d, different_columns_2d]


# ==================================================
def test_str_to_list():
    print("=== test_str_to_list ===")
    for i in test1:
        print(str_to_list(i))
    for i in test2:
        print(str_to_list(i))


# ==================================================
def test_is_regular_list():
    print("=== test_is_regular_list ===")
    for i in test1:
        print(is_regular_list(str_to_list(i)))
    for i in test2:
        print(is_regular_list(str_to_list(i)))


# ==================================================
def test_apply_to_list():
    print("=== test_apply_to_list ===")
    for i in test1:
        print(apply_to_list(lambda x: len(x), str_to_list(i)))
    for i in test2:
        print(apply_to_list(lambda x: len(x), str_to_list(i)))
    for i in test1:
        print(apply_to_numpy(lambda x: len(x), np.array(str_to_list(i))))


# ==================================================
def test_to_fraction():
    print("=== test_to_fraction ===")
    data = [0.25, 0.3333333333333333, np.pi, np.e]
    for i in data:
        print(to_fraction(i))


# ==================================================
def test_str_to_sympy():
    print("=== test_str_to_sympy ===")
    test = ["x+y", "a", "1.3", "2 sqrt(3)/3", "sin(x)", "0.5cos(y)", "3+x"]
    var = ["x", "y", "z"]
    for i in test:
        v = get_variable(str_to_sympy(i))
        s1 = str_to_sympy(i, var, rational=False)
        s2 = str_to_sympy(i, var, rational=True)
        s3 = str_to_sympy(i, var, subs={"x": 0.1})
        print(f"{i} {v} => {s1}, {s2}, {s3}")


# ==================================================
def test_affine_trans():
    print("=== test_affine_trans ===")
    test = [
        "[1,2,3]",
        "[1,a,b]",
        "[x,y,1]",
        "[1/2, sin(pi/3),0.3]",
        "[1,2,3]@[1,2,3]",
        "[x,y,1];[x,y,1]",
        "[1/2, sin(pi/3),0.3]:[1/2, sin(pi/3),0.3]",
        "[1,2]",
        "[1,2,3]*[3,1,2]",
        "[1,a,b]",
    ]
    A = "[[1,-1/2,0],[0,sqrt(3)/2,0],[0,0,1]]"
    cell = "[1,1,1]"

    for i in test:
        s1 = affine_trans(i)
        s2 = affine_trans(i, cell)
        s3 = affine_trans(i, A=A)
        s4 = affine_trans(i, cell, A)
        print(f"{i} => {s1}, {s2}, {s3}, {s4}")

    test1 = "[1,1,1]"
    test2 = "[[1,1,1],[2,2,2]]"
    cell1 = "[1/2,1/2,0]"
    cell2 = "[[1/2,1/2,0],[0,1/2,1/2]]"
    print(affine_trans(test1, cell2, A))
    print(affine_trans(test2, cell1, A))
    print(affine_trans(test2, cell2, A))


# ==================================================
test_str_to_list()
test_is_regular_list()
test_apply_to_list()
test_to_fraction()
test_str_to_sympy()
test_affine_trans()
