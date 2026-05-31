"""Build India-specific historical retirement replay data."""

from csv import DictWriter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from financial_calculators.historical_data import HistoricalYear


@dataclass(frozen=True)
class AnnualIndexClose:
    """Last available total-return index value for a calendar year."""

    year: int
    date: datetime
    value: float


def annual_closes_from_nse_tri_rows(rows) -> dict[int, AnnualIndexClose]:
    """Return the last available Nifty TRI close for each calendar year."""
    closes: dict[int, AnnualIndexClose] = {}
    for row in rows:
        date = datetime.strptime(row["Date"], "%d %b %Y")
        value = float(str(row["TotalReturnsIndex"]).replace(",", ""))
        current = closes.get(date.year)
        if current is None or date > current.date:
            closes[date.year] = AnnualIndexClose(
                year=date.year,
                date=date,
                value=value,
            )

    return closes


def annual_returns_from_closes(
    closes: dict[int, AnnualIndexClose],
) -> dict[int, float]:
    """Calculate calendar-year returns from annual close-to-close TRI values."""
    returns: dict[int, float] = {}
    for year in sorted(closes):
        previous = closes.get(year - 1)
        if previous is None:
            continue
        returns[year] = (closes[year].value / previous.value) - 1
    return returns


def combine_india_history(
    return_rates: dict[int, float],
    inflation_rates: dict[int, float],
) -> tuple[HistoricalYear, ...]:
    """Combine Nifty TRI returns and annual India CPI inflation rates."""
    years = sorted(set(return_rates).intersection(inflation_rates))
    return tuple(
        HistoricalYear(
            year=year,
            return_rate=return_rates[year],
            inflation_rate=inflation_rates[year],
        )
        for year in years
    )


def write_historical_years_csv(
    years: tuple[HistoricalYear, ...],
    csv_path: str | Path,
) -> None:
    """Write HistoricalYear records in the replay CSV format."""
    path = Path(csv_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as csv_file:
        writer = DictWriter(
            csv_file,
            fieldnames=["year", "return_rate", "inflation_rate"],
            lineterminator="\n",
        )
        writer.writeheader()
        for item in years:
            writer.writerow(
                {
                    "year": item.year,
                    "return_rate": round(item.return_rate * 100, 4),
                    "inflation_rate": round(item.inflation_rate * 100, 4),
                }
            )
