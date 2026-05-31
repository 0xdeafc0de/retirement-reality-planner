# Retirement Reality Planner

Personal finance calculators and retirement planning simulations that avoid
overly smooth, rosy projections.

Most simple retirement spreadsheets assume one fixed return and one fixed
inflation rate. That is useful for a quick estimate, but real retirement
outcomes depend heavily on sequence risk: bad market years, high inflation, or
large withdrawals early in retirement can change the result even when the
long-term average return looks comfortable.

This project is being built around that idea.

## What It Does Today

- Calculates inflation-adjusted purchasing power.
- Estimates how long a retirement corpus lasts with fixed return and inflation.
- Replays retirement plans against year-by-year historical return and inflation
  data from CSV files.
- Runs Monte Carlo retirement simulations with configurable return volatility,
  inflation volatility, crash probability, crash impact, and deterministic
  random seeds.
- Reports success rate, ending corpus percentiles, earliest failure year, and
  median failure year.

## Installation

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
```

Run the test suite:

```bash
.venv/bin/pytest -q
```

## CLI Usage

After installation, use the `fincalc` command.

### Inflation Calculator

```bash
.venv/bin/fincalc inflation \
  --present-value 20000000 \
  --inflation 6 \
  --years 20
```

Example output:

```text
Inflation calculator
Present value: ₹20,000,000.00
Inflation: 6.00%
Years: 20
Purchasing power after inflation: ₹6,236,094.54
Future nominal cost: ₹64,142,709.44
```

### Corpus Longevity Calculator

```bash
.venv/bin/fincalc corpus \
  --corpus 20000000 \
  --annual-expense 1200000 \
  --return-rate 8 \
  --inflation 5 \
  --max-years 60
```

Example output:

```text
Corpus longevity calculator
Initial corpus: ₹20,000,000.00
Annual expense: ₹1,200,000.00
Return: 8.00%
Inflation: 5.00%
Corpus lasts 22 years and 8 months.
Ending corpus: ₹-291,419.04
```

### Monte Carlo Retirement Simulation

```bash
.venv/bin/fincalc retire \
  --mode monte-carlo \
  --corpus 20000000 \
  --annual-expense 1200000 \
  --years 35 \
  --simulations 10000 \
  --return-mean 8 \
  --return-volatility 15 \
  --inflation-mean 5 \
  --inflation-volatility 2 \
  --crash-probability 5 \
  --crash-impact -30 \
  --seed 7
```

Example output:

```text
Monte Carlo retirement simulation
Simulations: 10,000
Horizon: 35 years
Initial corpus: ₹20,000,000.00
Annual expense: ₹1,200,000.00
Success rate: 6.3%
Median ending corpus: ₹-1,256,747.06
5th percentile ending corpus: ₹-3,176,691.24
10th percentile ending corpus: ₹-2,682,118.03
90th percentile ending corpus: ₹-111,240.59
Earliest failure year: 5
Median failure year: 17
```

### Historical Retirement Replay

Historical replay tests the same retirement plan against every valid rolling
start year in a CSV file.

CSV format:

```csv
year,return_rate,inflation_rate
2008,-35.0,8.0
2009,26.0,6.0
2010,14.0,5.5
```

Rates can be percentages like `8.5` or decimals like `0.085`.

```bash
.venv/bin/fincalc retire \
  --mode historical \
  --history-csv data/sample/historical_returns_sample.csv \
  --corpus 20000000 \
  --annual-expense 1200000 \
  --years 15
```

Example output:

```text
Historical retirement replay
Periods tested: 11
Horizon: 15 years
Initial corpus: ₹20,000,000.00
Annual expense: ₹1,200,000.00
Success rate: 81.8%
Worst start year: 2000
Worst ending corpus: ₹-110,849.53
Median ending corpus: ₹6,575,695.04
5th percentile ending corpus: ₹-61,224.41
10th percentile ending corpus: ₹-11,599.28
90th percentile ending corpus: ₹25,221,874.57
Earliest failure year: 13
Median failure year: 13.5
```

## Python API

```python
from financial_calculators import (
    load_historical_years,
    simulate_historical_replay,
    simulate_monte_carlo_retirement,
)

summary = simulate_monte_carlo_retirement(
    initial_corpus=20_000_000,
    annual_expense=1_200_000,
    years=35,
    simulations=10_000,
    return_mean=0.08,
    return_volatility=0.15,
    inflation_mean=0.05,
    inflation_volatility=0.02,
    crash_probability=0.05,
    crash_impact=-0.30,
    seed=7,
)

print(summary.success_rate)
print(summary.ending_corpus_p10)

history = load_historical_years("data/sample/historical_returns_sample.csv")
historical_summary = simulate_historical_replay(
    initial_corpus=20_000_000,
    annual_expense=1_200_000,
    years=15,
    historical_years=history,
)

print(historical_summary.worst_start_year)
```

## Modeling Assumptions

The fixed corpus calculator compounds returns monthly and increases expenses
monthly with inflation.

The Monte Carlo retirement simulator currently works at annual granularity:

- Annual expenses are withdrawn at the start of each year.
- Returns are sampled from a configurable normal distribution.
- Inflation is sampled independently from a configurable normal distribution.
- Optional crash years apply an additional negative return shock.
- Returns are bounded at -95% so a simulated year cannot lose more than the
  entire portfolio.
- Inflation is bounded at -20% to avoid unrealistic deflation outliers.
- A `--seed` makes runs reproducible.

The historical replay simulator uses the same annual timing model:

- Annual expenses are withdrawn at the start of each year.
- That year's historical return is applied after the withdrawal.
- The next year's expense is adjusted by that year's historical inflation.
- Every rolling start period with enough data is tested.

This is intentionally more honest than a single smooth compounding curve, but it
is still a model. It should be used for planning insight, not as financial
advice.

## Roadmap

- Historical bootstrap Monte Carlo: sample real historical years or multi-year
  blocks instead of purely synthetic normal returns.
- India-first datasets: CPI inflation, Nifty 50 / Nifty TRI, debt index or
  fixed-income assumptions.
- Asset allocation support: equity, debt, cash, rebalancing, and glide paths.
- Withdrawal strategies: fixed real withdrawal, guardrails, floor-and-upside,
  and dynamic spending.
- CSV/JSON output for analysis and charts.
- Web UI for non-technical users.

## Development

```bash
.venv/bin/pytest -q
```

Legacy scripts are still available:

```bash
python3 fvm.py
python3 corpus_runtime.py
```

## Disclaimer

This project is for education and planning exploration. It is not investment,
tax, legal, or retirement advice.
