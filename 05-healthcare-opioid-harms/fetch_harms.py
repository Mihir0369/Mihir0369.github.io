"""Download PHAC Opioid- and Stimulant-related Harms CSV and load it into SQLite.

Prints columns and distinct values so you can write the analysis queries against the real schema.
"""
import io
import re
import sqlite3

import pandas as pd
import requests

CSV_URL = "https://health-infobase.canada.ca/api/opioids/linked/export/opioids/csv"
DB_PATH = "harms.db"


def normalize(cols):
    return [re.sub(r"[^0-9a-z]+", "_", c.strip().lower()).strip("_") for c in cols]


def main() -> None:
    resp = requests.get(CSV_URL, timeout=120)
    resp.raise_for_status()
    df = pd.read_csv(io.BytesIO(resp.content), encoding="utf-8", encoding_errors="replace", low_memory=False)
    df.columns = normalize(df.columns)
    print(f"rows: {len(df)}, columns: {len(df.columns)}")
    print(list(df.columns))
    print()
    for col in df.columns:
        n = df[col].nunique(dropna=True)
        if 1 < n <= 30:
            print(f"{col} ({n} values): {sorted(df[col].dropna().astype(str).unique())}")
        else:
            print(f"{col}: {n} distinct, {df[col].isna().mean():.0%} null")

    with sqlite3.connect(DB_PATH) as con:
        df.to_sql("harms", con, if_exists="replace", index=False)
    df.to_csv("harms.csv", index=False)


if __name__ == "__main__":
    main()
