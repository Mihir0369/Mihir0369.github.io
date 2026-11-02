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
