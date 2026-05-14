"""Smoke test for the CLI entry point."""

from __future__ import annotations

import pytest

from real_estate_analysis.cli import main


def test_cli_runs_against_bundled_data(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["--top", "3"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Market summary by neighborhood" in captured.out
    assert "Top 3 value listings" in captured.out
    assert "Monthly listing volume" in captured.out
