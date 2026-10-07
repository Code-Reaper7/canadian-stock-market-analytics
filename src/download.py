"""Run from the project folder: python src/download.py"""
import json
import platform
from datetime import datetime, timezone
from importlib.metadata import version

import pandas as pd
import yfinance as yf

from config import COMPANIES, END, ROOT, START


def main():
    frames = []
    for symbol, _, _ in COMPANIES:
        print(f"Downloading {symbol}...", flush=True)
        prices = yf.download(
            symbol, start=START, end=END, interval="1d",
            auto_adjust=False, actions=False, progress=False,
            multi_level_index=False, threads=False, timeout=30,
        )
        if prices is None or prices.empty:
            raise RuntimeError(f"No data for {symbol}. No combined file written; retry later.")
        prices = prices.reset_index().rename(columns={
            "Date": "date", "Open": "open", "High": "high", "Low": "low",
            "Close": "close", "Adj Close": "adj_close", "Volume": "volume",
        })
        prices["symbol"] = symbol
        frames.append(prices[["symbol", "date", "open", "high", "low", "close", "adj_close", "volume"]])

    raw = ROOT / "data" / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    pd.concat(frames, ignore_index=True).to_csv(raw / "prices.csv", index=False)
    metadata = {
        "source": "Yahoo Finance via yfinance (unofficial client; not a TMX feed)",
        "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
        "start_inclusive": START, "end_exclusive": END,
        "symbols": [c[0] for c in COMPANIES], "auto_adjust": False,
        "python": platform.python_version(),
        "packages": {p: version(p) for p in ("pandas", "numpy", "yfinance")},
    }
    (raw / "metadata.json").write_text(json.dumps(metadata, indent=2))
    print("Saved data/raw/prices.csv and metadata.json. Next: python src/clean.py")


if __name__ == "__main__":
    main()
