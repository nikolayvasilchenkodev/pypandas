"""Command-line entry point printing a quick market report."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import pandas as pd

from real_estate_analysis.analysis import (
    market_summary,
    monthly_listing_volume,
    top_value_listings,
)
from real_estate_analysis.data import describe_quality, load_listings
from real_estate_analysis.features import add_engineered_features


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="real-estate-analysis",
        description="Print a quick pandas-driven market report for residential listings.",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=None,
        help="Path to a listings CSV. Defaults to the bundled sample dataset.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=5,
        help="Number of best-value listings to display (default: 5).",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable INFO-level logging.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    listings = load_listings(args.csv)
    enriched = add_engineered_features(listings)

    with pd.option_context("display.max_columns", None, "display.width", 120):
        print("=== Data quality ===")
        print(describe_quality(listings))
        print("\n=== Market summary by neighborhood ===")
        print(market_summary(enriched))
        print(f"\n=== Top {args.top} value listings ($/sqft) ===")
        print(top_value_listings(enriched, n=args.top))
        print("\n=== Monthly listing volume ===")
        print(monthly_listing_volume(enriched))

    return 0


if __name__ == "__main__":
    sys.exit(main())
