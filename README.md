# Real-Estate Analysis

[![CI](https://github.com/nickvasylchenko/pypandas/actions/workflows/ci.yml/badge.svg)](https://github.com/nickvasylchenko/pypandas/actions/workflows/ci.yml)
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
git clone https://github.com/nickvasylchenko/pypandas.git
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

## Example output

```
=== Market summary by neighborhood ===
                 n_listings  median_price_usd  mean_price_usd  median_price_per_sqft  median_age_years  luxury_share
neighborhood
Harbor Heights           67           1340432         1356871                  561.0              58.0          76.1
Old Town                 64            903211          927448                  410.5              62.5          39.1
Downtown                 70            760150          799043                  336.0              55.0          24.3
...
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
