import pytest

from financial_calculators.historical_data import load_historical_years
from financial_calculators.india_data import (
    annual_closes_from_nse_tri_rows,
    annual_returns_from_closes,
    combine_india_history,
)


def test_annual_returns_from_nse_tri_rows_uses_last_available_date():
    rows = [
        {"Date": "30 Dec 2020", "TotalReturnsIndex": "100.00"},
        {"Date": "31 Dec 2020", "TotalReturnsIndex": "110.00"},
        {"Date": "30 Dec 2021", "TotalReturnsIndex": "121.00"},
        {"Date": "31 Dec 2021", "TotalReturnsIndex": "120.00"},
    ]

    closes = annual_closes_from_nse_tri_rows(rows)
    returns = annual_returns_from_closes(closes)

    assert closes[2020].value == 110
    assert closes[2021].value == 120
    assert returns[2021] == pytest.approx((120 / 110) - 1)


def test_combine_india_history_keeps_only_years_with_both_series():
    history = combine_india_history(
        return_rates={2020: 0.10, 2021: 0.12},
        inflation_rates={2021: 0.05, 2022: 0.04},
    )

    assert len(history) == 1
    assert history[0].year == 2021
    assert history[0].return_rate == pytest.approx(0.12)
    assert history[0].inflation_rate == pytest.approx(0.05)


def test_committed_india_dataset_loads_for_historical_replay():
    history = load_historical_years("data/india/nifty50_tri_cpi_annual.csv")

    assert history[0].year == 2000
    assert history[-1].year == 2024
    assert len(history) == 25
    assert any(item.year == 2008 and item.return_rate < -0.50 for item in history)
