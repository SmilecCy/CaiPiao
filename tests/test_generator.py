"""generator 模块单元测试"""

from core.generator import generate, generate_many
from core.validator import validate


class TestGenerate:
    def test_returns_valid_ticket(self):
        red, blue = generate()
        validate(red, blue)

    def test_red_sorted(self):
        red, _ = generate()
        assert red == sorted(red)

    def test_red_has_no_duplicates(self):
        red, _ = generate()
        assert len(set(red)) == len(red) == 6

    def test_blue_in_range(self):
        _, blue = generate()
        assert 1 <= blue <= 16

    def test_seed_reproducible(self):
        a = generate(seed=42)
        b = generate(seed=42)
        assert a == b


class TestGenerateMany:
    def test_count(self):
        tickets = generate_many(5)
        assert len(tickets) == 5
        for red, blue in tickets:
            validate(red, blue)

    def test_invalid_count(self):
        import pytest

        with pytest.raises(ValueError):
            generate_many(0)