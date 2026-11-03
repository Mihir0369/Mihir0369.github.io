# Project 1: Banking, Household Credit and Lending-Rate Monitor

**Role targeted:** Reporting / BI Analyst in a bank's retail lending, risk or finance team
**Data (all Canadian):**
- [Bank of Canada Valet API](https://www.bankofcanada.ca/valet/): overnight target rate `V39079`, prime rate `V80691311`, conventional mortgage rates 1/3/5-year `V80691333`, `V80691334`, `V80691335`
- Statistics Canada [36-10-0639-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3610063901) credit liabilities of households (monthly)
- Statistics Canada [38-10-0238-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3810023801) household sector credit market summary (quarterly)
- Statistics Canada [11-10-0065-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1110006501) household debt service indicators (quarterly)

This is market-level data, not customer data. I found no Statistics Canada table with delinquency or arrears in my search, so this project does not report delinquency.

## Business problem
The head of retail lending wants one monthly view of how household borrowing, debt service burden and borrowing rates are moving, so the team can anticipate demand and repayment pressure.

## Deliverables
- SQLite database with rates, credit and debt-service tables
- Power BI report: Rates overview, Household credit by category, Debt service pressure
- 1-page methodology note and measure dictionary

## Steps
1. `python fetch_banking_data.py` pulls all sources into `banking.db` and CSVs, and prints each table's dimensions.
2. Pick the categories you will chart (the script lists the distinct values), then edit the filters in `sql/analysis.sql`.
3. Import into Power BI, add a date table, and relate everything on month.
4. Build the measures below and the three pages.

## Core DAX measures (adjust to your table names)
```DAX
Credit Balance = SUM(credit[value])
Credit MoM % = DIVIDE([Credit Balance] - CALCULATE([Credit Balance], PREVIOUSMONTH('Date'[Date])), CALCULATE([Credit Balance], PREVIOUSMONTH('Date'[Date])))
Credit YoY % = DIVIDE([Credit Balance] - CALCULATE([Credit Balance], SAMEPERIODLASTYEAR('Date'[Date])), CALCULATE([Credit Balance], SAMEPERIODLASTYEAR('Date'[Date])))
Prime Rate = AVERAGE(rates[prime_rate])
5Y Mortgage Rate = AVERAGE(rates[mortgage_5y])
Mortgage Spread to Prime = [5Y Mortgage Rate] - [Prime Rate]
```

## Report ideas
- Policy rate, prime and mortgage rates on one line chart with annotations at rate decisions
- Household credit by category (mortgage, non-mortgage, consumer credit) with YoY growth
- Debt service ratio trend next to the prime rate
- Scatter: rate change vs credit growth, with a lag slicer (0 to 12 months)

## Stretch
Add a simple lagged correlation between rate changes and credit growth. State clearly that this is correlation, not causation.

---

## What was built (results)

**Run order**
1. `python fetch_banking_data.py` downloads the rates and the three Statistics Canada tables into `banking.db` and raw CSVs (not committed).
2. `python build_model_data.py` writes the model-ready tables to `model/` and prints the checks.
3. `python build_powerbi.py` generates the Power BI project in `powerbi/` (open `household-credit.pbip`). Re-running it overwrites that folder, so edit the script, not the output.

**Report pages:** Start here, Rates, Credit, Rate lag. A Reset filters button clears the slicers; the Year filter carries across Rates and Credit.

**Model:** `fact_credit`, `fact_rates`, `fact_debt`, `lag_correlation`, plus `Date`, `Dim_Category`, `Dim_DebtMeasure` and `LagSteps` (the lag selector), and a measures table with 51 DAX measures.

**Results (checked against the model tables)**
- Household credit: $1.5 trillion (Jan 2010) to $3.3 trillion (Aug 2026). Year-over-year growth peaked at 8.7% (May 2022), fell to 3.5% by Oct 2023 and is 4.1% now.
- Prime rate: 2.45% (Feb 2022) to 7.20% (Jul 2023, held 11 months), 4.45% now.
- Credit growth versus the prime-rate change over the previous 12 months is most negative at an 18-month lag: correlation -0.52 over 170 months (-0.17 at 6 months, -0.43 at 12). Using the rate level instead gives a best lag of about 8 months, so the delay depends on the method.
- Debt service ratio: 12.6% (Apr 2020 quarter), 15.2% (Jan 2023 quarter), 14.5% now.

**Data traps handled**
- Category names repeat across the lender hierarchy (for example "Chartered banks" appears under several parents), so only the 8 categories that appear once per month are used.
- Auto loans start in 2016; this is the only gap.
- Credit cards (2011 to 2012) and personal loans (2013 to 2014) show year-over-year spikes above 20% that look like reclassifications, so they are used as latest-month figures only.
- Credit data ends Aug 2026, rates Oct 2026 and debt service Apr 2026.
