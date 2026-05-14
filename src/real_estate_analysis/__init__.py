"""Real-estate listings analysis toolkit built on pandas."""

from real_estate_analysis.analysis import (
    market_summary,
    price_per_sqft_by_neighborhood,
    top_value_listings,
)
from real_estate_analysis.data import load_listings
from real_estate_analysis.features import add_engineered_features

__all__ = [
    "add_engineered_features",
    "load_listings",
    "market_summary",
    "price_per_sqft_by_neighborhood",
    "top_value_listings",
]

__version__ = "0.1.0"
