"""Load Transport Canada National Collision Database CSVs (2019, 2020) into SQLite.

Column names and code labels below come from the NCDB layout as I know it; confirm them
against the data dictionary PDF. The script stops with a clear message if columns differ.
"""
import pathlib
import sqlite3
import sys

import numpy as np
import pandas as pd
import requests

BASE = "https://open.canada.ca/data/dataset/1eb9eba7-71d1-4b30-9fb1-30cbdab7e63a/resource"
FILES = {
    2019: f"{BASE}/1e2a6aa0-c35f-4736-984a-71f2eac1c1dc/download/2019_dataset_en.csv",
    2020: f"{BASE}/2164b2a7-a580-4708-bdac-8ab0c1304bc2/download/y_2020.csv",
}
DATA_DIR = pathlib.Path("data")
DB_PATH = "ncdb.db"

EXPECTED = ["C_YEAR", "C_MNTH", "C_WDAY", "C_HOUR", "C_SEV", "C_VEHS", "C_CONF", "C_RCFG",
            "C_WTHR", "C_RSUR", "C_RALN", "C_TRAF", "V_ID", "V_TYPE", "V_YEAR",
            "P_ID", "P_SEX", "P_AGE", "P_PSN", "P_ISEV", "P_SAFE", "P_USER"]

LABELS = {
    "C_SEV": {1: "Fatal", 2: "Injury"},
    "C_WDAY": {1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri", 6: "Sat", 7: "Sun"},
    "C_WTHR": {1: "Clear", 2: "Overcast", 3: "Raining", 4: "Snowing", 5: "Freezing rain",
               6: "Limited visibility", 7: "Strong wind"},
    "C_RSUR": {1: "Dry", 2: "Wet", 3: "Snow", 4: "Slush", 5: "Icy", 6: "Sand/gravel/dirt",
               7: "Muddy", 8: "Oil", 9: "Flooded"},
    "P_ISEV": {1: "No injury", 2: "Injury", 3: "Fatality"},
}


def download(year: int, url: str) -> pathlib.Path:
    DATA_DIR.mkdir(exist_ok=True)
    target = DATA_DIR / f"ncdb_{year}.csv"
    if target.exists():
        return target
    with requests.get(url, stream=True, timeout=120) as r:
        r.raise_for_status()
        with open(target, "wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 20):
                f.write(chunk)
    return target


def to_num(s: pd.Series) -> pd.Series:
    # NCDB uses letter codes (U, UU, N, NN, Q, QQ, X, XX...) for unknown or not applicable.
    return pd.to_numeric(s, errors="coerce")


def load_year(year: int) -> pd.DataFrame:
    df = pd.read_csv(download(year, FILES[year]), dtype=str)
    df.columns = [c.strip().upper() for c in df.columns]
    missing = [c for c in EXPECTED if c not in df.columns]
    if missing:
        sys.exit(f"{year}: columns not found {missing}. Actual columns: {list(df.columns)}")
    return df


def main() -> None:
    raw = pd.concat([load_year(y) for y in FILES], ignore_index=True)
    print(f"raw rows: {len(raw)}")

    for col in ["C_YEAR", "C_MNTH", "C_WDAY", "C_HOUR", "C_SEV", "C_VEHS", "C_WTHR", "C_RSUR",
                "V_ID", "V_YEAR", "P_ID", "P_AGE", "P_ISEV"]:
        raw[col] = to_num(raw[col])

    # Derive a collision ID: a new collision starts at vehicle 1, person 1.
    new_collision = (raw["V_ID"] == 1) & (raw["P_ID"] == 1)
    raw["collision_id"] = new_collision.cumsum()
    print(f"derived collisions: {raw['collision_id'].nunique()}")

    veh_per_collision = raw.groupby("collision_id")["V_ID"].nunique()
    declared = raw.groupby("collision_id")["C_VEHS"].first()
    both = pd.concat([veh_per_collision, declared], axis=1, keys=["observed", "declared"]).dropna()
    print(f"collision-ID check, vehicle count matches declared: {(both['observed'] == both['declared']).mean():.1%}")

    for col, mapping in LABELS.items():
        raw[col + "_LABEL"] = raw[col].map(mapping)
    raw.loc[raw["C_HOUR"] > 23, "C_HOUR"] = np.nan
    raw["age_band"] = pd.cut(raw["P_AGE"], [-1, 15, 24, 34, 44, 54, 64, 120],
                             labels=["<16", "16-24", "25-34", "35-44", "45-54", "55-64", "65+"]).astype(str)
    raw["vehicle_age"] = raw["C_YEAR"] - raw["V_YEAR"]
    raw.loc[(raw["vehicle_age"] < 0) | (raw["vehicle_age"] > 40), "vehicle_age"] = np.nan

    collisions = (raw.groupby("collision_id").agg(
        year=("C_YEAR", "first"), month=("C_MNTH", "first"), weekday=("C_WDAY_LABEL", "first"),
        hour=("C_HOUR", "first"), severity=("C_SEV_LABEL", "first"), vehicles=("C_VEHS", "first"),
        weather=("C_WTHR_LABEL", "first"), road_surface=("C_RSUR_LABEL", "first"),
        people=("P_ID", "size"),
    ).reset_index())

    persons = raw[["collision_id", "V_ID", "V_TYPE", "vehicle_age", "P_ID", "P_SEX", "P_AGE", "age_band",
                   "P_PSN", "P_USER", "P_ISEV_LABEL"]].rename(columns={
        "V_ID": "vehicle_id", "V_TYPE": "vehicle_type", "P_ID": "person_id", "P_SEX": "sex",
        "P_AGE": "age", "P_PSN": "position", "P_USER": "user_type", "P_ISEV_LABEL": "person_severity"})

    print(f"collisions: {len(collisions)}, persons: {len(persons)}")
    print("severity mix:", collisions["severity"].value_counts(dropna=False).to_dict())

    with sqlite3.connect(DB_PATH) as con:
        collisions.to_sql("collisions", con, if_exists="replace", index=False)
        persons.to_sql("persons", con, if_exists="replace", index=False)
    collisions.to_csv("collisions.csv", index=False)
    persons.to_csv("persons.csv", index=False)


if __name__ == "__main__":
    main()
