"""Pull Canadian rates (Bank of Canada Valet) and household credit tables (Statistics Canada) into SQLite."""
import io
import sqlite3
import zipfile

import pandas as pd
import requests

DB_PATH = "banking.db"
START_DATE = "2010-01-01"

VALET_URL = "https://www.bankofcanada.ca/valet/observations/{series}/json"
SERIES = {
    "V39079": "overnight_target",
    "V80691311": "prime_rate",
    "V80691333": "mortgage_1y",
    "V80691334": "mortgage_3y",
    "V80691335": "mortgage_5y",
}

STATCAN_URL = "https://www150.statcan.gc.ca/n1/tbl/csv/{pid}-eng.zip"
STATCAN_TABLES = {
    "36100639": "credit_liabilities_households",
    "38100238": "household_credit_summary",
    "11100065": "household_debt_service",
}


def fetch_rates() -> pd.DataFrame:
    url = VALET_URL.format(series=",".join(SERIES))
    resp = requests.get(url, params={"start_date": START_DATE}, timeout=60)
    resp.raise_for_status()
    rows = []
    for obs in resp.json()["observations"]:
        row = {"date": obs["d"]}
        for code, name in SERIES.items():
            row[name] = float(obs[code]["v"]) if code in obs and obs[code].get("v") else None
        rows.append(row)
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    return df


def to_monthly(df: pd.DataFrame) -> pd.DataFrame:
    m = df.set_index("date").resample("MS").last().reset_index()
    m["month"] = m["date"].dt.strftime("%Y-%m")
    return m


def fetch_statcan(pid: str) -> pd.DataFrame:
    resp = requests.get(STATCAN_URL.format(pid=pid), timeout=120)
    resp.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        with zf.open(f"{pid}.csv") as f:
            df = pd.read_csv(f, low_memory=False)
    df.columns = [c.strip().lower().replace(" ", "_").replace("-", "_") for c in df.columns]
    return df


def main() -> None:
    rates = fetch_rates()
    monthly = to_monthly(rates)
    print(f"rates: {len(rates)} observations, monthly: {len(monthly)} rows, "
          f"{monthly['date'].min():%Y-%m} to {monthly['date'].max():%Y-%m}")

    with sqlite3.connect(DB_PATH) as con:
        rates.to_sql("rates_daily", con, if_exists="replace", index=False)
        monthly.to_sql("rates_monthly", con, if_exists="replace", index=False)
        monthly.to_csv("rates_monthly.csv", index=False)

        for pid, name in STATCAN_TABLES.items():
            df = fetch_statcan(pid)
            df.to_sql(name, con, if_exists="replace", index=False)
            df.to_csv(f"{name}.csv", index=False)
            print(f"\n{name} ({pid}): {len(df)} rows, columns: {list(df.columns)}")
            for col in df.columns:
                if col in {"ref_date", "value", "dguid", "uom_id", "scalar_id", "vector", "coordinate",
                           "status", "symbol", "terminated", "decimals"}:
                    continue
                values = df[col].dropna().unique()
                if 1 < len(values) <= 25:
                    print(f"  {col}: {list(values)}")
            print(f"  period: {df['ref_date'].min()} to {df['ref_date'].max()}")


if __name__ == "__main__":
    main()
