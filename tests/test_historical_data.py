import pytest

from financial_calculators.historical_data import load_historical_years


def test_load_historical_years_parses_percent_and_decimal_rates(tmp_path):
    csv_path = tmp_path / "history.csv"
    csv_path.write_text(
        "year,return_rate,inflation_rate\n"
        "2021,12,5\n"
        "2020,0.08,0.04\n",
        encoding="utf-8",
    )

    years = load_historical_years(csv_path)

    assert [item.year for item in years] == [2020, 2021]
    assert years[0].return_rate == pytest.approx(0.08)
    assert years[1].inflation_rate == pytest.approx(0.05)


def test_load_historical_years_requires_expected_columns(tmp_path):
    csv_path = tmp_path / "history.csv"
    csv_path.write_text("year,return_rate\n2020,8\n", encoding="utf-8")

    with pytest.raises(ValueError, match="CSV must include columns"):
        load_historical_years(csv_path)

