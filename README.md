# Real-Estate Analysis

[![CI](https://github.com/nikolayvasilchenkodev/pypandas/actions/workflows/ci.yml/badge.svg)](https://github.com/nikolayvasilchenkodev/pypandas/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Code style: ruff](https://img.shields.io/badge/lint-ruff-46aef7)](https://docs.astral.sh/ruff/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A small, well-tested `pandas` toolkit for exploratory analysis of residential
real-estate listings. Built to demonstrate idiomatic pandas usage, clean
package layout, type hints, and a working CI pipeline.

## Highlights

- **Robust ingestion** — handles currency strings, sentinel values, duplicate
  rows, and mixed header casing typical of MLS exports.
- **Nullable dtypes everywhere** — `Int64`, `Float32`, `category`, `string`,
  and proper `datetime64` instead of `object` columns.
- **Vectorised feature engineering** — `$/sqft`, property age, listing age,
  price bands via `pd.cut`, luxury flag.
- **Analysis primitives** — per-neighborhood KPIs, value-screening,
  monthly listing volume via `resample`.
- **CLI** — `real-estate-analysis` prints a quick market report.
- **Tested** — `pytest` with `pytest-cov`, parametric cases, no-mutation
  guarantees, schema invariants.
- **CI** — `ruff` lint + format, `mypy --strict` on `src/`, `pytest` matrix
  across Python 3.10 / 3.11 / 3.12.

## Project layout

```
.
├── src/real_estate_analysis/
│   ├── __init__.py
│   ├── data.py            # loading + cleaning
│   ├── features.py        # vectorised feature engineering
│   ├── analysis.py        # aggregations / rankings
│   ├── cli.py             # `real-estate-analysis` entry point
│   └── data/listings.csv  # bundled sample dataset
├── scripts/
│   └── generate_sample_data.py
├── tests/
│   ├── conftest.py
│   ├── test_data.py
│   ├── test_features.py
│   └── test_analysis.py
├── .github/workflows/ci.yml
├── pyproject.toml
├── LICENSE
└── README.md
```

## Install

```bash
git clone https://github.com/nikolayvasilchenkodev/pypandas.git
cd pypandas
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Quick start

```python
from real_estate_analysis import (
    load_listings,
    add_engineered_features,
    market_summary,
    top_value_listings,
)

df = add_engineered_features(load_listings())
print(market_summary(df).head())
print(top_value_listings(df, n=5))
```

CLI:

```bash
real-estate-analysis --top 5 --verbose
```

Flags:

- `--csv PATH` — load a custom listings CSV (defaults to the bundled sample).
- `--top N` — number of best-value listings to display (default 5).
- `-v / --verbose` — enable INFO-level logging.
- `--no-color` — disable ANSI colors (useful when piping).

## Example output

Output is rendered with [`rich`](https://github.com/Textualize/rich) — colored
headers, right-aligned numerics, comma-grouped numbers, and section rules:

```
╭─────────────────────────────────╮
│  Real-Estate Market Report      │
│  source bundled sample dataset  │
│  rows   400                     │
╰─────────────────────────────────╯
────────────────────────────────────────────────────────────────────────────
 Market summary by neighborhood

 neighborhood     n_listings   median_price_usd   mean_price_usd   median_price_per_sqft   median_age_years   luxury_share
 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 Harbor Heights           62          1,277,732     1,268,642.82                  554.53                 44          85.20
 Old Town                 67          1,003,757          978,770                     369                 56          50.70
 Downtown                 79            746,706       793,715.93                  321.60                 68          23.70
 Westside                 65            626,296       620,850.48                  231.16                 74           4.70
 Lakeview                 52         617,762.50       645,392.18                  291.64                 59              8
 Maple Grove              75         511,191.50       531,833.66                  225.96              56.50           1.40
────────────────────────────────────────────────────────────────────────────
 Top 5 value listings ($/sqft)

 listing_id   neighborhood   property_type   bedrooms   living_area_sqft   list_price_usd   price_per_sqft
 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 L00067       Downtown       Single Family          6              3,820          383,735           100.45
 L00209       Westside       Townhouse              3                824           95,000           115.29
 L00237       Westside       Single Family          5              2,246          284,902           126.85
 L00381       Westside       Townhouse              5              3,113          400,619           128.69
 L00102       Downtown       Single Family          1              1,618          235,508           145.56
```

## Development

```bash
ruff check .
ruff format .
mypy src
pytest
```

Regenerate the sample dataset (deterministic, fixed seed):

```bash
python scripts/generate_sample_data.py
```

## License

[MIT](LICENSE).
