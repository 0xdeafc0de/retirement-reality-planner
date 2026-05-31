import pytest

from financial_calculators.corpus import simulate_corpus_longevity


def test_corpus_longevity_exhausts_when_withdrawals_exceed_growth():
    result = simulate_corpus_longevity(
        initial_corpus=1_200,
        annual_expense=1_200,
        annual_return_rate=0,
        annual_inflation_rate=0,
    )

    assert result.exhausted is True
    assert result.months_survived == 12


def test_corpus_longevity_can_survive_full_horizon():
    result = simulate_corpus_longevity(
        initial_corpus=1_200,
        annual_expense=0,
        annual_return_rate=0.05,
        annual_inflation_rate=0,
        max_years=2,
    )

    assert result.exhausted is False
    assert result.months_survived == 24
    assert result.ending_corpus > 1_200


def test_corpus_longevity_rejects_invalid_inputs():
    with pytest.raises(ValueError):
        simulate_corpus_longevity(
            initial_corpus=-1,
            annual_expense=1_200,
            annual_return_rate=0.05,
            annual_inflation_rate=0,
        )
