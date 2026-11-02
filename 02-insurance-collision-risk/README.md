# Project 2: Insurance, Collision Severity and Risk-Factor Analysis

**Role targeted:** Reporting / BI Analyst at a Canadian P&C insurer (underwriting or claims analytics)
**Data:** Transport Canada [National Collision Database](https://open.canada.ca/data/en/dataset/1eb9eba7-71d1-4b30-9fb1-30cbdab7e63a) (Open Government Licence - Canada). CSVs exist for 1999-2001, 2019, 2020 and 2021 (the English 2021 link was blank in the catalogue when I checked); other years are XLSX. This project uses 2019 and 2020 (about 17 MB and 16 MB). Download the [data dictionary PDF](https://open.canada.ca/data/dataset/1eb9eba7-71d1-4b30-9fb1-30cbdab7e63a/resource/21eb7966-38da-4814-a80e-521bce6c4c27/download/data_dictionary.pdf) and check every code label in the script against it.

## What this data is and is not
- Police-reported **fatal and injury** collisions only. No property-damage-only collisions.
- Not insurance claims. Do not report loss ratios, premiums or pricing.
- I did not check whether the file includes a province field. If it does, add it.
- The file is person-level (one row per person per vehicle). I could not confirm a collision ID, so the loader derives one from row order (a new collision starts at vehicle 1, person 1) and checks it against the vehicle-count field. Say so in your methodology note.

## Business problem
A claims and underwriting analytics team wants to understand when, where and under what conditions severe collisions concentrate, and which driver and vehicle characteristics are associated with injury severity, to inform risk monitoring and safe-driving messaging.

## Deliverables
- Clean SQLite tables: `persons`, `collisions`
- Power BI report: Overview, Conditions (weather, road surface, time), People and vehicles
- Methodology note with the collision-ID assumption, code mappings and limitations

## Steps
1. `python load_ncdb.py` downloads the two CSVs into `data/`, validates columns, builds the tables, and prints checks.
2. Run `sql/analysis.sql`.
3. Import `collisions.csv` and `persons.csv` into Power BI. Relate on `collision_id`.

## Core DAX measures
```DAX
Collisions = DISTINCTCOUNT(collisions[collision_id])
Fatal Collisions = CALCULATE([Collisions], collisions[severity] = "Fatal")
Fatal Share = DIVIDE([Fatal Collisions], [Collisions])
People Involved = COUNTROWS(persons)
Fatality Rate (persons) = DIVIDE(CALCULATE([People Involved], persons[person_severity] = "Fatality"), [People Involved])
Avg Vehicles per Collision = AVERAGE(collisions[vehicles])
```

## Report ideas
- Collisions by hour and weekday (heat map) with fatal share
- Fatal share by weather and road surface
- Person injury severity by age band, sex and seat position
- Vehicle age at collision vs severity

## Stretch
Compare 2019 with 2020 (pandemic year) and explain the change, with the caveat that the database is police-reported.
