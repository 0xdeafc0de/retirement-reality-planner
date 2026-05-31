"""Corpus longevity calculations for retirement planning."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CorpusLongevityResult:
    """Result of a corpus longevity simulation."""

    months_survived: int
    ending_corpus: float
    ending_monthly_expense: float
    exhausted: bool

    @property
    def years_survived(self) -> int:
        return self.months_survived // 12

    @property
    def remaining_months_survived(self) -> int:
        return self.months_survived % 12


def simulate_corpus_longevity(
    initial_corpus: float,
    annual_expense: float,
    annual_return_rate: float,
    annual_inflation_rate: float,
    max_years: int = 100,
) -> CorpusLongevityResult:
    """Estimate how long a corpus lasts with fixed return and inflation rates.

    Rates are decimals, so 8% should be passed as 0.08.
    """
    if initial_corpus < 0:
        raise ValueError("initial_corpus must be non-negative")
    if annual_expense < 0:
        raise ValueError("annual_expense must be non-negative")
    if annual_return_rate <= -1:
        raise ValueError("annual_return_rate must be greater than -100%")
    if annual_inflation_rate <= -1:
        raise ValueError("annual_inflation_rate must be greater than -100%")
    if max_years <= 0:
        raise ValueError("max_years must be positive")

    corpus = float(initial_corpus)
    monthly_expense = annual_expense / 12
    monthly_return = (1 + annual_return_rate) ** (1 / 12) - 1
    monthly_inflation = (1 + annual_inflation_rate) ** (1 / 12) - 1
    max_months = max_years * 12

    months_survived = 0
    for _ in range(max_months):
        corpus = corpus * (1 + monthly_return) - monthly_expense
        if corpus < 0:
            return CorpusLongevityResult(
                months_survived=months_survived,
                ending_corpus=corpus,
                ending_monthly_expense=monthly_expense,
                exhausted=True,
            )

        months_survived += 1
        monthly_expense *= 1 + monthly_inflation

    return CorpusLongevityResult(
        months_survived=months_survived,
        ending_corpus=corpus,
        ending_monthly_expense=monthly_expense,
        exhausted=False,
    )

