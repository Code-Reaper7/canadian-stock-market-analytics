"""Validate source data; calculate metrics independently for each symbol."""
import json

import numpy as np
import pandas as pd

from config import COMPANIES, ROOT

FIELDS = ["symbol", "date", "open", "high", "low", "close", "adj_close", "volume"]


def clean_prices(raw):
    missing = set(FIELDS) - set(raw.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    df = raw[FIELDS].copy()
    input_rows = len(df)
    if df.empty:
        raise ValueError("No data to clean")
    df["date"] = pd.to_datetime(df["date"], errors="raise").dt.normalize()
    if df["date"].dt.tz is not None:
        df["date"] = df["date"].dt.tz_localize(None)
    for col in FIELDS[2:]:
        df[col] = pd.to_numeric(df[col], errors="raise")
    if df.isna().any().any() or not np.isfinite(df[FIELDS[2:]].to_numpy()).all():
        raise ValueError("Missing or non-finite values: inspect raw data; do not fill prices blindly")
    df = df.drop_duplicates()  # Only exact duplicates are safe to remove.
    if df.duplicated(["symbol", "date"]).any():
        raise ValueError("Conflicting prices for the same symbol/date")
    if (df[FIELDS[2:7]] <= 0).any().any():
        raise ValueError("Prices must be positive")
    if ((df.volume < 0) | (df.volume % 1 != 0)).any():
        raise ValueError("Volume must be a nonnegative whole number")
    if ((df.high < df[["open", "close", "low"]].max(axis=1)) |
            (df.low > df[["open", "close", "high"]].min(axis=1))).any():
        raise ValueError("OHLC range inconsistency")
    df["volume"] = df.volume.astype("int64")
    df = df.sort_values(["symbol", "date"]).reset_index(drop=True)
    groups = df.groupby("symbol", sort=False)
    # Matched dates prevent comparing stocks over different available periods.
    calendars = [set(g.date) for _, g in groups]
    if any(dates != calendars[0] for dates in calendars[1:]):
        raise ValueError("Symbols have different dates; investigate missing observations before comparison")
    df["daily_return"] = groups.adj_close.pct_change(fill_method=None)
    df["ma30"] = groups.adj_close.transform(lambda s: s.rolling(30, min_periods=30).mean())
    df["indexed_value"] = groups.adj_close.transform(lambda s: 100 * s / s.iloc[0])
    df["drawdown"] = groups.adj_close.transform(lambda s: s / s.cummax() - 1)

    summary = []
    for symbol, g in df.groupby("symbol"):
        summary.append({
            "symbol": symbol, "start_date": g.date.iloc[0], "end_date": g.date.iloc[-1],
            "observations": len(g),
            "period_return": g.adj_close.iloc[-1] / g.adj_close.iloc[0] - 1,
            "avg_daily_volume": g.volume.mean(),
            "annualized_volatility": g.daily_return.std(ddof=1) * np.sqrt(252),
            "max_drawdown": g.drawdown.min(),
        })
    report = {
        "input_rows": input_rows, "output_rows": len(df),
        "exact_duplicates_removed": input_rows - len(df),
        "zero_volume_rows": int((df.volume == 0).sum()),
        "date_coverage": {s: {"rows": len(g), "first": str(g.date.min().date()),
                              "last": str(g.date.max().date())} for s, g in groups},
        "note": "Identical symbol calendars checked; not independently verified against an exchange calendar.",
    }
    return df, pd.DataFrame(summary), report


def main():
    raw = pd.read_csv(ROOT / "data/raw/prices.csv")
    expected = {s for s, _, _ in COMPANIES}
    if set(raw.symbol) != expected:
        raise ValueError("Downloaded symbols do not match the configured study sample")
    daily, summary, quality = clean_prices(raw)
    companies = pd.DataFrame(COMPANIES, columns=["symbol", "company", "sector"])
    summary = summary.merge(companies, on="symbol", validate="one_to_one")
    out = ROOT / "data/processed"
    out.mkdir(parents=True, exist_ok=True)
    daily.to_csv(out / "daily_metrics.csv", index=False)
    summary.to_csv(out / "stock_summary.csv", index=False)
    companies.to_csv(out / "companies.csv", index=False)
    (out / "quality_report.json").write_text(json.dumps(quality, indent=2))
    print(summary[["symbol", "period_return", "annualized_volatility"]].to_string(index=False))
    print("Saved validated metrics. Returns are decimals: 0.10 means 10%.")


if __name__ == "__main__":
    main()
