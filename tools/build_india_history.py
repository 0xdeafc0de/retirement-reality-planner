"""Build India historical replay data from public data sources."""

from __future__ import annotations

from pathlib import Path
import json
import sys
import urllib.request

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from financial_calculators.india_data import (
    annual_closes_from_nse_tri_rows,
    annual_returns_from_closes,
    combine_india_history,
    write_historical_years_csv,
)

NSE_TRI_URL = "https://www.niftyindices.com/Backpage.aspx/getTotalReturnIndexString"
WORLD_BANK_INFLATION_URL = (
    "https://api.worldbank.org/v2/country/IND/indicator/"
    "FP.CPI.TOTL.ZG?format=json&per_page=20000"
)
OUTPUT_PATH = Path("data/india/nifty50_tri_cpi_annual.csv")


def _fetch_json(request: urllib.request.Request):
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_nifty50_tri_rows(
    start_date: str = "01-Jan-1999",
    end_date: str = "31-Dec-2024",
):
    payload = {
        "cinfo": (
            "{'name':'Nifty 50','startDate':'"
            + start_date
            + "','endDate':'"
            + end_date
            + "','indexName':'Nifty 50'}"
        )
    }
    request = urllib.request.Request(
        NSE_TRI_URL,
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en-US,en;q=0.9",
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.niftyindices.com/reports/historical-data",
            "Origin": "https://www.niftyindices.com",
        },
    )
    response = _fetch_json(request)
    return json.loads(response["d"])


def fetch_world_bank_india_inflation() -> dict[int, float]:
    request = urllib.request.Request(
        WORLD_BANK_INFLATION_URL,
        headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0"},
    )
    response = _fetch_json(request)
    return {
        int(item["date"]): item["value"] / 100
        for item in response[1]
        if item["value"] is not None
    }


def build(output_path: Path = OUTPUT_PATH) -> tuple[int, int, int]:
    tri_rows = fetch_nifty50_tri_rows()
    annual_closes = annual_closes_from_nse_tri_rows(tri_rows)
    return_rates = annual_returns_from_closes(annual_closes)
    inflation_rates = fetch_world_bank_india_inflation()
    years = combine_india_history(return_rates, inflation_rates)
    write_historical_years_csv(years, output_path)
    return (years[0].year, years[-1].year, len(years))


def main() -> int:
    start_year, end_year, count = build()
    print(f"Wrote {OUTPUT_PATH} with {count} years: {start_year}-{end_year}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
