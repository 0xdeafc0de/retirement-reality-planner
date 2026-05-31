"""Command line interface for financial calculators."""

from argparse import ArgumentParser, Namespace

from financial_calculators.corpus import simulate_corpus_longevity
from financial_calculators.inflation import (
    adjusted_value_after_inflation,
    future_cost_after_inflation,
)


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

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

