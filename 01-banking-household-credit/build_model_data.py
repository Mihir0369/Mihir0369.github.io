"""Build the model-ready tables for Power BI from banking.db, and print the checks.

Run after fetch_banking_data.py. Outputs (CSV, in ./model/):
  fact_credit_monthly.csv   month, category, balance_millions, yoy_pct
  fact_rates_monthly.csv    month, overnight, prime, mortgage_1y/3y/5y, 12-month changes
  fact_debt_service.csv     quarter_start, debt_measure, ratio_pct   (seasonally adjusted ratios)
  lag_correlation.csv       lag_months, correlation, n         (credit growth vs earlier prime-rate change)
"""
import os
import sqlite3

import pandas as pd

DB = "banking.db"
OUT = "model"
LAG_MAX = 24
RATE_FOR_LAG = "prime_rate"

# Names repeat across the lender hierarchy (for example "Chartered banks" sits under mortgages,
# personal loans and others), so only categories that appear once per month are used.
CATEGORIES = {
    "Total credit liabilities of households": "Total household credit",
    "Mortgage loans": "Mortgage loans",
    "Non-mortgage loans": "Non-mortgage loans",
    "Credit cards": "Credit cards",
    "Lines of credit": "Lines of credit",
    "Home equity lines of credit": "Home equity lines of credit",
    "Personal loans": "Personal loans",
    "Of which: Auto loans": "Auto loans",
}
DEBT_SERVICE = {
    "Debt service ratio": "Total debt service ratio",
    "Mortgage debt service ratio": "Mortgage debt service ratio",
    "Non-mortgage debt service ratio": "Non-mortgage debt service ratio",
}


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    con = sqlite3.connect(DB)

    # ---- credit: seasonally adjusted, Canada, one row per category and month
    c = pd.read_sql("select ref_date, credit_liabilities_of_households as cat, value from credit_liabilities_households "
                    "where geo='Canada' and seasonality='Seasonally adjusted data'", con)
    c = c[c.cat.isin(CATEGORIES)].dropna(subset=["value"]).copy()
    assert c.groupby(["cat", "ref_date"]).size().max() == 1, "category is not unique per month"
    c["category"] = c.cat.map(CATEGORIES)
    c = c.rename(columns={"ref_date": "month", "value": "balance_millions"}).sort_values(["category", "month"])
    c["yoy_pct"] = c.groupby("category").balance_millions.pct_change(12) * 100
    c = c[c.month >= "2010-01"][["month", "category", "balance_millions", "yoy_pct"]]
    c.to_csv(f"{OUT}/fact_credit_monthly.csv", index=False)

    # ---- rates: monthly (last weekly or daily observation), with 12-month changes
    r = pd.read_sql("select month, overnight_target as overnight, prime_rate as prime, mortgage_1y, mortgage_3y, mortgage_5y "
                    "from rates_monthly order by month", con)
    for col in ["overnight", "prime", "mortgage_5y"]:
        r[f"{col}_chg_12m"] = r[col] - r[col].shift(12)
    r.to_csv(f"{OUT}/fact_rates_monthly.csv", index=False)

    # ---- debt service ratios: quarterly, seasonally adjusted
    d = pd.read_sql("select ref_date, estimates, value from household_debt_service where geo='Canada' and uom='Ratio' "
                    "and seasonal_adjustment='Seasonally adjusted at annual rates'", con)
    d["estimates"] = d.estimates.str.strip()
    d = d[d.estimates.isin(DEBT_SERVICE)].copy()
    d["debt_measure"] = d.estimates.map(DEBT_SERVICE)
    d["quarter_start"] = d.ref_date + "-01"
    d = d.rename(columns={"value": "ratio_pct"})[["quarter_start", "debt_measure", "ratio_pct"]]
    d = d[d.quarter_start >= "2010-01-01"].sort_values(["debt_measure", "quarter_start"])
    d.to_csv(f"{OUT}/fact_debt_service.csv", index=False)

    # ---- lag correlation: credit growth now versus the 12-month change in the prime rate k months earlier
    tot = c[c.category == "Total household credit"].set_index("month").yoy_pct
    chg = r.set_index("month")[f"{RATE_FOR_LAG.replace('prime_rate', 'prime')}_chg_12m"]
    rows = []
    for lag in range(0, LAG_MAX + 1):
        m = pd.concat([tot, chg.shift(lag)], axis=1, keys=["credit", "rate"]).dropna()
        rows.append({"lag_months": lag, "correlation": round(m.corr().iloc[0, 1], 3), "n": len(m)})
    lag = pd.DataFrame(rows)
    lag.to_csv(f"{OUT}/lag_correlation.csv", index=False)

    # ---- checks
    print("credit rows:", len(c), "| categories:", c.category.nunique(), "| months", c.month.min(), "to", c.month.max())
    print("rates rows:", len(r), "| nulls:", int(r.isna().sum()[["overnight", "prime", "mortgage_5y"]].sum()))
    print("debt service rows:", len(d), "| quarters", d.quarter_start.min(), "to", d.quarter_start.max())
    best = lag.loc[lag.correlation.abs().idxmax()]
    print("lag correlation: strongest at", int(best.lag_months), "months, r =", best.correlation, "n =", int(best.n))
    print(lag.to_string(index=False))
    latest = c[c.month == c.month.max()].set_index("category")
    print("\nlatest month", c.month.max())
    print(latest[["balance_millions", "yoy_pct"]].round(1))


if __name__ == "__main__":
    main()
