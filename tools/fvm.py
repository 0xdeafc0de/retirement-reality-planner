from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from financial_calculators.inflation import adjusted_value_after_inflation


def calculate_fvm(present_value, annual_rate, years):
    """Backward-compatible wrapper for inflation-adjusted purchasing power."""
    return adjusted_value_after_inflation(present_value, annual_rate, years)


def main():
    pv = float(input("Enter present value (e.g., 20000000 for ₹2Cr): ").strip() or 20000000)
    air = float(input("Enter avg annual inflation rate (e.g., 6 for 6%): ").strip() or 6)
    years = float(input("Enter number of years after which value is calculated: ").strip() or 20)

    print(f"Present Value {pv}, Annual inflation rate {air}%/yr, time period {years} years")

    air = air / 100

    fvm = calculate_fvm(pv, air, years)
    print(f"Purchasing power after {years:g} years: ₹{fvm:,.2f}")


if __name__ == "__main__":
    main()
