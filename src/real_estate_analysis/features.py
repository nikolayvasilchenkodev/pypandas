"""Feature engineering for real-estate listings."""

from __future__ import annotations

import pandas as pd

PRICE_BUCKETS_USD: tuple[int, ...] = (0, 250_000, 500_000, 750_000, 1_000_000, 2_000_000)
PRICE_BUCKET_LABELS: tuple[str, ...] = (
    "<250k",
    "250k-500k",
    "500k-750k",
    "750k-1M",
    "1M-2M",
)


def add_engineered_features(df: pd.DataFrame, *, reference_year: int | None = None) -> pd.DataFrame:
    """Append derived columns useful for downstream analysis.

    Adds:
        * ``price_per_sqft``       — list price divided by living area.
        * ``property_age_years``   — years since ``year_built``.
        * ``listing_age_days``     — days since ``listed_at``.
        * ``price_bucket``         — categorical price band.
        * ``is_luxury``            — boolean: price >= 1M USD.

    Args:
        df: Cleaned listings frame (see :func:`real_estate_analysis.data.load_listings`).
        reference_year: Year used as "today" when computing ages. Defaults to
            the max ``listed_at`` year in the data, or current UTC year.

    Returns:
        A new DataFrame; the input is not mutated.
    """
    enriched = df.copy()

    living_area = enriched["living_area_sqft"].astype("Float64")
    enriched["price_per_sqft"] = (enriched["list_price_usd"].astype("Float64") / living_area).round(
        2
    )

    if reference_year is None:
        listed_year = enriched["listed_at"].dt.year.max()
        reference_year = int(listed_year) if pd.notna(listed_year) else pd.Timestamp.utcnow().year

    enriched["property_age_years"] = (reference_year - enriched["year_built"]).astype("Int16")

    today = pd.Timestamp(year=reference_year, month=12, day=31)
    enriched["listing_age_days"] = (today - enriched["listed_at"]).dt.days.astype("Int32")

    enriched["price_bucket"] = pd.cut(
        enriched["list_price_usd"].astype("Float64"),
        bins=list(PRICE_BUCKETS_USD),
        labels=list(PRICE_BUCKET_LABELS),
        include_lowest=True,
    )

    enriched["is_luxury"] = enriched["list_price_usd"] >= 1_000_000

    return enriched
