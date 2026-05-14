"""Data loading and cleaning for the real-estate listings dataset.

The bundled CSV mimics a typical MLS export: noisy column names, currency
strings, mixed-type date columns, and a few duplicate rows. The loader
normalizes the shape so downstream code can rely on a clean schema.
"""

from __future__ import annotations

import logging
from importlib import resources
from pathlib import Path

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

LISTING_SCHEMA: dict[str, str] = {
    "listing_id": "string",
    "neighborhood": "category",
    "property_type": "category",
    "bedrooms": "Int16",
    "bathrooms": "Float32",
    "living_area_sqft": "Int32",
    "lot_size_sqft": "Int32",
    "year_built": "Int16",
    "list_price_usd": "Int64",
    "listed_at": "datetime64[ns]",
    "status": "category",
}

_CURRENCY_CHARS = str.maketrans("", "", "$,")


def _default_csv_path() -> Path:
    """Return path to the CSV bundled inside the package."""
    return Path(str(resources.files("real_estate_analysis") / "data" / "listings.csv"))


def _parse_currency(series: pd.Series) -> pd.Series:
    """Strip ``$`` and thousands separators, returning a nullable Int64 series."""
    cleaned = series.astype("string").str.translate(_CURRENCY_CHARS).str.strip()
    cleaned = cleaned.replace({"": pd.NA, "N/A": pd.NA, "nan": pd.NA})
    return pd.to_numeric(cleaned, errors="coerce").astype("Int64")


def load_listings(path: str | Path | None = None) -> pd.DataFrame:
    """Load and clean the listings dataset.

    Args:
        path: Optional path to a CSV file. Defaults to the bundled sample.

    Returns:
        A DataFrame with the schema declared in :data:`LISTING_SCHEMA`,
        duplicates removed, and obvious sentinel values replaced with ``NA``.
    """
    csv_path = Path(path) if path is not None else _default_csv_path()
    logger.info("Loading listings from %s", csv_path)

    raw = pd.read_csv(csv_path, dtype="string", keep_default_na=False, na_values=["", "N/A"])
    raw.columns = raw.columns.str.strip().str.lower().str.replace(" ", "_")

    raw["list_price_usd"] = _parse_currency(raw["list_price_usd"])
    raw["listed_at"] = pd.to_datetime(raw["listed_at"], errors="coerce")

    for col, dtype in LISTING_SCHEMA.items():
        if dtype.startswith("datetime") or col == "list_price_usd":
            continue
        raw[col] = raw[col].astype(dtype)

    cleaned = (
        raw.loc[:, list(LISTING_SCHEMA)]
        .drop_duplicates(subset="listing_id", keep="last")
        .replace({"living_area_sqft": {0: pd.NA}, "year_built": {0: pd.NA}})
        .reset_index(drop=True)
    )

    n_dropped = len(raw) - len(cleaned)
    if n_dropped:
        logger.info("Dropped %d duplicate listing rows", n_dropped)

    return cleaned


def describe_quality(df: pd.DataFrame) -> pd.DataFrame:
    """Return a per-column data-quality report (null count, dtype, unique count)."""
    return pd.DataFrame(
        {
            "dtype": df.dtypes.astype(str),
            "n_missing": df.isna().sum(),
            "pct_missing": (df.isna().mean() * 100).round(2),
            "n_unique": df.nunique(dropna=True),
        }
    ).sort_values("pct_missing", ascending=False)


def _coerce_numeric(values: pd.Series) -> np.ndarray:
    """Convert a pandas nullable series to a float numpy array (NA → NaN)."""
    return values.astype("Float64").to_numpy(dtype=float, na_value=np.nan)
