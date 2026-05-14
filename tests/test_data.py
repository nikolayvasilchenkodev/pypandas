"""Tests for the data loader."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from real_estate_analysis.data import LISTING_SCHEMA, describe_quality, load_listings


def test_load_listings_schema(listings: pd.DataFrame) -> None:
    assert list(listings.columns) == list(LISTING_SCHEMA)
    assert len(listings) > 0


def test_load_listings_dtypes(listings: pd.DataFrame) -> None:
    assert pd.api.types.is_datetime64_any_dtype(listings["listed_at"])
    assert pd.api.types.is_integer_dtype(listings["list_price_usd"])
    assert isinstance(listings["neighborhood"].dtype, pd.CategoricalDtype)


def test_listing_ids_are_unique(listings: pd.DataFrame) -> None:
    assert listings["listing_id"].is_unique


def test_currency_parsing_handles_missing(tmp_path: Path) -> None:
    csv = tmp_path / "sample.csv"
    csv.write_text(
        "listing_id,neighborhood,property_type,bedrooms,bathrooms,living_area_sqft,"
        "lot_size_sqft,year_built,list_price_usd,listed_at,status\n"
        'L1,Downtown,Condo,2,1.0,800,0,1990,"$425,000",2024-05-01,Active\n'
        "L2,Lakeview,Condo,3,2.0,1200,0,1985,N/A,2024-05-02,Active\n"
    )
    df = load_listings(csv)
    assert df.loc[df["listing_id"] == "L1", "list_price_usd"].iloc[0] == 425_000
    assert pd.isna(df.loc[df["listing_id"] == "L2", "list_price_usd"].iloc[0])


def test_describe_quality_columns(listings: pd.DataFrame) -> None:
    report = describe_quality(listings)
    assert {"dtype", "n_missing", "pct_missing", "n_unique"} <= set(report.columns)
    assert (report["pct_missing"] >= 0).all()


@pytest.mark.parametrize("col", ["list_price_usd", "living_area_sqft", "year_built"])
def test_numeric_columns_non_negative(listings: pd.DataFrame, col: str) -> None:
    values = listings[col].dropna()
    assert (values >= 0).all()
