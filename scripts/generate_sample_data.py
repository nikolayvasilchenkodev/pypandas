"""Generate a deterministic, slightly-messy sample listings CSV.

Run from the repo root::

    python scripts/generate_sample_data.py

The script writes ``src/real_estate_analysis/data/listings.csv``. Output is
reproducible (fixed seed) so committed CSV diffs stay reviewable.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

SEED = 20250514
N_ROWS = 400
OUT_PATH = (
    Path(__file__).resolve().parent.parent
    / "src"
    / "real_estate_analysis"
    / "data"
    / "listings.csv"
)

NEIGHBORHOODS = {
    "Downtown": (650_000, 180_000),
    "Lakeview": (520_000, 140_000),
    "Westside": (430_000, 110_000),
    "Old Town": (780_000, 220_000),
    "Harbor Heights": (1_100_000, 280_000),
    "Maple Grove": (360_000, 90_000),
}
PROPERTY_TYPES = ["Single Family", "Condo", "Townhouse", "Multi-Family"]
STATUSES = ["Active", "Pending", "Sold", "Withdrawn"]


def _format_currency(value: float | None) -> str:
    if value is None or np.isnan(value):
        return "N/A"
    return f"${round(value):,}"


def build_frame(rng: np.random.Generator) -> pd.DataFrame:
    neighborhoods = rng.choice(list(NEIGHBORHOODS), size=N_ROWS)
    base_prices = np.array([NEIGHBORHOODS[n][0] for n in neighborhoods])
    stds = np.array([NEIGHBORHOODS[n][1] for n in neighborhoods])
    price_noise = rng.normal(0, 1, size=N_ROWS)

    living_area = rng.integers(600, 4500, size=N_ROWS)
    sqft_premium = (living_area - 1500) * rng.uniform(120, 220, size=N_ROWS)
    list_price = np.clip(base_prices + stds * price_noise + sqft_premium, 95_000, 4_500_000)

    listed_at = pd.to_datetime("2024-01-01") + pd.to_timedelta(
        rng.integers(0, 450, size=N_ROWS), unit="D"
    )

    df = pd.DataFrame(
        {
            "listing_id": [f"L{idx:05d}" for idx in range(N_ROWS)],
            "neighborhood": neighborhoods,
            "property_type": rng.choice(PROPERTY_TYPES, size=N_ROWS, p=[0.5, 0.25, 0.15, 0.10]),
            "bedrooms": rng.integers(1, 7, size=N_ROWS),
            "bathrooms": np.round(rng.uniform(1.0, 5.0, size=N_ROWS) * 2) / 2,
            "living_area_sqft": living_area,
            "lot_size_sqft": rng.integers(0, 20_000, size=N_ROWS),
            "year_built": rng.integers(1905, 2025, size=N_ROWS),
            "list_price_usd": [_format_currency(p) for p in list_price],
            "listed_at": listed_at.strftime("%Y-%m-%d"),
            "status": rng.choice(STATUSES, size=N_ROWS, p=[0.55, 0.15, 0.25, 0.05]),
        }
    )

    # Inject realistic noise: missing prices, duplicate rows, sentinel zeros.
    missing_idx = rng.choice(df.index, size=8, replace=False)
    df.loc[missing_idx, "list_price_usd"] = "N/A"
    df.loc[rng.choice(df.index, size=5, replace=False), "year_built"] = 0
    duplicates = df.sample(6, random_state=SEED)
    df = pd.concat([df, duplicates], ignore_index=True)

    # Mess up column header capitalization to exercise the cleaner.
    df = df.rename(columns={"list_price_usd": "List_Price_USD", "listed_at": "Listed_At"})
    return df


def main() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    frame = build_frame(rng)
    frame.to_csv(OUT_PATH, index=False)
    print(f"Wrote {len(frame):,} rows to {OUT_PATH.relative_to(OUT_PATH.parent.parent.parent)}")


if __name__ == "__main__":
    main()
