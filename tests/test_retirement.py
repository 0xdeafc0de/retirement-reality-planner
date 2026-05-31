import pytest

from financial_calculators.retirement import simulate_monte_carlo_retirement


def test_monte_carlo_is_reproducible_with_seed():
    first = simulate_monte_carlo_retirement(
        initial_corpus=1_000_000,
        annual_expense=50_000,
        years=20,
        simulations=100,
        seed=42,
    )
    second = simulate_monte_carlo_retirement(
        initial_corpus=1_000_000,
        annual_expense=50_000,
        years=20,
        simulations=100,
        seed=42,
    )

    assert first.success_rate == second.success_rate
    assert first.median_ending_corpus == second.median_ending_corpus
    assert first.ending_corpus_p10 == second.ending_corpus_p10


def test_monte_carlo_succeeds_when_there_are_no_expenses():
    summary = simulate_monte_carlo_retirement(
        initial_corpus=1_000,
        annual_expense=0,
        years=10,
        simulations=25,
        seed=1,
    )

    assert summary.success_rate == 1
    assert summary.earliest_failure_year is None


def test_monte_carlo_reports_failure_years():
    summary = simulate_monte_carlo_retirement(
        initial_corpus=1_000,
        annual_expense=600,
        years=5,
        simulations=10,
        return_mean=0,
        return_volatility=0,
        inflation_mean=0,
        inflation_volatility=0,
        crash_probability=0,
    )

    assert summary.success_rate == 0
    assert summary.earliest_failure_year == 2
    assert summary.median_failure_year == 2


def test_monte_carlo_rejects_invalid_inputs():
    with pytest.raises(ValueError):
        simulate_monte_carlo_retirement(
            initial_corpus=1_000,
            annual_expense=100,
            years=0,
        )
