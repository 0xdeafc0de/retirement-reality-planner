#
# Corpus longevity estimator - Find out how long your hard earned savings
# will last with inflation and the RoI you get on the remaining corpus.
#
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from financial_calculators.corpus import simulate_corpus_longevity


def main():
    corpus = float(input("Enter initial corpus amount (e.g., 20000000 for ₹2Cr): ").strip() or 20000000)
    yearly_exp = float(input("Enter yearly withdrawal amount (e.g., 1200000 for ₹1L/month): ").strip() or 1200000)
    roi = float(input("Enter avg annual RoI (in %, e.g., 7.5): ").strip() or 8)
    inflation_rate = float(input("Enter avg inflation rate (in %, e.g., 5): ").strip() or 5)

    print(f"Using corpus {corpus}, yearly expenses {yearly_exp}, return {roi}%/yr and inflation rate {inflation_rate}%")

    result = simulate_corpus_longevity(
        initial_corpus=corpus,
        annual_expense=yearly_exp,
        annual_return_rate=roi / 100,
        annual_inflation_rate=inflation_rate / 100,
    )

    print(
        "\n Corpus will last "
        f"{result.years_survived} years and "
        f"{result.remaining_months_survived} months."
    )


if __name__ == "__main__":
    main()
