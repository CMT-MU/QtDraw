from qtpy.QtGui import QDoubleValidator, QRegExpValidator, QValidator
from qtpy.QtCore import QRegExp
from qtdraw.core.pixmap_converter import _latex2pixmap


"""
regular-expression patterns.
    - see, https://regexlib.com/CheatSheet.aspx
"""
# scalar.
int_ptn = "[+-]?[0-9]+"
float_ptn = "[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)"
str_ptn = "[^\[\],\"']*"  # except [],"
int_pos_ptn = "[+]?[0-9]+"
float_pos_ptn = "[+]?([0-9]+([.][0-9]*)?|[.][0-9]+)"

# 3-component vector.
int_vector_ptn = "^\[(" + int_ptn + ",){2}" + int_ptn + "\]$"
int_pos_vector_ptn = "^\[(" + int_pos_ptn + ",){2}" + int_pos_ptn + "\]$"
float_vector_ptn = "^\[(" + float_ptn + ",){2}" + float_ptn + "\]$"
float_pos_vector_ptn = "^\[(" + float_pos_ptn + ",){2}" + float_pos_ptn + "\]$"
str_vector_ptn = "^\[(" + str_ptn + ",){2}" + str_ptn + "\]$"

# list.
int_list_ptn = "^\[(" + int_ptn + ",)*" + int_ptn + "\]$"
int_pos_list_ptn = "^\[(" + int_pos_ptn + ",)*" + int_pos_ptn + "\]$"
float_list_ptn = "^\[(" + float_ptn + ",)*" + float_ptn + "\]$"
float_pos_list_ptn = "^\[(" + float_pos_ptn + ",)*" + float_pos_ptn + "\]$"
str_list_ptn = "^\[(" + str_ptn + ",)*" + str_ptn + "\]$"

# list of 3-component vector.
int_vector_list_ptn = "^\[(" + int_vector_ptn[1:-1] + ",)*" + int_vector_ptn[1:-1] + "\]$"
int_pos_vector_list_ptn = "^\[(" + int_pos_vector_ptn[1:-1] + ",)*" + int_pos_vector_ptn[1:-1] + "\]$"
float_vector_list_ptn = "^\[(" + float_vector_ptn[1:-1] + ",)*" + float_vector_ptn[1:-1] + "\]$"
float_pos_vector_list_ptn = "^\[(" + float_pos_vector_ptn[1:-1] + ",)*" + float_pos_vector_ptn[1:-1] + "\]$"
str_vector_list_ptn = "^\[(" + str_vector_ptn[1:-1] + ",)*" + str_vector_ptn[1:-1] + "\]$"

# list of list.
int_list_list_ptn = "^\[(" + int_list_ptn[1:-1] + ",)*" + int_list_ptn[1:-1] + "\]$"
int_pos_list_list_ptn = "^\[(" + int_pos_list_ptn[1:-1] + ",)*" + int_pos_list_ptn[1:-1] + "\]$"
float_list_list_ptn = "^\[(" + float_list_ptn[1:-1] + ",)*" + float_list_ptn[1:-1] + "\]$"
float_pos_list_list_ptn = "^\[(" + float_pos_list_ptn[1:-1] + ",)*" + float_pos_list_ptn[1:-1] + "\]$"
str_list_list_ptn = "^\[(" + str_list_ptn[1:-1] + ",)*" + str_list_ptn[1:-1] + "\]$"


class UnitValidator(QDoubleValidator):
    def __init__(self, parent=None):
        super().__init__(0.0, 1.0, 0, parent)
        self.setNotation(QDoubleValidator.StandardNotation)


class LaTeXValidator(QValidator):
    def __init__(self, parent=None):
        super().__init__(parent)

    def validate(self, text, pos):
        if text.count("$"):
            text = text.strip("$")
            flag = _latex2pixmap(text)
            if flag is None:
                return QValidator.Invalid, text, pos
            else:
                text = "$" + text + "$"
        return QValidator.Acceptable, text, pos


"""
validator mapping.
"""
validator_map = {
    "int": int_ptn,
    "real": float_ptn,
    "string": str_ptn,
    "int_positive": int_pos_ptn,
    "real_positive": float_pos_ptn,
    "real_unit": "real_unit",
    "latex": "latex",
    #
    "i_scalar": int_ptn,
    "i_pos_scalar": int_pos_ptn,
    "i_row": int_list_ptn,
    "i_pos_row": int_pos_list_ptn,
    "i_column": int_list_ptn,
    "i_pos_column": int_pos_list_ptn,
    "i_matrix": int_list_list_ptn,
    "i_pos_matrix": int_pos_list_list_ptn,
    "i_vector": int_vector_ptn,
    "i_pos_vector": int_pos_vector_ptn,
    "i_column_vector": int_vector_ptn,
    "i_pos_column_vector": int_pos_vector_ptn,
    "i_vector_list": int_vector_list_ptn,
    "i_pos_vector_list": int_pos_vector_list_ptn,
    #
    "r_scalar": float_ptn,
    "r_pos_scalar": float_pos_ptn,
    "r_row": float_list_ptn,
    "r_pos_row": float_pos_list_ptn,
    "r_column": float_list_ptn,
    "r_pos_column": float_pos_list_ptn,
    "r_matrix": float_list_list_ptn,
    "r_pos_matrix": float_pos_list_list_ptn,
    "r_vector": float_vector_ptn,
    "r_pos_vector": float_pos_vector_ptn,
    "r_column_vector": float_vector_ptn,
    "r_pos_column_vector": float_pos_vector_ptn,
    "r_vector_list": float_vector_list_ptn,
    "r_pos_vector_list": float_pos_vector_list_ptn,
    #
    "s_scalar": str_ptn,
    "s_row": str_list_ptn,
    "s_column": str_list_ptn,
    "s_matrix": str_list_list_ptn,
    "s_vector": str_vector_ptn,
    "s_column_vector": str_vector_ptn,
    "s_vector_list": str_vector_list_ptn,
}


def create_validator(validator):
    """
    create validator.

    Args:
        validator (str): name of validator. see, validator_map.keys()

    Returns:
        QValidator: validator.
    """
    if validator == "real_unit":
        return UnitValidator()
    elif validator == "latex":
        return LaTeXValidator()
    else:
        return QRegExpValidator(QRegExp(validator_map[validator]))
