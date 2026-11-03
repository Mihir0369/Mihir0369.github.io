"""Build the model-ready tables for Power BI from harms.db (PHAC opioid and stimulant harms), and print the checks.

Run after fetch_harms.py. Outputs (CSV, in ./model/):
  fact_harms_year.csv      source, substance, region, year, number, number_status, crude_rate, rate_status, partial_period
  fact_harms_quarter.csv   source, substance, region, quarter_start, number, number_status
  fact_age_sex.csv         source, substance, region, year, age_group, sex, number, number_status, partial_period

What the source file is: a flattened export of the website's charts (34,890 rows, 39 columns, English and French
copies of every label). Only `Overall numbers` (by year and by quarter) and `Sex and age group` are used here.
The `value` column mixes three things that must not be treated alike:
  a number      -> reported (a real zero is a zero)
  "Suppr."      -> suppressed by PHAC because the count is small (privacy rule); the true value is unknown
  blank (s.o.)  -> not applicable / not reported for that source, region or period
"""
import os
import sqlite3

import pandas as pd

DB = "harms.db"
OUT = "model"

SOURCES = {
    "Hospitalizations": "Hospital stays",
    "Emergency Department (ED) Visits": "Emergency department visits",
    "Emergency Medical Services (EMS)": "EMS responses",
    "Deaths": "Deaths",
}
PROVINCES = ["British Columbia", "Alberta", "Saskatchewan", "Manitoba", "Ontario", "Quebec", "New Brunswick",
             "Nova Scotia", "Prince Edward Island", "Newfoundland and Labrador"]
TERRITORIES = ["Yukon", "Northwest Territories", "Nunavut"]


def status(v: pd.Series) -> pd.Series:
    num = pd.to_numeric(v, errors="coerce")
    s = pd.Series("Reported", index=v.index)
    s[v == "Suppr."] = "Suppressed"
    s[v.isna()] = "Not available"
    return s, num


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    con = sqlite3.connect(DB)
    h = pd.read_sql("select source, specific_measure, substance, region, time_period, xaxislabels, aggregator, "
                    "disaggregator, unit, value from harms", con)
    h["value"] = h["value"].where(h["value"].notna(), None)
    h["source"] = h.source.map(SOURCES)
    assert h.source.notna().all(), "unexpected source"

    # ---- yearly: Overall numbers, 'By year' rows (one row per source, substance, region, year, unit)
    o = h[(h.specific_measure == "Overall numbers") & (h.time_period == "By year")].copy()
    o["year"] = o.xaxislabels.str[:4].astype(int)
    o["partial"] = o.xaxislabels.str.contains("Jan to Mar")
    key = ["source", "substance", "region", "year"]
    assert not o.duplicated(key + ["unit"]).any()
    n = o[o.unit == "Number"].set_index(key)
    r = o[o.unit == "Crude rate"].set_index(key)
    y = n[["value"]].rename(columns={"value": "num_raw"}).join(r[["value"]].rename(columns={"value": "rate_raw"}), how="outer").reset_index()
    y["number_status"], y["number"] = status(y.num_raw)
    y["rate_status"], y["crude_rate"] = status(y.rate_raw)
    # a region that is absent for a source is not "not available", it is simply not a row -> keep only rows that exist
    y["partial_period"] = (y.year == 2026).astype(int)   # 2026 covers January to March only
    assert set(o[o.partial].year) == {2026}
    y = y[key + ["number", "number_status", "crude_rate", "rate_status", "partial_period"]].sort_values(key)
    y.to_csv(f"{OUT}/fact_harms_year.csv", index=False)

    # ---- quarterly: Overall numbers, 'By quarter'
    q = h[(h.specific_measure == "Overall numbers") & (h.time_period == "By quarter")].copy()
    q["year"] = q.xaxislabels.str[:4].astype(int)
    q["qn"] = q.xaxislabels.str[-1].astype(int)
    q["quarter_start"] = pd.to_datetime(dict(year=q.year, month=(q.qn - 1) * 3 + 1, day=1)).dt.strftime("%Y-%m-%d")
    assert not q.duplicated(["source", "substance", "region", "quarter_start"]).any()
    q["number_status"], q["number"] = status(q.value)
    q = q[["source", "substance", "region", "quarter_start", "number", "number_status"]].sort_values(["source", "substance", "region", "quarter_start"])
    q.to_csv(f"{OUT}/fact_harms_quarter.csv", index=False)

    # ---- age and sex: 'Sex and age group', counts, year in time_period
    a = h[(h.specific_measure == "Sex and age group") & (h.unit == "Number")].copy()
    a = a[a.time_period.str[:4].str.isdigit()]
    a["year"] = a.time_period.str[:4].astype(int)
    a = a.rename(columns={"aggregator": "age_group", "disaggregator": "sex"})
    assert not a.duplicated(["source", "substance", "region", "year", "age_group", "sex"]).any()
    a["number_status"], a["number"] = status(a.value)
    a["partial_period"] = (a.year == 2026).astype(int)
    a = a[["source", "substance", "region", "year", "age_group", "sex", "number", "number_status", "partial_period"]].sort_values(
        ["source", "substance", "region", "year", "age_group", "sex"])
    a.to_csv(f"{OUT}/fact_age_sex.csv", index=False)

    # ---- checks
    print("year rows:", len(y), "| quarter rows:", len(q), "| age-sex rows:", len(a))
    print("\nstatus mix (year, number):", y.number_status.value_counts().to_dict())
    print("status mix (age-sex):", a.number_status.value_counts().to_dict())

    can = y[(y.region == "Canada") & (y.year == 2024) & (y.substance == "Opioids")].set_index("source").number
    print("\nCanada 2024 opioid counts:", can.to_dict())
    for src in SOURCES.values():
        t = y[(y.source == src) & (y.year == 2024) & (y.substance == "Opioids") & (y.region != "Canada")]
        s = t.number.sum()
        c = can.get(src)
        miss = sorted(t[t.number_status != "Reported"].region)
        print(f"  {src}: Canada {c} | sum of listed regions {s:.0f} | listed regions {len(t)} | not reported {miss}")

    # coverage: which jurisdictions have a reported 2024 opioid count, by source
    cov = y[(y.year == 2024) & (y.substance == "Opioids") & (y.number_status == "Reported") & (~y.region.isin(["Canada"]))]
    print("\nReported jurisdictions, 2024 opioids:")
    print(cov.groupby("source").region.apply(lambda s: sorted(s)).to_string())

    # quarterly versus yearly, Canada
    qq = q[(q.region == "Canada")].copy()
    qq["year"] = qq.quarter_start.str[:4].astype(int)
    qs = qq.groupby(["source", "substance", "year"]).number.sum().reset_index()
    m = qs.merge(y[y.region == "Canada"][["source", "substance", "year", "number"]], on=["source", "substance", "year"], suffixes=("_q", "_y"))
    m = m[m.year <= 2025]
    m["pct"] = (m.number_q - m.number_y) / m.number_y * 100
    print("\nquarters summed vs published year, Canada, 2016-2025: n =", len(m), "| max gap pct:", round(m.pct.abs().max(), 2),
          "| all gaps <= 0:", bool((m.number_q <= m.number_y).all()))


if __name__ == "__main__":
    main()
