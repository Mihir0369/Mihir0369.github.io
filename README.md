# Data & BI Portfolio: Canadian public-data case studies

**Live site:** https://mihir0369.github.io/

Four finished case studies and one in development, all built on Canadian public data. Each one follows the same path: the question, data preparation, SQL checks, a Power BI star-schema model with documented DAX, findings, and recommendations. Every project says what its data cannot tell you.

| # | Sector | Case study | Status | Power BI report |
|---|--------|-----------|--------|-----------------|
| 1 | Banking | [Household credit and lending rates](01-banking-household-credit) | Finished | 5 pages, 60 measures |
| 2 | Transportation safety | [Collision severity and risk factors](02-insurance-collision-risk) | Finished | 7 pages, 102 measures |
| 3 | Government | [Toronto 311 service requests](03-government-311) | Finished | 5 pages (plus a drill-through page), 61 measures |
| 4 | IT consulting | [Federal contracts on a Fabric lakehouse](04-consulting-fabric-procurement) | In development | Report not built yet |
| 5 | Healthcare | [Opioid and stimulant harms](05-healthcare-opioid-harms) | Finished | 6 pages, 95 measures |

## Headline findings

- **Household credit:** across lags of 0 to 24 months, the strongest negative association between rate changes and credit growth appears at 18 months (correlation -0.52). It is observational, not causal. Total household credit is $3.30 trillion (August 2026), 2.22 times its January 2010 level. Market-level data only.
- **Collision risk:** 185,772 fatal and injury collisions (2019 and 2020). Among recorded fatal and injury collisions, the fatal share was 3.41% overnight (10 pm to 6 am) against 1.52% by day (2.24x). The denominator is recorded collisions with no traffic volumes, so it is not a per-trip risk. The fatal share rose in 2020 because injury collisions fell almost 25% while fatal ones barely moved.
- **Toronto 311:** 500,269 requests in 2025, up 14.47%. 49.45% of parks, forestry and environment requests are recorded as open, against 1.37% to 6.60% in every other division. 58.17% of 2025 requests sit under request types renamed or introduced in January 2025, so growth by type is not comparable across the break.
- **Opioid and stimulant harms:** opioid deaths declined faster than EMS responses in the reported data: from the 2023 peak to 2025, deaths fell 29.43% (8,083 to 5,704) and EMS responses 7.84% (42,756 to 39,406). Annual Canada totals as reported; the places that report differ by source.

Exact figures, method and limits are on each case page.

## What each dataset can and cannot support

- **Banking:** market-level data only. No customer or account data, so no default modelling.
- **Transportation safety:** police-reported fatal and injury collisions only. Not claims data, no property-damage-only collisions, so no loss ratios or pricing. Fatal share is not exposure-based road risk.
- **Government (311):** there is no close date, so "open" means open at the data snapshot, not a confirmed backlog, and time to close cannot be measured.
- **Healthcare:** published, aggregated counts by province and period. No patient-level data, and some values are suppressed.
- **Procurement:** disclosed federal contracts over $10,000, published up to several months after award.

## How every Power BI report is laid out

All finished reports share one structure so they read the same way:

1. A banner with the page title and subtitle.
2. A filter and headline row, with a Reset filters button.
3. Four icon number cards.
4. The chart and table panels, with titles that state the conclusion.
5. Three finding boxes, each with a key number.
6. A one-line footnote.
7. A source footer, and a final **Data quality** page.

Percentages and ratios are shown to two decimals and counts as whole numbers. The reports contain no tooltips, page-navigation buttons or scroll bars.

## Folder layout

This folder is the Git repository root.

- `01-...` to `05-...`: one folder per project, with its own README, loader script, SQL, model data, a `powerbi/` project (PBIP: TMDL semantic model plus PBIR report), the exported PDF and `build_powerbi.py` (or `build_report.py` for project 3), which regenerates the report pages.
- `site/`: the portfolio website (plain HTML, CSS and JavaScript, deployed to GitHub Pages by GitHub Actions).
- Raw data and large generated files are excluded by `.gitignore` and re-created by each project's loader.

## Open a report

1. Download the project's `.zip` from its case page, or use the `powerbi/` folder here.
2. Open the `.pbip` file in Power BI Desktop (free). Turn on the Developer mode / PBIP preview if asked.
3. If the model reads a CSV, change the path in `expressions.tmdl` to where the file now is, then click Refresh.

## The website

One scrolling homepage (hero, impact, projects, about, skills, experience, contact) and one crawlable page per finished project (`toronto-311.html`, `household-credit.html`, `collision-risk.html`, `substance-harms.html`), each with its own title, description, canonical URL and social preview.

- `projects.js` holds the profile and case-study content. `build_evidence.py` reads the real project files and writes `evidence.js` (SQL excerpts, data-coverage blocks, DAX notes) and a star-schema diagram per project from each `relationships.tmdl`.
- `build_home.py` writes `index.html` and the four project pages as plain HTML, so search engines and text-only readers see the content without JavaScript. `case.js` then adds the charts, report viewer and DAX panel in the browser. `case.html?id=...` redirects to the project page.
- `check_site.py` checks links, assets, anchors, meta tags, headings, image alt text, project pages, sitemap and downloads (`--external` also tests outside links). GitHub Actions rebuilds the site and runs it before every deploy.
- Rebuild after editing content: `python build_evidence.py && python build_home.py && python check_site.py` from `site/` (needs Node and Pillow).
- Report pages open in a viewer with previous and next arrows. Screenshots are also stored as WebP for fast loading; the original PNGs stay for detailed review.

Run it locally with `python -m http.server` from `site/`.

## Setup for the loaders

```bash
python -m venv .venv
.venv\Scripts\activate
pip install pandas numpy requests openpyxl
```

Each project folder has a README (the write-up), `sql/` and a loader script. Run the loader, check the printed columns and checks, then open the database in DB Browser for SQLite or import the CSV outputs into Power BI Desktop. Where a real column differs from an assumption, fix the mapping near the top of the script.

## Data sources and licences

| # | Source | Licence |
|---|--------|---------|
| 1 | [Bank of Canada Valet API](https://www.bankofcanada.ca/valet/) and Statistics Canada tables 36-10-0639, 38-10-0238, 11-10-0065 | Bank of Canada terms; Statistics Canada Open Licence |
| 2 | [Transport Canada National Collision Database](https://open.canada.ca/data/en/dataset/1eb9eba7-71d1-4b30-9fb1-30cbdab7e63a) | Open Government Licence - Canada |
| 3 | [Open Data Toronto: 311 Service Requests](https://open.toronto.ca/dataset/311-service-requests-customer-initiated/) | Open Government Licence - Toronto |
| 4 | [Proactive Publication - Contracts](https://open.canada.ca/data/dataset/d8f85d91-7dec-4fd1-8055-483b77225d8b) (about 655 MB CSV) | Open Government Licence - Canada |
| 5 | [PHAC Health Infobase, Opioid- and Stimulant-related Harms in Canada](https://open.canada.ca/data/en/dataset/1092497d-6c72-4e66-930b-9d6337e64af5) | Open Government Licence - Canada |

No employer or client data is used anywhere in this repository.

## Rules for every project

- State the source, licence, refresh date and limits at the top of the README and on the report.
- Show a KPI table, three to five findings and three recommendations in plain business language, without claiming causes the data cannot support.
- Include a data-quality section: row counts, null checks and reconciliation to source totals.
- Document every DAX measure and its business definition.
