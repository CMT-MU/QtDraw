"""
Test for utility.

This module provides a test for utility.
"""

from qtdraw.util.util import str_to_list

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
test_str_to_list()
