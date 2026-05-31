"""Command line interface for financial calculators."""

from argparse import ArgumentParser, Namespace

from financial_calculators.corpus import simulate_corpus_longevity
from financial_calculators.inflation import (
    adjusted_value_after_inflation,
    future_cost_after_inflation,
)
from financial_calculators.retirement import simulate_monte_carlo_retirement


def _money(value: float, currency: str) -> str:
    return f"{currency}{value:,.2f}"


def _add_inflation_command(parser: ArgumentParser) -> None:
    parser.add_argument("--present-value", type=float, default=20_000_000)
    parser.add_argument("--inflation", type=float, default=6)
    parser.add_argument("--years", type=float, default=20)
    parser.add_argument("--currency", default="₹")


def _add_corpus_command(parser: ArgumentParser) -> None:
    parser.add_argument("--corpus", type=float, default=20_000_000)
    parser.add_argument("--annual-expense", type=float, default=1_200_000)
    parser.add_argument("--return-rate", type=float, default=8)
    parser.add_argument("--inflation", type=float, default=5)
    parser.add_argument("--max-years", type=int, default=100)
    parser.add_argument("--currency", default="₹")


def _add_retire_command(parser: ArgumentParser) -> None:
    parser.add_argument("--mode", choices=["monte-carlo"], default="monte-carlo")
    parser.add_argument("--corpus", type=float, default=20_000_000)
    parser.add_argument("--annual-expense", type=float, default=1_200_000)
    parser.add_argument("--years", type=int, default=35)
    parser.add_argument("--simulations", type=int, default=10_000)
    parser.add_argument("--return-mean", type=float, default=8)
    parser.add_argument("--return-volatility", type=float, default=15)
    parser.add_argument("--inflation-mean", type=float, default=5)
    parser.add_argument("--inflation-volatility", type=float, default=2)
    parser.add_argument("--crash-probability", type=float, default=5)
    parser.add_argument("--crash-impact", type=float, default=-30)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--currency", default="₹")


def run_inflation(args: Namespace) -> int:
    inflation_rate = args.inflation / 100
    adjusted_value = adjusted_value_after_inflation(
        args.present_value,
        inflation_rate,
        args.years,
    )
    future_cost = future_cost_after_inflation(
        args.present_value,
        inflation_rate,
        args.years,
    )

    print("Inflation calculator")
    print(f"Present value: {_money(args.present_value, args.currency)}")
    print(f"Inflation: {args.inflation:.2f}%")
    print(f"Years: {args.years:g}")
    print(f"Purchasing power after inflation: {_money(adjusted_value, args.currency)}")
    print(f"Future nominal cost: {_money(future_cost, args.currency)}")
    return 0


def run_corpus(args: Namespace) -> int:
    result = simulate_corpus_longevity(
        initial_corpus=args.corpus,
        annual_expense=args.annual_expense,
        annual_return_rate=args.return_rate / 100,
        annual_inflation_rate=args.inflation / 100,
        max_years=args.max_years,
    )

    print("Corpus longevity calculator")
    print(f"Initial corpus: {_money(args.corpus, args.currency)}")
    print(f"Annual expense: {_money(args.annual_expense, args.currency)}")
    print(f"Return: {args.return_rate:.2f}%")
    print(f"Inflation: {args.inflation:.2f}%")
    if result.exhausted:
        print(
            "Corpus lasts "
            f"{result.years_survived} years and "
            f"{result.remaining_months_survived} months."
        )
    else:
        print(f"Corpus survives the full {args.max_years}-year horizon.")
    print(f"Ending corpus: {_money(result.ending_corpus, args.currency)}")
    return 0


def run_retire(args: Namespace) -> int:
    summary = simulate_monte_carlo_retirement(
        initial_corpus=args.corpus,
        annual_expense=args.annual_expense,
        years=args.years,
        simulations=args.simulations,
        return_mean=args.return_mean / 100,
        return_volatility=args.return_volatility / 100,
        inflation_mean=args.inflation_mean / 100,
        inflation_volatility=args.inflation_volatility / 100,
        crash_probability=args.crash_probability / 100,
        crash_impact=args.crash_impact / 100,
        seed=args.seed,
    )

    print("Monte Carlo retirement simulation")
    print(f"Simulations: {summary.simulations:,}")
    print(f"Horizon: {summary.horizon_years} years")
    print(f"Initial corpus: {_money(args.corpus, args.currency)}")
    print(f"Annual expense: {_money(args.annual_expense, args.currency)}")
    print(f"Success rate: {summary.success_rate * 100:.1f}%")
    print(f"Median ending corpus: {_money(summary.median_ending_corpus, args.currency)}")
    print(f"5th percentile ending corpus: {_money(summary.ending_corpus_p5, args.currency)}")
    print(f"10th percentile ending corpus: {_money(summary.ending_corpus_p10, args.currency)}")
    print(f"90th percentile ending corpus: {_money(summary.ending_corpus_p90, args.currency)}")
    if summary.earliest_failure_year is None:
        print("No simulated path exhausted the corpus.")
    else:
        print(f"Earliest failure year: {summary.earliest_failure_year}")
        print(f"Median failure year: {summary.median_failure_year:g}")
    return 0


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(
        prog="fincalc",
        description="Personal finance calculators and retirement planning tools.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    inflation_parser = subparsers.add_parser(
        "inflation",
        help="Calculate inflation-adjusted purchasing power.",
    )
    _add_inflation_command(inflation_parser)
    inflation_parser.set_defaults(func=run_inflation)

    corpus_parser = subparsers.add_parser(
        "corpus",
        help="Estimate corpus longevity with fixed return and inflation rates.",
    )
    _add_corpus_command(corpus_parser)
    corpus_parser.set_defaults(func=run_corpus)

    retire_parser = subparsers.add_parser(
        "retire",
        help="Run retirement planning simulations.",
    )
    _add_retire_command(retire_parser)
    retire_parser.set_defaults(func=run_retire)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
