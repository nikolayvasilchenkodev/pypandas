"""Shared pytest fixtures."""

from __future__ import annotations

import pandas as pd
import pytest

from real_estate_analysis.data import load_listings
from real_estate_analysis.features import add_engineered_features


@pytest.fixture(scope="session")
def listings() -> pd.DataFrame:
    """Cleaned listings dataset loaded from the bundled sample."""
    return load_listings()


@pytest.fixture(scope="session")
def enriched(listings: pd.DataFrame) -> pd.DataFrame:
    """Listings with engineered features applied."""
    return add_engineered_features(listings, reference_year=2025)
