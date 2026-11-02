"""Download Toronto 311 yearly ZIPs, repair malformed rows, load into SQLite and build staging tables.

Usage:
    python load_311.py --list
    python load_311.py --years 2023 2024 2025

Findings from inspecting the files (document these in the case study):
  * Columns: Creation Date, Status, First 3 Chars of Postal Code, Intersection Street 1/2, Ward,
    Service Request Type, Division, Section.
  * There is NO close date, so time to close cannot be measured.
  * About 8% of rows have an unquoted comma inside the Division value
    ("Parks, Forestry & Recreation"), giving 10 fields instead of 9. They are repaired here.
"""
import argparse
import csv
import io
import re
import sqlite3
import zipfile

import pandas as pd
import requests

BASE = "https://ckan0.cf.opendata.inter.prod-toronto.ca"
PACKAGE_ID = "311-service-requests-customer-initiated"
DB_PATH = "311.db"

COLUMNS = ["created_ts", "status", "fsa", "intersection_1", "intersection_2",
           "ward", "service_request_type", "division", "section"]
COMMA_DIVISIONS = {"Parks, Forestry & Recreation", "Environment, Climate & Forestry"}
DIVISION_GROUP = {
    "Parks, Forestry & Recreation": "Parks, Forestry & Environment",
    "Environment, Climate & Forestry": "Parks, Forestry & Environment",
    "Parks and Recreation": "Parks, Forestry & Environment",
}
STATUS_GROUP = {"Completed": "Resolved", "Closed": "Resolved", "Cancelled": "Cancelled",
                "Canceled": "Cancelled", "New": "Open", "In Progress": "Open", "Unknown": "Unknown"}


def get_package() -> dict:
    r = requests.get(f"{BASE}/api/3/action/package_show", params={"id": PACKAGE_ID}, timeout=60)
    r.raise_for_status()
    return r.json()["result"]


def parse_csv(text: str, year: int) -> tuple[pd.DataFrame, dict]:
    reader = csv.reader(io.StringIO(text))
    next(reader)  # header
    rows, stats = [], {"fields_9": 0, "fields_10_repaired": 0, "skipped": 0}
    for r in reader:
        if len(r) == 9:
            stats["fields_9"] += 1
        elif len(r) == 10:
            # Unquoted comma. Nearly always inside Division (e.g. "Parks, Forestry & Recreation");
            # a handful are inside Section.
            if (r[7] + "," + r[8]).strip() in COMMA_DIVISIONS:
                r = r[:7] + [(r[7] + "," + r[8]).strip()] + [r[9]]
            else:
                r = r[:8] + [(r[8] + "," + r[9]).strip()]
            stats["fields_10_repaired"] += 1
        else:
            stats["skipped"] += 1
            continue
        rows.append([c.strip() for c in r])
    df = pd.DataFrame(rows, columns=COLUMNS)
    df["source_year"] = year
    return df, stats


def read_zip(url: str, year: int) -> pd.DataFrame:
    r = requests.get(url, timeout=300)
    r.raise_for_status()
    frames = []
    with zipfile.ZipFile(io.BytesIO(r.content)) as zf:
        for name in zf.namelist():
            if name.lower().endswith(".csv"):
                text = zf.read(name).decode("utf-8", errors="replace")
                df, stats = parse_csv(text, year)
                print(f"{year} {name}: {len(df)} rows, parse stats {stats}")
                frames.append(df)
    return pd.concat(frames, ignore_index=True)


def stage(raw: pd.DataFrame) -> pd.DataFrame:
    s = raw.copy()
    s["created_ts"] = pd.to_datetime(s["created_ts"], errors="coerce")
    s["created_date"] = s["created_ts"].dt.date.astype(str)
    s["year"] = s["created_ts"].dt.year
    s["month"] = s["created_ts"].dt.strftime("%Y-%m")
    s["weekday"] = s["created_ts"].dt.day_name()
    s["hour"] = s["created_ts"].dt.hour
    s["status_group"] = s["status"].map(STATUS_GROUP).fillna("Unknown")
    s["location_type"] = s["fsa"].apply(lambda v: "Intersection" if v.lower() == "intersection" else "Postal area")
    s["ward_name"] = s["ward"].str.replace(r"\s*\(\d+\)$", "", regex=True)
    s["ward_no"] = pd.to_numeric(s["ward"].str.extract(r"\((\d+)\)$")[0], errors="coerce")
    for c in ("division", "section", "service_request_type", "ward"):
        s[c] = s[c].replace("", pd.NA)
    # The Parks/Forestry division was renamed and split in 2025; group the lineage for comparisons.
    s["division_group"] = s["division"].replace(DIVISION_GROUP)
    return s


def aggregate(stg: pd.DataFrame) -> pd.DataFrame:
    """Month-level table for Power BI (small enough to import without a row-level model)."""
    return (stg.groupby(["month", "year", "division_group", "service_request_type", "ward_name",
                         "status_group", "location_type"], dropna=False)
               .size().reset_index(name="requests"))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--years", nargs="*", type=int, default=[])
    args = ap.parse_args()

    pkg = get_package()
    print(pkg["title"], "|", pkg.get("license_title"), "| refresh:", pkg.get("refresh_rate"))
    if args.list or not args.years:
        for res in pkg["resources"]:
            print(f'{res["format"]:5} {res["name"]}')
        return

    frames = []
    for year in args.years:
        res = next((x for x in pkg["resources"]
                    if x["format"].upper() == "ZIP" and re.search(rf"\b{year}\b", x["name"])), None)
        if res is None:
            print(f"no ZIP resource found for {year}")
            continue
        frames.append(read_zip(res["url"], year))
    if not frames:
        return

    raw = pd.concat(frames, ignore_index=True)
    stg = stage(raw)
    print(f"\nstaging rows: {len(stg)}")
    print("null created_ts:", int(stg["created_ts"].isna().sum()))
    print("status counts:", stg["status"].value_counts().to_dict())

    with sqlite3.connect(DB_PATH) as con:
        stg.to_sql("stg_requests", con, if_exists="replace", index=False)
        con.execute("CREATE INDEX IF NOT EXISTS ix_month ON stg_requests(month)")
    agg = aggregate(stg)
    agg.to_csv("requests_monthly_agg.csv", index=False)
    print(f"aggregate rows for Power BI: {len(agg)}; total requests preserved: {agg['requests'].sum() == len(stg)}")


if __name__ == "__main__":
    main()
