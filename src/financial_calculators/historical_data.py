"""CSV loading helpers for historical retirement simulations."""

from csv import DictReader
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class HistoricalYear:
    """One year of historical return and inflation data."""

    year: int
    return_rate: float
    inflation_rate: float


def _parse_rate(value: str, field_name: str) -> float:
    if value is None or value.strip() == "":
        raise ValueError(f"{field_name} is required")

    rate = float(value.strip())
    if abs(rate) > 1:
        rate = rate / 100
    if rate <= -1:
        raise ValueError(f"{field_name} must be greater than -100%")
    return rate


def load_historical_years(csv_path: str | Path) -> tuple[HistoricalYear, ...]:
    """Load historical yearly data from a CSV file.

    Required columns: year, return_rate, inflation_rate.
    Rates can be decimals like 0.08 or percentages like 8.
    """
    path = Path(csv_path)
    with path.open(newline="") as csv_file:
        reader = DictReader(csv_file)
        required_fields = {"year", "return_rate", "inflation_rate"}
        if reader.fieldnames is None or not required_fields.issubset(reader.fieldnames):
            required = ", ".join(sorted(required_fields))
            raise ValueError(f"CSV must include columns: {required}")

        years = tuple(
            HistoricalYear(
                year=int(row["year"]),
                return_rate=_parse_rate(row["return_rate"], "return_rate"),
                inflation_rate=_parse_rate(row["inflation_rate"], "inflation_rate"),
            )
            for row in reader
        )

    if not years:
        raise ValueError("CSV must include at least one data row")
    return tuple(sorted(years, key=lambda item: item.year))

