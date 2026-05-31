import pytest

from financial_calculators.inflation import (
    adjusted_value_after_inflation,
    future_cost_after_inflation,
)


def test_adjusted_value_after_inflation_reduces_purchasing_power():
    assert adjusted_value_after_inflation(100, 0.10, 1) == pytest.approx(90.9091)


def test_future_cost_after_inflation_increases_nominal_cost():
    assert future_cost_after_inflation(100, 0.10, 1) == pytest.approx(110)


def test_inflation_rejects_invalid_inputs():
    with pytest.raises(ValueError):
        adjusted_value_after_inflation(100, -1, 10)

