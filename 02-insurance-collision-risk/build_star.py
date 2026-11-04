"""Turn the cleaned SQLite tables into a star schema for Power BI: two fact tables and fifteen dimensions.

Run after load_ncdb.py:  python build_star.py        (writes CSVs to ./model/)

Why a star schema: the model, not the visuals, is what makes the numbers trustworthy. Each fact table holds keys and
counts only; every label, group and sort order lives in a dimension, and "unknown" is a real member (key 0) of each
dimension, so no row falls out of a chart as (Blank).
"""
import pathlib
import sqlite3

import numpy as np
import pandas as pd

DB = "ncdb.db"
OUT = pathlib.Path("model")
UNK = "Unknown or not reported"
OUT.mkdir(exist_ok=True)


def write_dim(name, rows, cols, unknown_key=0, unknown_extra=None):
    """rows: list of tuples (label, group...) in display order. Key = position + 1; the unknown member has key 0."""
    data = [(unknown_key,) + (UNK,) + (unknown_extra if unknown_extra is not None else (UNK,) * (len(cols) - 2))]
    data += [(i + 1,) + tuple(r) for i, r in enumerate(rows)]
    df = pd.DataFrame(data, columns=cols)
    df.to_csv(OUT / f"dim_{name}.csv", index=False)
    return {r[0]: i + 1 for i, r in enumerate(rows)}, df


def key_of(series, mapping):
    return series.map(mapping).fillna(0).astype(int)


con = sqlite3.connect(DB)
c = pd.read_sql("select * from collisions", con)
p = pd.read_sql("select * from persons", con)

# ------------------------------------------------------------------ dimensions
hours = [(("12 am" if h == 0 else f"{h} am" if h < 12 else "12 pm" if h == 12 else f"{h - 12} pm"),
          "Night (10 pm to 6 am)" if h >= 22 or h < 6 else "Morning (6 to 10 am)" if h < 10 else "Midday (10 am to 4 pm)" if h < 16
          else "Evening rush (4 to 8 pm)" if h < 20 else "Late evening (8 to 10 pm)") for h in range(24)]
hour_map = {h: h + 1 for h in range(24)}
pd.DataFrame([(0, "Unknown hour", UNK)] + [(h + 1, a, b) for h, (a, b) in enumerate(hours)], columns=["hour_key", "hour_label", "day_part"]).to_csv(OUT / "dim_hour.csv", index=False)

days = [("Mon", "Weekday"), ("Tue", "Weekday"), ("Wed", "Weekday"), ("Thu", "Weekday"), ("Fri", "Weekday"), ("Sat", "Weekend"), ("Sun", "Weekend")]
day_map, _ = write_dim("weekday", days, ["weekday_key", "weekday", "week_part"])

sev_map, _ = write_dim("severity", [("Fatal",), ("Injury",)], ["severity_key", "severity"])
weather_rows = [("Clear and sunny", "Dry weather"), ("Overcast", "Dry weather"), ("Raining", "Rain"), ("Snowing", "Snow or ice"),
                ("Freezing rain or hail", "Snow or ice"), ("Poor visibility", "Visibility or wind"), ("Strong wind", "Visibility or wind")]
weather_map, _ = write_dim("weather", weather_rows, ["weather_key", "weather", "weather_group"])
surface_rows = [("Dry", "Dry"), ("Wet", "Wet"), ("Snow", "Winter surface"), ("Slush", "Winter surface"), ("Icy", "Winter surface"),
                ("Sand, gravel or dirt", "Other surface"), ("Muddy", "Other surface"), ("Oil", "Other surface"), ("Flooded", "Other surface")]
surface_map, _ = write_dim("surface", surface_rows, ["surface_key", "road_surface", "surface_group"])
align_rows = [("Straight and level", "Straight"), ("Straight with gradient", "Straight"), ("Curved and level", "Curved"), ("Curved with gradient", "Curved"),
              ("Top of a hill", "Hill"), ("Bottom of a hill", "Hill")]
align_map, _ = write_dim("alignment", align_rows, ["alignment_key", "road_alignment", "alignment_group"])
layout_rows = [("Not at an intersection", "Open road"), ("Intersection", "Intersection"), ("Parking lot or driveway entrance", "Driveway or lot"),
               ("Railway crossing", "Special feature"), ("Bridge or overpass", "Special feature"), ("Tunnel or underpass", "Special feature"),
               ("Passing or climbing lane", "Open road"), ("Ramp", "Special feature"), ("Traffic circle", "Intersection"), ("Freeway lane", "Open road")]
layout_map, _ = write_dim("layout", layout_rows, ["layout_key", "road_layout", "layout_group"])
traffic_rows = [("Signals",), ("Stop or yield sign",), ("No control",), ("Other control",)]
traffic_map, _ = write_dim("traffic", traffic_rows, ["traffic_key", "traffic_control"])
type_rows = [("Hit a moving object", "Single vehicle"), ("Hit a stationary object", "Single vehicle"), ("Ran off left shoulder", "Single vehicle"),
             ("Ran off right shoulder", "Single vehicle"), ("Rollover on roadway", "Single vehicle"), ("Other single-vehicle", "Single vehicle"),
             ("Rear-end", "Two vehicles, same direction"), ("Side swipe", "Two vehicles, same direction"), ("Passing or left-turn conflict", "Two vehicles, same direction"),
             ("Passing or right-turn conflict", "Two vehicles, same direction"), ("Other, same direction", "Two vehicles, same direction"),
             ("Head-on", "Two vehicles, different directions"), ("Approaching side swipe", "Two vehicles, different directions"),
             ("Left turn across traffic", "Two vehicles, different directions"), ("Right turn conflict", "Two vehicles, different directions"),
             ("Right angle", "Two vehicles, different directions"), ("Other, different directions", "Two vehicles, different directions"),
             ("Hit a parked vehicle", "Hit a parked vehicle")]
type_map, _ = write_dim("collision_type", type_rows, ["type_key", "collision_type", "collision_group"])
user_map, _ = write_dim("road_user", [("Driver",), ("Passenger",), ("Pedestrian",), ("Bicyclist",), ("Motorcyclist",)], ["user_key", "road_user"])
safety_rows = [("No safety device used", "No protection"), ("No safety device equipped", "No protection"), ("Safety device used", "Protection used"),
               ("Helmet worn", "Protection used"), ("Helmet and reflective clothing", "Protection used"), ("Reflective clothing", "Protection used"),
               ("Other safety device", "Protection used")]
safety_map, _ = write_dim("safety", safety_rows, ["safety_key", "safety_device", "protection"])
age_rows = [("Under 16",), ("16-24",), ("25-34",), ("35-44",), ("45-54",), ("55-64",), ("65 and over",)]
age_map, _ = write_dim("age_band", age_rows, ["age_key", "age_band"])
sex_map, _ = write_dim("sex", [("Female",), ("Male",)], ["sex_key", "sex"])
veh_rows = [("Car or light truck", "Cars and light trucks"), ("Van", "Cars and light trucks"), ("Heavy truck", "Heavy vehicles"), ("Bus", "Heavy vehicles"),
            ("Motorcycle or moped", "Two-wheelers"), ("Bicycle", "Two-wheelers"), ("No vehicle (pedestrian)", "No vehicle"), ("Off-road vehicle", "Other"),
            ("Motorhome", "Other"), ("Farm equipment", "Other"), ("Construction equipment", "Other"), ("Emergency vehicle", "Other"), ("Snowmobile", "Other"), ("Streetcar", "Other")]
veh_map, _ = write_dim("vehicle", veh_rows, ["vehicle_key", "vehicle_type", "vehicle_group"])
psev_map, _ = write_dim("person_severity", [("No injury",), ("Injury",), ("Fatality",)], ["person_severity_key", "person_severity"])

# ------------------------------------------------------------------ facts
fc = pd.DataFrame({
    "collision_id": c["collision_id"],
    "year": c["year"],
    "month_start": pd.to_datetime(dict(year=c["year"], month=c["month"].fillna(1).astype(int), day=1)).dt.strftime("%Y-%m-%d"),
    "weekday_key": key_of(c["weekday"], day_map),
    "hour_key": c["hour"].map(lambda h: 0 if pd.isna(h) else int(h) + 1).astype(int),
    "severity_key": key_of(c["severity"], sev_map),
    "weather_key": key_of(c["weather"], weather_map),
    "surface_key": key_of(c["road_surface"], surface_map),
    "alignment_key": key_of(c["road_alignment"], align_map),
    "layout_key": key_of(c["road_layout"], layout_map),
    "traffic_key": key_of(c["traffic_control"], traffic_map),
    "type_key": key_of(c["configuration"], type_map),
    "vehicles": c["vehicles_seen"].fillna(0).astype(int),
    "people": c["people"],
    "killed": c["killed"],
    "injured": c["injured"],
})
fc.loc[c["month"].isna(), "month_start"] = ""
fc.to_csv(OUT / "fact_collision.csv", index=False)

fp = pd.DataFrame({
    "collision_id": p["collision_id"],
    "age": p["age"],
    "age_key": key_of(p["age_band"], age_map),
    "user_key": key_of(p["user_type"], user_map),
    "safety_key": key_of(p["safety_device"], safety_map),
    "sex_key": key_of(p["sex"], sex_map),
    "vehicle_key": key_of(p["vehicle_type"], veh_map),
    "person_severity_key": key_of(p["person_severity"], psev_map),
})
fp["age"] = fp["age"].astype("Int64")
fp.to_csv(OUT / "fact_person.csv", index=False)

# ------------------------------------------------------------------ checks
print(f"fact_collision {len(fc):,} rows | fact_person {len(fp):,} rows | dimensions: {len(list(OUT.glob('dim_*.csv')))}")
for name, col, df in [("hour", "hour_key", fc), ("weather", "weather_key", fc), ("surface", "surface_key", fc), ("alignment", "alignment_key", fc),
                      ("traffic", "traffic_key", fc), ("collision type", "type_key", fc), ("weekday", "weekday_key", fc),
                      ("road user", "user_key", fp), ("safety device", "safety_key", fp), ("age band", "age_key", fp), ("vehicle", "vehicle_key", fp)]:
    print(f"  unknown {name}: {(df[col] == 0).mean():.1%}")
assert fc["collision_id"].is_unique, "collision_id must be unique in the collision fact"
assert set(fp["collision_id"]) <= set(fc["collision_id"]), "every person must belong to a collision"
assert fc["severity_key"].isin([1, 2]).all()
print("keys: collision_id unique, every person has a collision, every severity is Fatal or Injury")
