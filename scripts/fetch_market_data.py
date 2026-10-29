#!/usr/bin/env python3
"""Market Data Downloader & Matrix Updater for Nasdaq-100 Constituents.

Fetches daily OHLCV bars via yfinance for the 101 Nasdaq-100 constituents,
benchmark QQQ, cash proxy BIL, and price index ^NDX.
Updates the persistent CSV matrices in the data/ directory.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"


def load_universe(universe_path: Path) -> list[str]:
    """Load unique ticker list from universe CSV."""
    df = pd.read_csv(universe_path)
    ticker_col = "ticker" if "ticker" in df.columns else df.columns[0]
    return df[ticker_col].dropna().unique().tolist()


def update_matrices(
    start_date: str = "2010-01-01",
    end_date: str | None = None,
    universe_path: Path | None = None,
) -> None:
    """Fetch recent market data and update persistent matrix CSVs."""
    try:
        import yfinance as yf
    except ImportError:
        print("[!] Error: 'yfinance' is not installed. Run: pip install yfinance")
        sys.exit(1)

    if universe_path is None:
        universe_path = DATA_DIR / "local_snapshot_universe.csv"

    tickers = load_universe(universe_path)
    symbols = sorted(set(tickers) | {"QQQ", "BIL", "^NDX", "^IXIC"})

    print(f"[*] Target universe: {len(symbols)} symbols (101 constituents + benchmarks)")
    print(f"[*] Downloading daily OHLCV from {start_date} to {end_date or 'today'}...")

    raw = yf.download(
        symbols,
        start=start_date,
        end=end_date,
        auto_adjust=False,
        actions=False,
        threads=True,
        progress=True,
    )

    if raw.empty:
        print("[!] Warning: No data downloaded from yfinance. Check network connection.")
        return

    # Extract adjusted matrices
    close_raw = raw["Close"]
    adj_close = raw["Adj Close"]
    open_raw = raw["Open"]
    high_raw = raw["High"]
    low_raw = raw["Low"]
    volume_raw = raw["Volume"]

    # Compute adjustment factor: Adj Close / Close
    factor = adj_close / close_raw.replace(0, np.nan)
    factor = factor.fillna(1.0)

    open_adj = open_raw * factor
    high_adj = high_raw * factor
    low_adj = low_raw * factor

    # Align dates with QQQ trading calendar
    valid_sessions = adj_close["QQQ"].dropna().index
    open_adj = open_adj.reindex(index=valid_sessions)
    high_adj = high_adj.reindex(index=valid_sessions)
    low_adj = low_adj.reindex(index=valid_sessions)
    adj_close = adj_close.reindex(index=valid_sessions)
    volume_raw = volume_raw.reindex(index=valid_sessions)
    close_raw = close_raw.reindex(index=valid_sessions)

    # Save to CSV
    open_adj.to_csv(DATA_DIR / "open.csv")
    high_adj.to_csv(DATA_DIR / "high.csv")
    low_adj.to_csv(DATA_DIR / "low.csv")
    adj_close.to_csv(DATA_DIR / "close.csv")
    volume_raw.to_csv(DATA_DIR / "volume.csv")
    close_raw.to_csv(DATA_DIR / "raw_close.csv")

    print(f"[+] Successfully updated data matrices! Total sessions: {len(valid_sessions)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", default="2010-01-01", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", default=None, help="End date (YYYY-MM-DD)")
    parser.add_argument("--universe", type=Path, default=None, help="Path to universe CSV")
    args = parser.parse_args()

    update_matrices(args.start, args.end, args.universe)


if __name__ == "__main__":
    main()
