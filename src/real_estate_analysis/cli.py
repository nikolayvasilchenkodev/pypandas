"""Command-line entry point printing a quick market report."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import pandas as pd
from rich.box import SIMPLE_HEAVY
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

from real_estate_analysis.analysis import (
    market_summary,
    monthly_listing_volume,
    top_value_listings,
)
from real_estate_analysis.data import describe_quality, load_listings
from real_estate_analysis.features import add_engineered_features

_NUMERIC_KINDS = "iufc"


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
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI colors (useful for piping).",
    )
    return parser


def _fmt_cell(value: object) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return Text("—", style="dim").plain  # type: ignore[return-value]
    if isinstance(value, float):
        if value.is_integer():
            return f"{int(value):,}"
        return f"{value:,.2f}"
    if isinstance(value, int):
        return f"{value:,}"
    if isinstance(value, pd.Timestamp):
        return value.strftime("%Y-%m-%d")
    return str(value)


def _df_to_table(
    df: pd.DataFrame,
    *,
    title: str,
    index_label: str | None = None,
    caption: str | None = None,
) -> Table:
    table = Table(
        title=Text(title, style="bold cyan"),
        title_justify="left",
        box=SIMPLE_HEAVY,
        header_style="bold magenta",
        show_lines=False,
        pad_edge=False,
        caption=caption,
        caption_style="dim italic",
    )

    show_index = index_label is not None or df.index.name is not None
    if show_index:
        label = index_label or (df.index.name or "")
        table.add_column(str(label), style="bold yellow", no_wrap=True)

    for col in df.columns:
        numeric = df[col].dtype.kind in _NUMERIC_KINDS
        table.add_column(
            str(col),
            justify="right" if numeric else "left",
            style="green" if numeric else "white",
            overflow="fold",
        )

    for idx, row in df.iterrows():
        cells: list[str] = []
        if show_index:
            cells.append(_fmt_cell(idx))
        cells.extend(_fmt_cell(v) for v in row.tolist())
        table.add_row(*cells)

    return table


def _series_to_table(s: pd.Series, *, title: str, index_label: str) -> Table:
    return _df_to_table(s.to_frame(), title=title, index_label=index_label)


def _header(console: Console, csv_path: Path | None, n_rows: int) -> None:
    src = str(csv_path) if csv_path else "bundled sample dataset"
    body = Text.from_markup(
        f"[bold]Real-Estate Market Report[/bold]\n"
        f"[dim]source[/dim] {src}\n"
        f"[dim]rows  [/dim] {n_rows:,}"
    )
    console.print(Panel(body, border_style="cyan", expand=False, padding=(0, 2)))


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    console = Console(
        no_color=args.no_color,
        highlight=False,
        soft_wrap=False,
        width=None if sys.stdout.isatty() else 140,
    )
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(message)s",
        datefmt="%H:%M:%S",
        handlers=[RichHandler(console=console, rich_tracebacks=True, show_path=False)],
    )

    listings = load_listings(args.csv)
    enriched = add_engineered_features(listings)

    _header(console, args.csv, len(listings))

    console.print(Rule(style="cyan"))
    console.print(_df_to_table(describe_quality(listings), title="Data quality", index_label="column"))

    console.print(Rule(style="cyan"))
    console.print(_df_to_table(market_summary(enriched), title="Market summary by neighborhood"))

    console.print(Rule(style="cyan"))
    console.print(
        _df_to_table(
            top_value_listings(enriched, n=args.top),
            title=f"Top {args.top} value listings ($/sqft)",
        )
    )

    console.print(Rule(style="cyan"))
    console.print(
        _series_to_table(
            monthly_listing_volume(enriched),
            title="Monthly listing volume",
            index_label="month",
        )
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
