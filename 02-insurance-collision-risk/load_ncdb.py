"""Load Transport Canada National Collision Database CSVs (2019, 2020), clean them, and write the model tables.

Run:  python load_ncdb.py
Output: ncdb.db (SQLite, tables collisions, vehicles, persons). Then run build_star.py to write the star-schema CSVs in ./model/ for Power BI.

What the file is: one row per person in each vehicle in each police-reported fatal or injury collision.
Every code label below comes from the National Collision Database data dictionary (data/data_dictionary.pdf).

Findings that shape the cleaning (all checked in the printout):
  * The file has a collision key, C_CASE, that the data dictionary does not mention. It is unique per
    collision, contiguous, and the severity, hour, weather and road surface never change within a case,
    so it is the collision ID. An ID derived from "vehicle 1, person 1" splits and merges collisions.
  * Code formats differ between years ("2" in 2019, "02" in 2020), so codes are cast to numbers.
  * Unknown, other and "jurisdiction does not provide" use letter codes (U, UU, Q, QQ, X, XX, *, **),
    kept as "Unknown or not reported" and never as a real category or a zero.
  * Dummy rows: a parked car gets a dummy person (P_ID NN) and a pedestrian gets a dummy vehicle (V_ID 99).
    These are not people or vehicles, so the persons and vehicles tables keep only real ones.
"""
import pathlib
import sqlite3
import sys
import time

import numpy as np
import pandas as pd
import requests

BASE = "https://open.canada.ca/data/dataset/1eb9eba7-71d1-4b30-9fb1-30cbdab7e63a/resource"
FILES = {
    2019: f"{BASE}/1e2a6aa0-c35f-4736-984a-71f2eac1c1dc/download/2019_dataset_en.csv",
    2020: f"{BASE}/2164b2a7-a580-4708-bdac-8ab0c1304bc2/download/y_2020.csv",
}
DATA_DIR = pathlib.Path("data")
MODEL_DIR = pathlib.Path("model")
DB_PATH = "ncdb.db"
UNK = "Unknown or not reported"

EXPECTED = ["C_YEAR", "C_MNTH", "C_WDAY", "C_HOUR", "C_SEV", "C_VEHS", "C_CONF", "C_RCFG", "C_WTHR", "C_RSUR", "C_RALN",
            "C_TRAF", "V_ID", "V_TYPE", "V_YEAR", "P_ID", "P_SEX", "P_AGE", "P_PSN", "P_ISEV", "P_SAFE", "P_USER", "C_CASE"]

SEVERITY = {1: "Fatal", 2: "Injury"}
WEEKDAY = {1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri", 6: "Sat", 7: "Sun"}
WEATHER = {1: "Clear and sunny", 2: "Overcast", 3: "Raining", 4: "Snowing", 5: "Freezing rain or hail", 6: "Poor visibility", 7: "Strong wind"}
SURFACE = {1: "Dry", 2: "Wet", 3: "Snow", 4: "Slush", 5: "Icy", 6: "Sand, gravel or dirt", 7: "Muddy", 8: "Oil", 9: "Flooded"}
ALIGN = {1: "Straight and level", 2: "Straight with gradient", 3: "Curved and level", 4: "Curved with gradient", 5: "Top of a hill", 6: "Bottom of a hill"}
ROADCFG = {1: "Not at an intersection", 2: "Intersection", 3: "Parking lot or driveway entrance", 4: "Railway crossing", 5: "Bridge or overpass",
           6: "Tunnel or underpass", 7: "Passing or climbing lane", 8: "Ramp", 9: "Traffic circle", 10: "Freeway lane", 11: "Freeway lane", 12: "Freeway lane"}
CONF = {1: "Hit a moving object", 2: "Hit a stationary object", 3: "Ran off left shoulder", 4: "Ran off right shoulder", 5: "Rollover on roadway",
        6: "Other single-vehicle", 21: "Rear-end", 22: "Side swipe", 23: "Passing or left-turn conflict", 24: "Passing or right-turn conflict",
        25: "Other, same direction", 31: "Head-on", 32: "Approaching side swipe", 33: "Left turn across traffic", 34: "Right turn conflict",
        35: "Right angle", 36: "Other, different directions", 41: "Hit a parked vehicle"}


def conf_group(c):
    if pd.isna(c):
        return UNK
    c = int(c)
    return ("Single vehicle" if c <= 6 else "Two vehicles, same direction" if c <= 25 else "Two vehicles, different directions" if c <= 36 else "Hit a parked vehicle")


def traffic_group(c):
    if pd.isna(c):
        return UNK
    c = int(c)
    return ("Signals" if c in (1, 2) else "Stop or yield sign" if c in (3, 4) else "No control" if c == 18 else "Other control")


VTYPE = {1: "Car or light truck", 5: "Van", 6: "Van", 7: "Heavy truck", 8: "Heavy truck", 9: "Bus", 10: "Bus", 11: "Bus", 14: "Motorcycle or moped",
         16: "Off-road vehicle", 17: "Bicycle", 18: "Motorhome", 19: "Farm equipment", 20: "Construction equipment", 21: "Emergency vehicle",
         22: "Snowmobile", 23: "Streetcar"}
USER = {1: "Driver", 2: "Passenger", 3: "Pedestrian", 4: "Bicyclist", 5: "Motorcyclist"}
SAFE = {1: "No safety device used", 2: "Safety device used", 9: "Helmet worn", 10: "Reflective clothing", 11: "Helmet and reflective clothing",
        12: "Other safety device", 13: "No safety device equipped"}
PSEV = {1: "No injury", 2: "Injury", 3: "Fatality"}
AGE_BANDS = ["Under 16", "16-24", "25-34", "35-44", "45-54", "55-64", "65 and over"]


def download(year: int, url: str) -> pathlib.Path:
    DATA_DIR.mkdir(exist_ok=True)
    target = DATA_DIR / f"ncdb_{year}.csv"
    if target.exists():
        return target
    for attempt in range(6):   # open.canada.ca answers 429 when called twice in a row, so wait and retry
        with requests.get(url, stream=True, timeout=120, headers={"User-Agent": "Mozilla/5.0 (portfolio research)"}) as r:
            if r.status_code == 429:
                time.sleep(20 * (attempt + 1))
                continue
            r.raise_for_status()
            with open(target, "wb") as f:
                for chunk in r.iter_content(chunk_size=1 << 20):
                    f.write(chunk)
            return target
    raise RuntimeError(f"{year}: still rate limited after retries")


def num(s: pd.Series) -> pd.Series:
    """Letter codes (U, UU, Q, QQ, X, XX, N, NN, *) become missing; "02" and "2" both become 2."""
    return pd.to_numeric(s, errors="coerce")


def label(s: pd.Series, mapping: dict) -> pd.Series:
    return s.map(mapping).fillna(UNK)


def load_year(year: int) -> pd.DataFrame:
    df = pd.read_csv(download(year, FILES[year]), dtype=str)
    df.columns = [c.strip().upper() for c in df.columns]
    missing = [c for c in EXPECTED if c not in df.columns]
    if missing:
        sys.exit(f"{year}: columns not found {missing}. Actual columns: {list(df.columns)}")
    df["src_year"] = year
    return df


def main() -> None:
    raw = pd.concat([load_year(y) for y in FILES], ignore_index=True)
    print(f"raw rows: {len(raw):,} ({raw.groupby('src_year').size().to_dict()})")
    raw["collision_id"] = raw["src_year"].astype(str) + "-" + raw["C_CASE"].astype(str)

    # ---- is C_CASE a usable collision key? (these are the checks behind the decision)
    g = raw.groupby("collision_id")
    print(f"collisions by C_CASE: {g.ngroups:,} | C_CASE values shared by both years: {raw.groupby('C_CASE').src_year.nunique().gt(1).sum()}")
    for c in ["C_SEV", "C_HOUR", "C_WDAY", "C_MNTH", "C_WTHR", "C_RSUR"]:
        print(f"  {c} changes within a collision in {int(g[c].nunique().gt(1).sum())} collisions")
    blocks = (raw["collision_id"] != raw["collision_id"].shift()).sum()
    print(f"  collisions are contiguous blocks: {blocks == g.ngroups}")
    vid, pid = num(raw["V_ID"]), num(raw["P_ID"])
    real_veh = raw.assign(v=vid)[vid < 99].groupby("collision_id")["v"].nunique()
    declared = raw.assign(d=num(raw["C_VEHS"])).groupby("collision_id")["d"].first()
    both = pd.concat([real_veh, declared], axis=1, keys=["seen", "declared"]).dropna()
    print(f"  vehicle count seen equals vehicle count declared: {(both.seen == both.declared).mean():.1%}")
    old_start = (vid == 1) & (pid == 1)
    print(f"  the old 'vehicle 1, person 1' rule would find {int(old_start.sum()):,} collisions, not {g.ngroups:,}")

    # ---- collisions (one row per collision)
    first = g.first()
    persons_raw = raw.assign(P=pid, A=num(raw["P_AGE"]), S=num(raw["P_ISEV"]))
    real_people = persons_raw[persons_raw["P"].notna()]
    killed = real_people[real_people["S"] == 3].groupby("collision_id").size()
    hurt = real_people[real_people["S"] == 2].groupby("collision_id").size()
    people_n = real_people.groupby("collision_id").size()
    veh_n = raw[vid < 99].assign(v=vid).groupby("collision_id")["v"].nunique()
    c = pd.DataFrame({
        "year": num(first["C_YEAR"]).astype("Int64"),
        "month": num(first["C_MNTH"]).astype("Int64"),
        "weekday_num": num(first["C_WDAY"]).astype("Int64"),
        "hour": num(first["C_HOUR"]).astype("Int64"),
        "severity": label(num(first["C_SEV"]), SEVERITY),
        "vehicles_declared": num(first["C_VEHS"]).astype("Int64"),
        "vehicles_seen": veh_n.reindex(first.index).astype("Int64"),
        "people": people_n.reindex(first.index).fillna(0).astype(int),
        "killed": killed.reindex(first.index).fillna(0).astype(int),
        "injured": hurt.reindex(first.index).fillna(0).astype(int),
        "configuration": label(num(first["C_CONF"]), CONF),
        "configuration_group": num(first["C_CONF"]).map(conf_group),
        "road_layout": label(num(first["C_RCFG"]), ROADCFG),
        "weather": label(num(first["C_WTHR"]), WEATHER),
        "road_surface": label(num(first["C_RSUR"]), SURFACE),
        "road_alignment": label(num(first["C_RALN"]), ALIGN),
        "traffic_control": num(first["C_TRAF"]).map(traffic_group),
    })
    c["weekday"] = c["weekday_num"].map(WEEKDAY).fillna(UNK)
    c.loc[c["hour"] > 23, "hour"] = pd.NA
    c.index.name = "collision_id"
    c = c.reset_index()

    # ---- vehicles (real vehicles only: V_ID 99 is a pedestrian, UU is an unmatched person)
    v = raw[(vid < 99)].copy()
    v["V"] = num(v["V_ID"])
    vv = v.groupby(["collision_id", "V"]).agg(vehicle_type_code=("V_TYPE", "first"), model_year=("V_YEAR", "first"), occupants=("P_ID", "size")).reset_index()
    vv["vehicle_type"] = label(num(vv["vehicle_type_code"]), VTYPE)
    myear = num(vv["model_year"])
    cyear = vv["collision_id"].map(c.set_index("collision_id")["year"]).astype(float)
    vv["vehicle_age"] = (cyear - myear).where((cyear - myear).between(0, 40))
    vv["vehicle_age_band"] = pd.cut(vv["vehicle_age"], [-1, 3, 7, 12, 40], labels=["0-3 years", "4-7 years", "8-12 years", "13 years or more"]).astype(object).fillna(UNK)
    vv = vv.rename(columns={"V": "vehicle_seq"})[["collision_id", "vehicle_seq", "vehicle_type", "vehicle_age", "vehicle_age_band", "occupants"]]

    # ---- persons (real people only: P_ID NN is a dummy for a parked car, UU is a runaway vehicle)
    p = real_people.copy()
    p["age"] = p["A"].where(p["A"].between(0, 99))
    p["age_band"] = pd.cut(p["age"], [-1, 15, 24, 34, 44, 54, 64, 120], labels=AGE_BANDS).astype(object).fillna(UNK)
    p["sex"] = p["P_SEX"].map({"M": "Male", "F": "Female"}).fillna(UNK)
    p["user_type"] = label(num(p["P_USER"]), USER)
    p["safety_device"] = label(num(p["P_SAFE"]), SAFE)
    p["person_severity"] = label(p["S"], PSEV)
    p["position"] = np.where(num(p["P_PSN"]) == 11, "Driver", np.where(num(p["P_PSN"]) == 99, "Pedestrian", np.where(num(p["P_PSN"]).isin([12, 13, 21, 22, 23, 31, 32, 33, 96, 97, 98]), "Passenger", UNK)))
    p["vehicle_seq"] = num(p["V_ID"]).where(num(p["V_ID"]) < 99)
    persons = p[["collision_id", "vehicle_seq", "P", "sex", "age", "age_band", "user_type", "position", "safety_device", "person_severity"]].rename(columns={"P": "person_seq"})
    persons = persons.merge(vv[["collision_id", "vehicle_seq", "vehicle_type", "vehicle_age_band"]], on=["collision_id", "vehicle_seq"], how="left")
    persons["vehicle_type"] = persons["vehicle_type"].fillna(pd.Series(np.where(persons["user_type"] == "Pedestrian", "No vehicle (pedestrian)", UNK), index=persons.index))
    persons["vehicle_age_band"] = persons["vehicle_age_band"].fillna(pd.Series(np.where(persons["user_type"] == "Pedestrian", "Not applicable", UNK), index=persons.index))
    for col_ in ["vehicle_seq", "person_seq", "age"]:
        persons[col_] = persons[col_].astype("Int64")

    # ---- checks
    print(f"\ncollisions: {len(c):,} ({c.groupby('year').size().to_dict()}) | vehicles: {len(vv):,} | persons: {len(persons):,} "
          f"(of {len(raw):,} rows; {len(raw) - len(persons):,} are dummy or unmatched records)")
    print("severity mix:", c.severity.value_counts().to_dict())
    print("fatalities in persons table:", int((persons.person_severity == "Fatality").sum()), "| killed summed on collisions:", int(c.killed.sum()))
    print("fatal collisions with no fatality person row:", int(((c.severity == "Fatal") & (c.killed == 0)).sum()),
          "| injury collisions that have a fatality row:", int(((c.severity == "Injury") & (c.killed > 0)).sum()))
    for col in ["hour", "weather", "road_surface", "road_alignment", "traffic_control", "configuration"]:
        s_ = c[col]
        miss = s_.isna().mean() if col == "hour" else (s_ == UNK).mean()
        print(f"  unknown share, {col}: {miss:.1%}")
    print(f"  person age unknown: {(persons.age_band == UNK).mean():.1%} | sex unknown: {(persons.sex == UNK).mean():.1%}")

    with sqlite3.connect(DB_PATH) as con:
        c.to_sql("collisions", con, if_exists="replace", index=False)
        vv.to_sql("vehicles", con, if_exists="replace", index=False)
        persons.to_sql("persons", con, if_exists="replace", index=False)


if __name__ == "__main__":
    main()
