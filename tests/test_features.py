"""Tests for feature engineering."""

from __future__ import annotations

import pandas as pd

from real_estate_analysis.features import PRICE_BUCKET_LABELS, add_engineered_features


def test_engineered_columns_present(enriched: pd.DataFrame) -> None:
    expected = {
        "price_per_sqft",
        "property_age_years",
        "listing_age_days",
        "price_bucket",
        "is_luxury",
    }
    assert expected <= set(enriched.columns)


def test_price_per_sqft_matches_manual_calc(enriched: pd.DataFrame) -> None:
    cols = ["price_per_sqft", "list_price_usd", "living_area_sqft"]
    sample = enriched.dropna(subset=cols).head(5)
    price = sample["list_price_usd"].astype(float)
    area = sample["living_area_sqft"].astype(float)
    manual = (price / area).round(2)
    pd.testing.assert_series_equal(
        sample["price_per_sqft"].astype(float).reset_index(drop=True),
        manual.reset_index(drop=True),
        check_names=False,
    )


def test_is_luxury_threshold(enriched: pd.DataFrame) -> None:
    luxury = enriched.loc[enriched["is_luxury"], "list_price_usd"]
    assert (luxury >= 1_000_000).all()


def test_price_bucket_labels(enriched: pd.DataFrame) -> None:
    used = set(enriched["price_bucket"].dropna().unique())
    assert used <= set(PRICE_BUCKET_LABELS)


def test_add_engineered_features_does_not_mutate(listings: pd.DataFrame) -> None:
    before = listings.copy()
    add_engineered_features(listings)
    pd.testing.assert_frame_equal(before, listings)
