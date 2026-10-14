"""validator 模块单元测试"""

import pytest

from core.validator import (
    ValidationError,
    validate,
    validate_blue,
    validate_red,
)


class TestValidateRed:
    def test_valid(self):
        validate_red([1, 2, 3, 4, 5, 6])

    def test_wrong_count(self):
        with pytest.raises(ValidationError):
            validate_red([1, 2, 3, 4, 5])

    def test_out_of_range_low(self):
        with pytest.raises(ValidationError):
            validate_red([0, 2, 3, 4, 5, 6])

    def test_out_of_range_high(self):
        with pytest.raises(ValidationError):
            validate_red([1, 2, 3, 4, 5, 34])

    def test_duplicate(self):
        with pytest.raises(ValidationError):
            validate_red([1, 1, 3, 4, 5, 6])

    def test_non_integer(self):
        with pytest.raises(ValidationError):
            validate_red([1, 2, 3, 4, 5, "6"])


class TestValidateBlue:
    def test_valid(self):
        validate_blue(1)
        validate_blue(16)

    def test_out_of_range(self):
        with pytest.raises(ValidationError):
            validate_blue(0)
        with pytest.raises(ValidationError):
            validate_blue(17)

    def test_non_integer(self):
        with pytest.raises(ValidationError):
            validate_blue("7")


def test_validate():
    validate([1, 2, 3, 4, 5, 6], 7)
    with pytest.raises(ValidationError):
        validate([1, 2, 3, 4, 5, 6], 17)