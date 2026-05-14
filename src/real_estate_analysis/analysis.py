"""Aggregation and ranking utilities over the engineered listings frame."""

from __future__ import annotations

from typing import Final

import pandas as pd

_MEDIAN: Final[str] = "median"
_MEAN: Final[str] = "mean"


def market_summary(df: pd.DataFrame) -> pd.DataFrame:
    """High-level KPIs per neighborhood.

    Returns one row per neighborhood with active-listing count, median price,
    median price per sqft, median property age, and luxury-listing share.
    """
    grouped = df.groupby("neighborhood", observed=True)
    summary = grouped.agg(
        n_listings=("listing_id", "count"),
        median_price_usd=("list_price_usd", _MEDIAN),
        mean_price_usd=("list_price_usd", _MEAN),
        median_price_per_sqft=("price_per_sqft", _MEDIAN),
        median_age_years=("property_age_years", _MEDIAN),
        luxury_share=("is_luxury", _MEAN),
    )
    summary["luxury_share"] = (summary["luxury_share"] * 100).round(1)
    return summary.sort_values("median_price_usd", ascending=False)


def price_per_sqft_by_neighborhood(
    df: pd.DataFrame, *, property_type: str | None = None
) -> pd.Series:
    """Median price-per-sqft per neighborhood, optionally filtered by property type."""
    frame = df if property_type is None else df.loc[df["property_type"] == property_type]
    return (
        frame.groupby("neighborhood", observed=True)["price_per_sqft"]
        .median()
        .sort_values(ascending=False)
        .rename("median_price_per_sqft")
    )


def top_value_listings(df: pd.DataFrame, *, n: int = 10) -> pd.DataFrame:
    """Return the ``n`` cheapest listings per square foot.

    A common screen for buyers: same neighborhood, lower $/sqft signals value.
    """
    if n <= 0:
        raise ValueError("n must be positive")

    relevant_cols = [
        "listing_id",
        "neighborhood",
        "property_type",
        "bedrooms",
        "living_area_sqft",
        "list_price_usd",
        "price_per_sqft",
    ]
    return (
        df.loc[df["price_per_sqft"].notna(), relevant_cols]
        .nsmallest(n, "price_per_sqft")
        .reset_index(drop=True)
    )


def monthly_listing_volume(df: pd.DataFrame) -> pd.Series:
    """Listings created per calendar month."""
    return (
        df.dropna(subset=["listed_at"])
        .set_index("listed_at")
        .resample("MS")["listing_id"]
        .count()
        .rename("n_listings")
    )
