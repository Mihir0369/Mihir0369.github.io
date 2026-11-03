# Project 5: Healthcare, Opioid and Stimulant Harms by Province

**Role targeted:** BI / Reporting Analyst at a hospital, health authority, public health unit or Ontario Health partner
**Data:** Public Health Agency of Canada, [Opioid- and Stimulant-related Harms in Canada](https://health-infobase.canada.ca/substance-related-harms/opioids-stimulants/) (Open Government Licence - Canada). Open CSV export: `https://health-infobase.canada.ca/api/opioids/linked/export/opioids/csv`, also a ZIP with data and user guide. Published as aggregated counts and rates by province or territory and period, covering hospitalizations, emergency medical service responses, and deaths. Updated September 2026 in the catalogue record.

I chose this because the Ontario hospital datasets I searched in the data.ontario.ca catalogue have no downloadable files (empty records), and Ontario Health's emergency department reporting has no bulk download. I also found CIHI's wait-times tables (XLSX, copyright CIHI; read its terms of use before reusing).

I confirmed the catalogue record, licence and file links. I did not open the CSV, so the loader prints its real columns and does not assume them. Read the user guide in the ZIP before you define any measure.

## Business problem
A public health team wants to see how harms are changing across provinces and over time, which substances and age groups drive hospitalizations, and how hospital burden compares with EMS and deaths, to support planning.

## Deliverables
- Clean SQLite table with documented cleaning rules
- Power BI report: Trend overview, Province comparison, Hospital vs EMS vs deaths
- Methodology note on suppression, rate definitions and comparability across provinces

## Steps
1. `python fetch_harms.py` downloads the CSV, saves it as `harms.csv`, loads `harms.db`, and prints columns, row counts, and the distinct values of every categorical column.
2. Using that printout and the user guide, set the column names in `sql/analysis.sql` (the file uses placeholders in angle brackets).
3. Import into Power BI. Build a date table if the period is monthly or quarterly.

## Example DAX measures (rename to the real columns)
```DAX
Events = SUM(harms[value])
Events YoY % = DIVIDE([Events] - CALCULATE([Events], SAMEPERIODLASTYEAR('Date'[Date])), CALCULATE([Events], SAMEPERIODLASTYEAR('Date'[Date])))
Share of National = DIVIDE([Events], CALCULATE([Events], ALL(harms[province])))
```
Use published rates for comparing provinces. Counts alone mislead because populations differ.

## Report ideas
- Quarterly trend of hospitalizations by substance
- Province ranking by rate per 100,000 with a small-count warning
- Age and sex breakdown where available
- Side-by-side hospitalizations, EMS responses and deaths

## Governance notes (good to show)
- Small counts may be suppressed in the source. Show suppression as "suppressed", never as zero.
- Do not rank provinces without noting differences in reporting methods.
- Use neutral, non-stigmatizing language in titles and labels.

## What was built (results)
- `fetch_harms.py` downloads the PHAC export (34,890 rows, 39 columns) into `harms.db`; `build_model_data.py` turns it into three model tables in `model/` (yearly, quarterly, age and sex) and prints the checks.
- `sql/analysis.sql` holds the data-quality queries: keys are unique, Canada equals the sum of the places that report, and quarters add up to slightly less than the published year.
- `build_powerbi.py` generates the Power BI project in `powerbi/` (TMDL model and PBIR report, six pages). `opioid-harms.pdf` is the export.

Data traps found: `value` mixes numbers, "Suppr." (suppressed) and blanks (not available); hospital stays leave out Quebec and emergency department visits cover 7 of 13 provinces and territories in the Canada total; quarters do not add up to the published year; 2026 covers January to March only; some 2025 provincial values look provisional, so provinces are compared on 2024.
