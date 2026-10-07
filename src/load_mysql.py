"""Load validated data into tables created by sql/schema.sql, then export SQL views."""
import argparse
from getpass import getpass

import numpy as np
import pandas as pd
from sqlalchemy import MetaData, Table, create_engine, text
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.engine import URL

from clean import FIELDS
from config import ROOT


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", default="root")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=3306)
    args = parser.parse_args()
    engine = create_engine(URL.create("mysql+pymysql", username=args.user,
        password=getpass("MySQL password: "), host=args.host, port=args.port,
        database="canadian_market"))
    folder = ROOT / "data/processed"
    prices = pd.read_csv(folder / "daily_metrics.csv")[FIELDS]
    prices["date"] = pd.to_datetime(prices.date).dt.date
    companies = pd.read_csv(folder / "companies.csv")
    try:
        with engine.begin() as conn:
            # Updates matching keys; preserves unrelated tables and data.
            for name, frame, keys in [("companies", companies, ["symbol"]),
                                       ("prices", prices, ["symbol", "date"])]:
                table = Table(name, MetaData(), autoload_with=conn)
                records = frame.to_dict("records")
                for start in range(0, len(records), 500):
                    stmt = insert(table).values(records[start:start + 500])
                    conn.execute(stmt.on_duplicate_key_update(**{
                        c: stmt.inserted[c] for c in frame.columns if c not in keys}))
            # File is checked-in project SQL, not user-submitted query text.
            for statement in (ROOT / "sql/analysis.sql").read_text().split(";"):
                if statement.strip():
                    conn.execute(text(statement))
        with engine.connect() as conn:
            summary = pd.read_sql(text("SELECT * FROM stock_summary ORDER BY symbol"), conn)
            daily = pd.read_sql(text("SELECT * FROM daily_metrics ORDER BY symbol, date"), conn)
        # Check SQL's independently calculated results against the Pandas results.
        expected = pd.read_csv(folder / "stock_summary.csv").sort_values("symbol")
        if summary.symbol.tolist() != expected.symbol.tolist():
            raise ValueError("Database contains a different stock sample; use a fresh project database")
        for col in ["observations", "period_return", "avg_daily_volume", "annualized_volatility", "max_drawdown"]:
            np.testing.assert_allclose(summary[col], expected[col], rtol=1e-8, atol=1e-10, equal_nan=True)
        expected_daily = pd.read_csv(folder / "daily_metrics.csv").sort_values(["symbol", "date"])
        if len(daily) != len(expected_daily):
            raise ValueError("Database date coverage differs from the current input")
        actual_keys = list(zip(daily.symbol, pd.to_datetime(daily.date)))
        expected_keys = list(zip(expected_daily.symbol, pd.to_datetime(expected_daily.date)))
        if actual_keys != expected_keys:
            raise ValueError("Database keys differ from the current input")
        for col in ["daily_return", "ma30", "indexed_value", "drawdown"]:
            np.testing.assert_allclose(daily[col], expected_daily[col], rtol=1e-8, atol=1e-10, equal_nan=True)
        output = ROOT / "data/powerbi"
        output.mkdir(parents=True, exist_ok=True)
        daily.to_csv(output / "daily_metrics.csv", index=False)
        summary.to_csv(output / "stock_summary.csv", index=False)
        companies.to_csv(output / "companies.csv", index=False)
        print("MySQL loaded; SQL/Pandas summary checks passed; Power BI CSVs exported.")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
