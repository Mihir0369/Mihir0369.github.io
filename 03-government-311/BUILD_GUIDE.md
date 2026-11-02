# Build Guide: Toronto 311 Power BI Report (about 3 to 4 hours)

You will build a 3-page Power BI report from `requests_monthly_agg.csv`, check it against numbers already verified in SQL, export screenshots, and put the project on GitHub. Do the steps in order and tick the check at the end of each step before moving on.

**Numbers to check your report against** (from `results/*.csv`):

| What | Expected |
|---|---|
| Total requests, 2023 to 2025 | 1,351,594 |
| Requests by year | 2023: 414,282 / 2024: 437,043 / 2025: 500,269 |
| Requests YoY | 2024: +5.5% / 2025: +14.5% |
| 2025 Resolved % / Cancelled % / Open % | 80.5% / 10.3% / 7.8% |
| 2025 Open % by division | Parks, Forestry & Environment 49.4%, Transportation 6.6%, Toronto Water 5.7%, Municipal Licensing & Standards 5.6%, Solid Waste 1.7%, 311 1.4% |

---

## Step 0. Prepare (10 min)
1. Install **Power BI Desktop** from the Microsoft Store if you do not have it.
2. Turn on project files so the report can live in Git: **File > Options and settings > Options > Preview features > tick "Power BI Project (.pbip) save option"**, then restart Power BI Desktop.
3. In this folder, create `powerbi/` and `screenshots/` (inside `03-government-311`).
4. Confirm `requests_monthly_agg.csv` exists in this folder (about 32 MB, 295,239 rows). If it is missing, run `python load_311.py --years 2023 2024 2025`.

## Step 1. Create and save the project (5 min)
1. Open Power BI Desktop, a blank report.
2. **File > Save as**, choose type **Power BI Project (*.pbip)**, save as `powerbi/toronto-311.pbip`.

## Step 2. Load and clean the data in Power Query (20 min)
1. **Home > Get data > Text/CSV**, pick `requests_monthly_agg.csv`, then **Transform Data**.
2. Rename the query to `requests` (right-click it in the Queries pane).
3. Set column types (click the type icon in each header):
   - `month`: Text
   - `year`, `requests`: Whole number
   - `division_group`, `service_request_type`, `ward_name`, `status_group`, `location_type`: Text
4. Add the date key: **Add Column > Custom Column**, name `MonthStart`, formula:
   ```
   Date.FromText([month] & "-01")
   ```
   Set its type to **Date**.
5. Replace nulls so nothing disappears from visuals: select `ward_name`, **Transform > Replace Values**: replace `null` with `Unknown ward`. Repeat for `division_group` with `Unknown division` if it has nulls.
6. **Home > Close & Apply**.

Check: **Data view** shows 295,239 rows. If not, one of the steps dropped rows; compare with the CSV row count.

## Step 3. Date table and relationship (15 min)
1. **Table view > New table**, paste:
   ```DAX
   Date =
   ADDCOLUMNS (
       CALENDAR ( DATE ( 2023, 1, 1 ), DATE ( 2025, 12, 31 ) ),
       "Year", YEAR ( [Date] ),
       "Month Number", MONTH ( [Date] ),
       "Month", FORMAT ( [Date], "mmm" ),
       "Year Month", FORMAT ( [Date], "yyyy-mm" )
   )
   ```
2. Select the new table, **Table tools > Mark as date table**, choose the `Date` column.
3. Sort `Month` by `Month Number`: select the `Month` column, **Column tools > Sort by column > Month Number**.
4. **Model view**: drag `Date[Date]` onto `requests[MonthStart]`. It must be one-to-many, single direction, Date side = 1.
5. Hide `MonthStart`, `month` and `year` from report view (right-click > Hide). Use the Date table's columns in visuals.

Check: in the Report view, a Card with `requests[requests]` summed shows **1,351,594**.

## Step 4. Measures (20 min)
**Home > New table > Enter data**: create an empty table named `_Measures`. Then add each measure below with **right-click `_Measures` > New measure**. Set the format in **Measure tools** after each.

```DAX
Requests = SUM ( requests[requests] )
```
Format: whole number, thousands separator.

```DAX
Resolved = CALCULATE ( [Requests], requests[status_group] = "Resolved" )
Cancelled = CALCULATE ( [Requests], requests[status_group] = "Cancelled" )
Open = CALCULATE ( [Requests], requests[status_group] = "Open" )
Resolved % = DIVIDE ( [Resolved], [Requests] )
Cancelled % = DIVIDE ( [Cancelled], [Requests] )
Open % = DIVIDE ( [Open], [Requests] )
```
Format the three percentages: percentage, 1 decimal.

```DAX
Requests PY = CALCULATE ( [Requests], SAMEPERIODLASTYEAR ( 'Date'[Date] ) )
Requests YoY % = DIVIDE ( [Requests] - [Requests PY], [Requests PY] )
```
`YoY %` is blank for 2023, which is correct (no 2022 data). Do not fill it with zero.

```DAX
Selected Year Label =
IF ( HASONEVALUE ( 'Date'[Year] ), SELECTEDVALUE ( 'Date'[Year] ), "2023 to 2025" )
```

Check: put `Date[Year]` and `[Requests]` in a table. You should see 414,282 / 437,043 / 500,269. Add `[Requests YoY %]`: blank, 5.5%, 14.5%. Add `[Open %]` and compare with the expected table above.

## Step 5. Page 1: Overview (40 min)
Rename the page **Overview**. Set **View > Page view > Fit to page**. Canvas 16:9.

1. **Title text box** (top): "Toronto 311: demand is rising, and some requests stay open". Smaller subtitle text box: "Customer-initiated requests, 2023 to 2025. Source: City of Toronto Open Data (Open Government Licence - Toronto)."
2. **Slicer** (top right): `Date[Year]`, style **Tile/Buttons**. Allow multi-select.
3. **Four Card visuals** in a row: `[Requests]`, `[Resolved %]`, `[Open %]`, `[Requests YoY %]`. Turn on the category label under each value.
4. **Line chart**: X axis `Date[Month]`, Y axis `[Requests]`, Legend `Date[Year]`. This overlays the three years. Title: "Requests per month by year".
5. **Text box note** under the chart: "Request types were renamed in January 2025, so the February 2025 jump partly reflects new snow-related request types. See Request types page."
6. Alt text on every visual: **Format > General > Alt text**.

Check: with the year slicer on 2025, cards show 500,269 / 80.5% / 7.8% / +14.5%.

## Step 6. Page 2: Outcomes by division (40 min)
New page **Outcomes by division**.

1. **Title:** "Half of parks and forestry requests are still open" (write the finding, not the topic).
2. **Slicer:** `Date[Year]` (tile style), default select 2025 by clicking it before saving.
3. **Clustered bar chart:** Y `requests[division_group]`, X `[Open %]`. Sort by `Open %` descending. Add data labels. Colour the Parks, Forestry & Environment bar differently (**Format > Visual > Bars > Colors > Show all**).
4. **100% stacked bar:** Y `requests[division_group]`, X `[Requests]`, Legend `requests[status_group]`. Title: "Outcome mix by division". Order legend as Resolved, Open, Cancelled, Unknown with consistent colours (green, amber, grey, light grey).
5. **Table** (or matrix): rows `division_group`; values `[Requests]`, `[Resolved %]`, `[Cancelled %]`, `[Open %]`. Add conditional formatting on `Open %` (**data bars**).
6. **Text box note:** "Open means status New or In Progress at the time of the data snapshot. It cannot tell a genuine backlog from a status that was never updated. The data has no close date."

Check: with 2025 selected, Parks, Forestry & Environment shows 49.4% and Solid Waste 1.7%. Select 2023 only: Parks, Forestry & Environment should still show about 44.7% (requests from 2023 still open).

## Step 7. Page 3: Request types (30 min)
New page **Request types**.

1. **Title:** "What people ask 311 for, and a naming change to watch".
2. **Slicers:** `Date[Year]` (tile), and `requests[division_group]` (dropdown).
3. **Bar chart:** Y `requests[service_request_type]`, X `[Requests]`. In the **Filters pane**, set the visual filter **Top N: Top 15 by `[Requests]`**. Add data labels.
4. **Table:** `service_request_type`, `[Requests]`, `[Cancelled %]`, `[Open %]`. Sort by Requests. Add a visual filter `[Requests]` is greater than 1000 so tiny types do not show noise.
5. **Warning text box** (amber background): "In January 2025, 255 request type names changed or were introduced; they cover 58.2% of 2025 requests. Compare type counts only within 2023 to 2024, or within 2025."

Check: with 2025 selected the top types are Residential Bin Lid Damaged (24,448), Property Standards and Maintenance Violations (17,079), Pick up Dead Wildlife (15,513). Dead-wildlife Cancelled % is about 38.8%.

## Step 8. Polish (20 min)
- **View > Themes**: pick one theme and keep it. Use two colours at most plus grey; use the same colour for the same meaning on every page.
- Font sizes: titles 18 to 20, labels at least 11.
- Align and distribute visuals (**Format > Align**). Keep margins even.
- **Page navigation**: add three buttons (**Insert > Buttons > Navigator > Page navigator**).
- Add a footer text box on each page: "Source: City of Toronto Open Data. Data period 2023 to 2025. Not an official City report."
- Test the **Tab order** (View > Selection pane order) for accessibility.

## Step 9. Verify before you share (10 min)
Re-run the checks in the table at the top, on the live report, with a fresh eye. If a number differs from the table, fix the report, not the table, unless you can show the SQL result is wrong.

## Step 10. Capture and export (10 min)
1. For each page, screenshot (Win + Shift + S) into `screenshots/` as `01-overview.png`, `02-outcomes.png`, `03-types.png`.
2. **File > Export > Export to PDF** into `powerbi/toronto-311.pdf`.
3. Do not commit raw data or the model cache (see `.gitignore` in the parent folder). Keep `requests_monthly_agg.csv` on your computer; it is not in Git.

## Step 11. Put it on GitHub (15 min)
From the parent folder (`Portfolio Projects`) in a terminal:
```bash
git init
git add .gitignore README.md 03-government-311 site
git status
git commit -m "Add Toronto 311 case study"
```
Create an empty repo on GitHub, then:
```bash
git branch -M main
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```
Run `git status` before the commit and confirm no `.csv`, `.db` or `.zip` data file is staged (the `.gitignore` excludes them; anyone can re-create them with `load_311.py`). The `results/*.csv` summary files are small and fine to commit.

## Step 12. Add it to your portfolio site (10 min)
- Copy the three screenshots to `site/images/`.
- Ask me to add an image gallery to the case page, or open `site/projects.js` and replace the `repo` line with your GitHub URL.
- Write a 2-sentence LinkedIn post: the question, the headline (49% of forestry requests still open), and the limit (no close date).

## If you get stuck
| Problem | Fix |
|---|---|
| Date relationship will not create | `MonthStart` must have type Date, and the Date table's `Date` column must have no time part |
| `Requests YoY %` shows blank for every year | The Date table is not marked as a date table, or the relationship is inactive |
| Months sort alphabetically | Sort `Month` by `Month Number` (Step 3.3) |
| Totals are off | You are summing `requests[requests]`; make sure `[Requests]` is not set to Count |
| Report is slow | Confirm you imported `requests_monthly_agg.csv`, not the 287 MB staging file |

## What to say in an interview (60 seconds)
"I analysed 1.35 million Toronto 311 requests. The data has no close date, so instead of forcing a time-to-close metric I measured outcomes. About half of parks and forestry requests are still open, even requests from 2023, against 1 to 7 percent elsewhere. I also found that request types were renamed in January 2025, so I limited type comparisons accordingly. I cannot say whether the open requests are a backlog or stale statuses; I recommended the city add a closed date."
