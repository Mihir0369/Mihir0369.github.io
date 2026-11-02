# Data & BI Portfolio: 5 Canadian Industry Case Studies

Every project uses Canadian public data. Each follows the same path: business problem, data prep, SQL, Power BI model and DAX, insights, recommendations.

| # | Industry | Case study | Canadian source | Licence |
|---|----------|-----------|-----------------|---------|
| 1 | Banking | Household credit and lending-rate monitor | [Bank of Canada Valet API](https://www.bankofcanada.ca/valet/) + Statistics Canada tables 36-10-0639, 38-10-0238, 11-10-0065 | Bank of Canada terms; Statistics Canada Open Licence |
| 2 | Insurance | Collision severity and risk-factor analysis for an auto insurer | [Transport Canada National Collision Database](https://open.canada.ca/data/en/dataset/1eb9eba7-71d1-4b30-9fb1-30cbdab7e63a) | Open Government Licence - Canada |
| 3 | Government | Toronto 311 service performance dashboard | [Open Data Toronto: 311 Service Requests](https://open.toronto.ca/) (CKAN package `311-service-requests-customer-initiated`) | Open Government Licence - Toronto |
| 4 | IT consulting | Federal procurement analytics on a Fabric lakehouse | [Proactive Publication - Contracts](https://open.canada.ca/data/dataset/d8f85d91-7dec-4fd1-8055-483b77225d8b) (about 655 MB CSV) | Open Government Licence - Canada |
| 5 | Healthcare | Opioid and stimulant harms by province (hospital, EMS, deaths) | [PHAC Health Infobase, Opioid- and Stimulant-related Harms in Canada](https://open.canada.ca/data/en/dataset/1092497d-6c72-4e66-930b-9d6337e64af5) | Open Government Licence - Canada |

I checked that these sources exist and are open (catalogue records, licences, file sizes). I did not download or inspect the data files, so each loader prints the columns it finds and checks them before running. Where a project's real columns differ from my assumptions, fix the mapping near the top of the script.

## What each dataset can and cannot support
- **Banking:** market-level data only. It has no customer or account data, so do not claim default modelling.
- **Insurance:** police-reported **fatal and injury** collisions only. It is not claims data and has no property-damage-only collisions, so do not claim loss ratios or pricing.
- **Healthcare:** published, aggregated counts by province and period. No patient-level data.
- **Procurement:** disclosed federal contracts over $10,000, published up to several months after award.

## Folder layout
This folder is the Git repository root. Each project has its own folder (`01-...` to `05-...`) with a README, loader script and SQL. `site/` is the portfolio website. Project 3 also has a `BUILD_GUIDE.md` for building the Power BI report step by step. Raw data and the large generated files are excluded by `.gitignore` and are re-created by each project's loader.

## Suggested order
1. Project 3 (Toronto 311: clean, local, quick)
2. Project 1 (small files, good for DAX and time series)
3. Project 4 (shows DP-600, large data)
4. Project 2
5. Project 5

## Setup
```bash
python -m venv .venv
.venv\Scripts\activate
pip install pandas numpy requests openpyxl
```
Each folder has a README (the case-study write-up), `sql/`, and a loader script. Run the loader, check the printed columns and checks, then open the `.db` file in DB Browser for SQLite or import the CSV outputs into Power BI Desktop.

## Rules for every project
- State the source, licence, refresh date and limits at the top of the README and on the report.
- Show a KPI table, 3 to 5 findings, and 3 recommendations in plain business language.
- Include a data-quality section: row counts, null checks, reconciliation to source totals.
- Add screenshots to the GitHub README. Only use Publish to web for public, non-sensitive data.
- Document every DAX measure and its business definition.
