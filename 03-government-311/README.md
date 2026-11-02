# Project 3: Government, Toronto 311 Demand and Unresolved Requests

**Role targeted:** Data / Reporting Analyst in municipal, provincial or federal government
**Data:** City of Toronto [311 Service Requests - Customer Initiated](https://open.toronto.ca/), 2023 to 2025 (1,351,594 requests). Open Government Licence - Toronto. Refreshed monthly.

## Business question
Where does the city leave requests unresolved, and what is behind the growth in 311 demand?

## Headline result
49.4% of 2025 parks, forestry and environment requests are still open, against 1.4% to 6.6% in every other division. Full findings, charts and limits are in [projects.js](../site/projects.js) and on the case-study page.

## What the data actually contains (checked, not assumed)
| Field | Notes |
|---|---|
| Creation Date | Timestamp to the second |
| Status | Completed, Closed, Cancelled, In Progress, New, Unknown |
| First 3 Chars of Postal Code, Intersection Street 1/2 | Location is either a postal area or an intersection |
| Ward | Name and number, e.g. `Beaches-East York (19)` |
| Service Request Type, Division, Section | |

Three things shaped the analysis:
1. **There is no close date.** Time to close cannot be measured, so the project reports request status instead.
2. **About 8% of rows are malformed.** An unquoted comma splits "Parks, Forestry & Recreation" and "Environment, Climate & Forestry" into two fields. `load_311.py` repairs them and reports the counts.
3. **Request types were renamed in January 2025.** 255 type names appear only in 2025, covering 58.2% of that year's requests, so type-level trends cannot cross the 2024/2025 boundary. The Parks/Forestry division was also renamed and split in 2025; the loader groups it as `Parks, Forestry & Environment`.

## Reproduce it
```bash
python load_311.py --years 2023 2024 2025   # downloads, repairs, loads 311.db, writes requests_monthly_agg.csv
python run_sql.py                           # runs sql/analysis.sql, prints results, saves results/*.csv
```
Reconciliation printed by the loader: rows read per file match each file's line count minus the header (414,282 / 437,043 / 500,269), and the monthly aggregate preserves the total request count.

## Power BI build
The report is a Power BI project (`powerbi/toronto-311.pbip`, PBIR + TMDL, so every page and measure is readable in Git). Open it in Power BI Desktop with the project-file preview feature on. The CSV path is the `CsvPath` parameter in Power Query: point it at your local `requests_monthly_agg.csv` (not in Git; create it with `load_311.py`).

**Model (star schema).** One fact table, `requests`, loaded from the 295,239-row monthly summary (1,351,594 requests). Four dimensions: `Date` (marked as the date table), `Dim_Division` (7), `Dim_ServiceType` (829, with a *Taxonomy Era* flag: in both periods, 2023-24 only, 2025 only) and `Dim_Status` (4, in a fixed order). Do not import `stg_requests.csv` (287 MB); it is for SQL and spot checks.

**Measures (DAX).** Requests, Resolved, Cancelled, Open and their shares; year-over-year change; "vs rest" gap for parks and forestry; and text measures that write the findings on each page from the current filters (headline, busiest month, largest type, and so on).

**Pages**
1. **Start here:** the question, three findings calculated from the latest year in the data, how to use the report, and the main limit.
2. **Overview:** KPI cards, key findings, monthly requests by year.
3. **Outcomes:** open share by division, outcome mix, scorecard, a hover tooltip, and drill-through to **Division detail** (request types behind one division).
4. **Request types:** top types with Year, Taxonomy era and Division filters, and the January 2025 renaming warning.

Every page has navigation buttons, a synced Year filter and a Reset filters button. A figure that is not comparable across years is shown as a count or a same-year gap, not a year-over-year change. Reconciled against the SQL: yearly totals, open share by division, and the 58.2% renamed-type share.

## Interview talking points
- You found that the dataset cannot answer "how long do requests take" and said so, instead of forcing it.
- You found and repaired a malformed-row problem and reconciled counts afterwards.
- You caught a taxonomy change that would have produced misleading type-level growth numbers.
- You separated what the data shows (49% still open) from what it cannot show (backlog vs stale status).
