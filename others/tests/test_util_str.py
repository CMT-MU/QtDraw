"""
Test for utility.

This module provides a test for utility.
"""

from qtdraw.util.util import str_to_list, affine_trans

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
test_affine_trans()
