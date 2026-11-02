# Project 4: IT Consulting, Federal Procurement Analytics on a Fabric Lakehouse

**Role targeted:** Fabric Analytics Engineer / Power BI Developer / BI consultant
**Data:** Treasury Board of Canada Secretariat, [Proactive Publication - Contracts](https://open.canada.ca/data/dataset/d8f85d91-7dec-4fd1-8055-483b77225d8b) (Open Government Licence - Canada). The main file, `contracts.csv`, is about **655 MB**: federal contracts over $10,000. A data dictionary and a JSON schema are published with it. The schema lists 41 fields, including `vendor_name`, `buyer_name`, `contract_date`, `contract_value`, `original_value`, `amendment_value`, `commodity_type`, `solicitation_procedure`, `number_of_bids`, `trade_agreement`, `country_of_vendor`, `instrument_type`, and `reporting_period`.

A file this size is a real reason to use a lakehouse, which makes this a better DP-600 showpiece than a toy sample.

## Client scenario
A procurement-advisory client wants a governed, refreshable view of federal contracting: who buys what, how competitive awards are, how much contracts grow through amendments, and which vendors dominate. You build the lakehouse, the star schema, and a certified semantic model.

## Deliverables
- Architecture diagram: source file, bronze, silver, gold, semantic model, report
- Fabric lakehouse with Delta tables (`bronze_contracts`, `silver_contracts`, gold star schema)
- Semantic model (Direct Lake or Import) with documented measures, plus a row-level security example by department
- Power BI report: Spend overview, Competition and amendments, Vendor concentration
- Handover document: refresh approach, data dictionary, known limitations

## Steps
1. Create a Fabric workspace (trial capacity) and a lakehouse.
2. Download `contracts.csv` yourself from the dataset page and upload it to `Files/raw/` in the lakehouse (or ingest it with a pipeline Copy activity from the URL).
3. Run `notebooks/medallion.py` in a Fabric notebook. It prints schema and reconciliation checks, and adapts to whichever department column exists.
4. Create the semantic model on the gold tables, set relationships, add measures and RLS.
5. Build the report and check performance with Performance Analyzer.
6. Write the handover document and a short note on how you would promote dev to prod.

## Core DAX measures
```DAX
Contract Value = SUM(fact_contracts[contract_value])
Contracts = COUNTROWS(fact_contracts)
Avg Contract Value = DIVIDE([Contract Value], [Contracts])
Amendment Uplift % = DIVIDE(SUM(fact_contracts[amendment_value]), SUM(fact_contracts[original_value]))
Competitive Share = DIVIDE(CALCULATE([Contracts], fact_contracts[is_competitive] = 1), [Contracts])
Top 10 Vendor Share = DIVIDE(SUMX(TOPN(10, VALUES(dim_vendor[vendor_name]), [Contract Value]), [Contract Value]), [Contract Value])
Contract Value YoY % = DIVIDE([Contract Value] - CALCULATE([Contract Value], SAMEPERIODLASTYEAR(dim_date[date])), CALCULATE([Contract Value], SAMEPERIODLASTYEAR(dim_date[date])))
```

## Notes and limits
- Contracts are published up to several months after award, so the latest months are incomplete. Say so on the report.
- There is a separate aggregate file for contracts of $10K and under and a legacy file. Use only the over-$10,000 file unless you document otherwise.
- Fabric trial capacity expires. Take screenshots, export the notebook, and record a short walkthrough.
