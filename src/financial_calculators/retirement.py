"""Retirement planning simulations."""

from dataclasses import dataclass
import random
from statistics import median


@dataclass(frozen=True)
class RetirementPath:
    """One simulated retirement outcome."""

    ending_corpus: float
    years_survived: int
    exhausted: bool
    start_year: int | None = None
    end_year: int | None = None


@dataclass(frozen=True)
class MonteCarloRetirementSummary:
    """Summary statistics for a Monte Carlo retirement simulation."""

    simulations: int
    horizon_years: int
    success_rate: float
    median_ending_corpus: float
    ending_corpus_p5: float
    ending_corpus_p10: float
    ending_corpus_p90: float
    earliest_failure_year: int | None
    median_failure_year: float | None
    paths: tuple[RetirementPath, ...]


@dataclass(frozen=True)
class HistoricalReplaySummary:
    """Summary statistics for historical retirement replay."""

    periods: int
    horizon_years: int
    success_rate: float
    median_ending_corpus: float
    ending_corpus_p5: float
    ending_corpus_p10: float
    ending_corpus_p90: float
    earliest_failure_year: int | None
    median_failure_year: float | None
    worst_start_year: int
    worst_ending_corpus: float
    paths: tuple[RetirementPath, ...]


def _validate_rate(name: str, value: float) -> None:
    if value <= -1:
        raise ValueError(f"{name} must be greater than -100%")


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        raise ValueError("values must not be empty")
    if not 0 <= percentile <= 100:
        raise ValueError("percentile must be between 0 and 100")

    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]

    rank = (len(ordered) - 1) * (percentile / 100)
    lower = int(rank)
    upper = min(lower + 1, len(ordered) - 1)
    weight = rank - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def _bounded_return(value: float) -> float:
    return max(value, -0.95)


def _bounded_inflation(value: float) -> float:
    return max(value, -0.20)


def simulate_monte_carlo_retirement(
    initial_corpus: float,
    annual_expense: float,
    years: int,
    simulations: int = 10_000,
    return_mean: float = 0.08,
    return_volatility: float = 0.15,
    inflation_mean: float = 0.05,
    inflation_volatility: float = 0.02,
    crash_probability: float = 0.05,
    crash_impact: float = -0.30,
    seed: int | None = None,
) -> MonteCarloRetirementSummary:
    """Run a Monte Carlo retirement simulation with optional fat-tail crash years.

    Rates are decimals, so 8% should be passed as 0.08. Expenses are withdrawn
    at the start of each year, making early bad-return years visible.
    """
    if initial_corpus < 0:
        raise ValueError("initial_corpus must be non-negative")
    if annual_expense < 0:
        raise ValueError("annual_expense must be non-negative")
    if years <= 0:
        raise ValueError("years must be positive")
    if simulations <= 0:
        raise ValueError("simulations must be positive")
    if return_volatility < 0:
        raise ValueError("return_volatility must be non-negative")
    if inflation_volatility < 0:
        raise ValueError("inflation_volatility must be non-negative")
    if not 0 <= crash_probability <= 1:
        raise ValueError("crash_probability must be between 0 and 1")

    _validate_rate("return_mean", return_mean)
    _validate_rate("inflation_mean", inflation_mean)
    _validate_rate("crash_impact", crash_impact)

    rng = random.Random(seed)
    paths: list[RetirementPath] = []

    for _ in range(simulations):
        corpus = float(initial_corpus)
        expense = float(annual_expense)
        years_survived = 0
        exhausted = False

        for year in range(1, years + 1):
            corpus -= expense
            if corpus < 0:
                years_survived = year - 1
                exhausted = True
                break

            annual_return = rng.gauss(return_mean, return_volatility)
            if rng.random() < crash_probability:
                annual_return += crash_impact
            annual_return = _bounded_return(annual_return)

            inflation = _bounded_inflation(
                rng.gauss(inflation_mean, inflation_volatility)
            )

            corpus *= 1 + annual_return
            expense *= 1 + inflation
            years_survived = year

        paths.append(
            RetirementPath(
                ending_corpus=corpus,
                years_survived=years_survived,
                exhausted=exhausted,
            )
        )

    ending_values = [path.ending_corpus for path in paths]
    failures = [path.years_survived + 1 for path in paths if path.exhausted]
    successes = simulations - len(failures)

    return MonteCarloRetirementSummary(
        simulations=simulations,
        horizon_years=years,
        success_rate=successes / simulations,
        median_ending_corpus=median(ending_values),
        ending_corpus_p5=_percentile(ending_values, 5),
        ending_corpus_p10=_percentile(ending_values, 10),
        ending_corpus_p90=_percentile(ending_values, 90),
        earliest_failure_year=min(failures) if failures else None,
        median_failure_year=median(failures) if failures else None,
        paths=tuple(paths),
    )


def simulate_historical_replay(
    initial_corpus: float,
    annual_expense: float,
    years: int,
    historical_years,
) -> HistoricalReplaySummary:
    """Replay retirement against every valid rolling historical period.

    historical_years must contain objects with year, return_rate, and
    inflation_rate attributes. Rates should be decimals, so 8% is 0.08.
    """
    if initial_corpus < 0:
        raise ValueError("initial_corpus must be non-negative")
    if annual_expense < 0:
        raise ValueError("annual_expense must be non-negative")
    if years <= 0:
        raise ValueError("years must be positive")

    ordered_years = tuple(sorted(historical_years, key=lambda item: item.year))
    if len(ordered_years) < years:
        raise ValueError("historical_years must contain at least years rows")

    paths: list[RetirementPath] = []
    for start_index in range(0, len(ordered_years) - years + 1):
        period = ordered_years[start_index : start_index + years]
        corpus = float(initial_corpus)
        expense = float(annual_expense)
        years_survived = 0
        exhausted = False

        for index, item in enumerate(period, start=1):
            _validate_rate("return_rate", item.return_rate)
            _validate_rate("inflation_rate", item.inflation_rate)

            corpus -= expense
            if corpus < 0:
                years_survived = index - 1
                exhausted = True
                break

            corpus *= 1 + item.return_rate
            expense *= 1 + item.inflation_rate
            years_survived = index

        paths.append(
            RetirementPath(
                ending_corpus=corpus,
                years_survived=years_survived,
                exhausted=exhausted,
                start_year=period[0].year,
                end_year=period[-1].year,
            )
        )

    ending_values = [path.ending_corpus for path in paths]
    failures = [path.years_survived + 1 for path in paths if path.exhausted]
    successes = len(paths) - len(failures)
    worst_path = min(paths, key=lambda path: path.ending_corpus)
    worst_start_year = worst_path.start_year
    if worst_start_year is None:
        raise RuntimeError("historical replay path is missing a start year")

    return HistoricalReplaySummary(
        periods=len(paths),
        horizon_years=years,
        success_rate=successes / len(paths),
        median_ending_corpus=median(ending_values),
        ending_corpus_p5=_percentile(ending_values, 5),
        ending_corpus_p10=_percentile(ending_values, 10),
        ending_corpus_p90=_percentile(ending_values, 90),
        earliest_failure_year=min(failures) if failures else None,
        median_failure_year=median(failures) if failures else None,
        worst_start_year=worst_start_year,
        worst_ending_corpus=worst_path.ending_corpus,
        paths=tuple(paths),
    )
