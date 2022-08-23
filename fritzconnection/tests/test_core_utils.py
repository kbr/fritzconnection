
import pytest


from ..core.utils import (
    boolean_from_string,
    get_boolean_from_string,
)


@pytest.mark.parametrize(
    "value, expected_result", [
        ("True", True),
        ("TRUE", True),
        ("false", False),
        ("fAlSe", False),
        ("On", True),
        ("Off", False),
        ("1", True),
        ("0", False),
    ]
)
def test_boolean_from_string(value, expected_result):
    """
    Test to get a real boolean and not a string.
    """
    result = boolean_from_string(value)
    assert result == expected_result


@pytest.mark.parametrize(
    "value", [
        "wahr",
        "falsch",
        "l",
        "10",
        "01",
        "",
        "None",
    ]
)
def test_boolean_from_string_valueerror(value):
    with pytest.raises(ValueError):
        boolean_from_string(value)


@pytest.mark.parametrize(
    "value", [
        True,
        False,
        None,
        42,
    ]
)
def test_boolean_from_string_typeerror(value):
    with pytest.raises(AttributeError):
        boolean_from_string(value)


@pytest.mark.parametrize(
    "value, expected_result", [
        ("true", True),
        ("false", False),
        ("wahr", None),
        ("falsch", None),
        ("None", None),
        (42, None),
        ("", None),
        (None, None),
    ]
)
def test_get_boolean_from_string(value, expected_result):
    result = get_boolean_from_string(value)
    assert result == expected_result
