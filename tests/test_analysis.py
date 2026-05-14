"""Tests for the analysis aggregations."""

from __future__ import annotations

import pandas as pd
import pytest

from real_estate_analysis.analysis import (
    market_summary,
    monthly_listing_volume,
    price_per_sqft_by_neighborhood,
    top_value_listings,
)


def test_market_summary_shape(enriched: pd.DataFrame) -> None:
    summary = market_summary(enriched)
    expected_cols = {
        "n_listings",
        "median_price_usd",
        "mean_price_usd",
        "median_price_per_sqft",
        "median_age_years",
        "luxury_share",
    }
    assert expected_cols == set(summary.columns)
    assert summary["n_listings"].sum() == len(enriched)


def test_market_summary_sorted_descending(enriched: pd.DataFrame) -> None:
    summary = market_summary(enriched)
    medians = summary["median_price_usd"].tolist()
    assert medians == sorted(medians, reverse=True)


def test_price_per_sqft_by_neighborhood_filter(enriched: pd.DataFrame) -> None:
    full = price_per_sqft_by_neighborhood(enriched)
    condo = price_per_sqft_by_neighborhood(enriched, property_type="Condo")
    assert set(condo.index) <= set(full.index)


def test_top_value_listings_returns_n(enriched: pd.DataFrame) -> None:
    top = top_value_listings(enriched, n=7)
    assert len(top) == 7
    assert top["price_per_sqft"].is_monotonic_increasing


def test_top_value_listings_rejects_zero() -> None:
    with pytest.raises(ValueError):
        top_value_listings(pd.DataFrame(), n=0)


def test_monthly_listing_volume_index_is_month_start(enriched: pd.DataFrame) -> None:
    volume = monthly_listing_volume(enriched)
    assert volume.index.is_monotonic_increasing
    assert (volume.index.day == 1).all()
    assert volume.sum() == enriched["listed_at"].notna().sum()
