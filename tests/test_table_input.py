"""
Values accepted by the editors of the data table must be drawn without errors.

The editor of a cell checks its text with the validator of the column, and the table stores the text as typed. Each value
below is tried in every column with an editor; a value that the validator accepts must be drawn, saved and read again.
"""

import pytest

from qtdraw.core.pyvista_widget_setting import object_default
from qtdraw.widget.validator import (
    validator_float,
    validator_int,
    validator_list_float,
    validator_list_int,
    validator_math,
)

VALIDATORS = {
    "int": validator_int,
    "float": validator_float,
    "list_int": validator_list_int,
    "list_float": validator_list_float,
    "math": validator_math,
}
# extreme but finite values (e.g. 1e-9 or 1e9) are not tried: some shapes take minutes to be made with them.
NUMBERS = ["0", "1", "-1", "0.5", "-0", "2/3", "pi", "sqrt(2)", "nan", "inf", "-inf", "1e400", "10**400", "I", "oo", "x"]
LISTS = ["[]", "[[]]", "[[],[],[]]", "[0,0]", "[[0,0],[0,0]]"]

# accepted values that are not drawn yet: an object without a direction or size (zero vector, length or step).
# such a column has the value zero, e.g. "[0,0,0]" or "-0".
DEGENERATE = {
    ("bond", "direction"): "[0,0,0]",
    ("line", "direction"): "[0,0,0]",
    ("plane", "normal"): "[0,0,0]",
    ("circle", "normal"): "[0,0,0]",
    ("torus", "normal"): "[0,0,0]",
    ("ellipsoid", "normal"): "[0,0,0]",
    ("toroid", "normal"): "[0,0,0]",
    ("text3d", "view"): "[0,0,0]",
    ("stream", "shape"): "0",
    ("stream", "vector"): "[0,0,0]",
    ("stream", "size"): "0",
    ("stream", "length"): "0",
    ("spline_t", "t_range"): "[0,0,0]",
}


def values(vtype, option):
    """
    Values to try in a column: single numbers, and lists made of one number repeated to the shape of the column.
    """
    shape = option.get("shape")
    if vtype not in ("list_int", "list_float", "math") or not shape:
        return NUMBERS + LISTS

    def nested(number, shape):
        if not shape:
            return number
        n = shape[0] if shape[0] > 0 else 2  # 0 means any length.
        return "[" + ",".join(nested(number, shape[1:]) for _ in range(n)) + "]"

    return [nested(number, tuple(shape)) for number in NUMBERS] + LISTS


def is_zero(text):
    return set(text) <= set("[],-0")


COLUMNS = [
    (object_type, column, vtype, option)
    for object_type, columns in object_default.items()
    for column, (vtype, option, default) in columns.items()
    if vtype in VALIDATORS
]


# ==================================================
@pytest.mark.parametrize("vtype", sorted(VALIDATORS))
@pytest.mark.parametrize("text", NUMBERS + LISTS)
def test_validator_returns_text_or_none(vtype, text):
    for option in [{}, {"shape": (0,)}, {"shape": (3,)}, {"shape": (0, 0)}, {"min": 0, "max": "*"}]:
        if "shape" in option and vtype in ("int", "float"):
            continue
        result = VALIDATORS[vtype](text, **option)
        assert result is None or isinstance(result, str)


@pytest.mark.parametrize("text", ["nan", "inf", "-inf", "1e400", "NaN", "Infinity"])
def test_float_rejects_values_that_are_not_finite(text):
    assert validator_float(text) is None
    assert validator_float(text, min=0.0, max="*") is None


@pytest.mark.parametrize("text", ["[nan,0,0]", "[1e400,0,0]", "[oo,0,0]", "[zoo,0,0]", "[I,0,0]", "[10**400,0,0]"])
def test_list_float_rejects_values_that_are_not_finite_real_numbers(text):
    assert validator_list_float(text, shape=(3,), var=[""], digit=4) is None


@pytest.mark.parametrize("text", ["[]", "[[]]"])
def test_list_float_rejects_an_empty_list(text):
    assert validator_list_float(text, shape=(0,), var=[""], digit=4) is None
    assert validator_list_float(text) is None


@pytest.mark.parametrize("text", ["[0.5,1]", "[pi,1]", "[1/2,1]", "[I,1]", "[oo,1]", "[10**400,1]"])
def test_list_int_rejects_values_that_are_not_integers(text):
    assert validator_list_int(text, shape=(2,)) is None


@pytest.mark.parametrize("text, expected", [("[1,2]", "[1,2]"), ("[4/2,-3]", "[2,-3]"), ("[1.0,0]", "[1,0]")])
def test_list_int_accepts_integers(text, expected):
    assert validator_list_int(text, shape=(2,)) == expected


def test_int_rejects_values_beyond_64_bits():
    assert validator_int("9" * 30) is None
    assert validator_int("12") == "12"


@pytest.mark.parametrize("object_type, column, vtype, option", COLUMNS, ids=[f"{t}.{c}" for t, c, _, _ in COLUMNS])
def test_default_value_is_accepted(object_type, column, vtype, option):
    default = object_default[object_type][column][2]
    assert VALIDATORS[vtype](default, **option) is not None


@pytest.mark.parametrize("object_type", ["polygon", "spline"])
def test_points_of_any_number_are_accepted(object_type):
    vtype, option, default = object_default[object_type]["point"]
    assert validator_list_float("[[0,0,0],[1,0,0],[1,1,0],[0,1,0]]", **option) is not None
    assert validator_list_float("[[0,0],[1,0],[1,1]]", **option) is None  # 2 components.


def test_faces_of_different_sizes_are_accepted():
    vtype, option, default = object_default["polygon"]["connectivity"]
    assert validator_list_int("[[0,1,2,3],[0,1,4]]", **option) == "[[0,1,2,3],[0,1,4]]"
    assert validator_list_int("[[[0]],[1]]", **option) is None  # deeper than a list of faces.


# ==================================================
@pytest.mark.parametrize("object_type, column, vtype, option", COLUMNS, ids=[f"{t}.{c}" for t, c, _, _ in COLUMNS])
def test_accepted_value_is_drawn(widget, qtbot, tmp_path, object_type, column, vtype, option):
    getattr(widget, f"add_{object_type}")()
    model = widget._data[object_type]
    i = list(object_default[object_type]).index(column)
    accepted = []
    for text in values(vtype, option):
        if VALIDATORS[vtype](text, **option) is None or ((object_type, column) in DEGENERATE and is_zero(text)):
            continue
        accepted.append(text)
        file = tmp_path / "a.qtdw"
        with qtbot.capture_exceptions() as exceptions:
            model.setData(model.index(0, i), text)  # as the editor of the table does.
            widget.render()
            widget.save(str(file))
            widget.load(str(file))
        assert not exceptions, f"{object_type}.{column} = {text!r}: {exceptions[0][1]!r}"
        model = widget._data[object_type]
        assert model.index(0, i).data() == text  # the text is kept as typed.
    assert accepted, f"no value is accepted for {object_type}.{column}."


@pytest.mark.xfail(strict=True, reason="an object without a direction or size is not handled yet.")
@pytest.mark.parametrize("object_type, column", sorted(DEGENERATE), ids=[f"{t}.{c}" for t, c in sorted(DEGENERATE)])
def test_degenerate_value_is_drawn(widget, qtbot, object_type, column):
    getattr(widget, f"add_{object_type}")()
    model = widget._data[object_type]
    vtype, option, default = object_default[object_type][column]
    text = DEGENERATE[(object_type, column)]
    assert VALIDATORS[vtype](text, **option) is not None
    with qtbot.capture_exceptions() as exceptions:
        model.setData(model.index(0, list(object_default[object_type]).index(column)), text)
        widget.render()
    assert not exceptions, repr(exceptions[0][1])


@pytest.mark.parametrize("text", ["0", "-0", "1"])
def test_size_of_latex_text2d_is_drawn(widget, qtbot, text):
    widget.add_text2d("$x^2$")
    model = widget._data["text2d"]
    vtype, option, default = object_default["text2d"]["size"]
    if VALIDATORS[vtype](text, **option) is None:
        return
    with qtbot.capture_exceptions() as exceptions:
        model.setData(model.index(0, list(object_default["text2d"]).index("size")), text)
        widget.render()
    assert not exceptions, repr(exceptions[0][1])


def test_hint_tells_that_faces_may_differ_in_length():
    from qtdraw.widget.validator import validator_hint

    vtype, option, default = object_default["polygon"]["connectivity"]
    assert "different lengths" in validator_hint(vtype, option)
    vtype, option, default = object_default["polygon"]["point"]
    assert "different lengths" not in validator_hint(vtype, option)


@pytest.mark.parametrize("text", ["[[Max(0,1),2,3]]", "[[0,1,2],]", "[[4/2,0,1],[0,1,3,4]]"])
def test_faces_with_expressions_are_drawn(widget, qtbot, text):
    widget.add_polygon()
    model = widget._data["polygon"]
    vtype, option, default = object_default["polygon"]["connectivity"]
    assert validator_list_int(text, **option) is not None
    with qtbot.capture_exceptions() as exceptions:
        model.setData(model.index(0, list(object_default["polygon"]).index("connectivity")), text)
        widget.render()
    assert not exceptions, repr(exceptions[0][1])


@pytest.mark.parametrize("text", ["I", "1+2*I", "exp(I*pi/3)"])
def test_modulation_coefficient_may_be_complex(text):
    from qtdraw.multipie.multipie_modulation_dialog import modulation_panel

    vtype, option, default = modulation_panel["coeff"]
    assert VALIDATORS[vtype](text, **option) is not None


@pytest.mark.parametrize("text", ["nan", "oo", "zoo"])
def test_modulation_coefficient_is_finite(text):
    from qtdraw.multipie.multipie_modulation_dialog import modulation_panel

    vtype, option, default = modulation_panel["coeff"]
    assert VALIDATORS[vtype](text, **option) is None


@pytest.mark.parametrize("object_type, column", [("orbital", "shape"), ("orbital", "surface"), ("stream", "shape")])
def test_constant_shape_is_real(object_type, column):
    vtype, option, default = object_default[object_type][column]
    assert VALIDATORS[vtype]("I", **option) is None
    assert VALIDATORS[vtype]("I*x", **option) is not None  # the magnitude of a complex function is drawn.


def test_constant_stream_vector_is_real():
    vtype, option, default = object_default["stream"]["vector"]
    assert VALIDATORS[vtype]("[I,0,0]", **option) is None
