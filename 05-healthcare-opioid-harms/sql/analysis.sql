-- Analysis and data-quality queries for harms.db (table `harms`, loaded by fetch_harms.py from the PHAC CSV).
-- The file is a flattened export of website charts: one row per plotted point, English and French labels side by side.
-- `value` is TEXT and mixes numbers, the string 'Suppr.' (suppressed small count) and NULL (s.o., not applicable).

-- 1. What is in the file: rows by source and kind of chart
SELECT source, specific_measure, COUNT(*) AS rows
FROM harms
GROUP BY source, specific_measure
ORDER BY source, rows DESC;

-- 2. Three kinds of "empty": real numbers, suppressed, and not available (a real zero is a zero)
SELECT CASE WHEN value IS NULL THEN 'Not available (blank)'
            WHEN value = 'Suppr.' THEN 'Suppressed'
            WHEN CAST(value AS REAL) = 0 THEN 'Reported zero'
            ELSE 'Reported' END AS value_kind,
       COUNT(*) AS rows,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM harms), 1) AS pct_of_rows
FROM harms
GROUP BY 1
ORDER BY rows DESC;

-- 3. Key check: the three tables are unique on their natural key (each query should return zero rows)
SELECT source, substance, region, xaxislabels, unit, COUNT(*) AS n
FROM harms
WHERE specific_measure = 'Overall numbers' AND time_period = 'By year'
GROUP BY source, substance, region, xaxislabels, unit
HAVING COUNT(*) > 1;

-- 4. Who reports? Jurisdictions with a published opioid count for 2024, by source.
--    "Canada" is the sum of these, not of all 13 provinces and territories.
SELECT source, COUNT(*) AS jurisdictions_reporting, GROUP_CONCAT(region, ', ') AS reporting
FROM harms
WHERE specific_measure = 'Overall numbers' AND time_period = 'By year' AND unit = 'Number'
  AND substance = 'Opioids' AND xaxislabels = '2024' AND region <> 'Canada'
  AND value IS NOT NULL AND value <> 'Suppr.'
GROUP BY source;

-- 5. Does Canada equal the sum of its parts? (2024, opioids)
--    Deaths, ED visits and hospitalizations match exactly. EMS differs by 2,622 because its Canada total also includes
--    Winnipeg, Whitehorse and Yellowknife, which are excluded here (they stand in for Manitoba, Yukon and the Northwest Territories).
SELECT h.source,
       MAX(CASE WHEN h.region = 'Canada' THEN CAST(h.value AS REAL) END) AS canada,
       SUM(CASE WHEN h.region <> 'Canada' AND h.value NOT IN ('Suppr.') THEN CAST(h.value AS REAL) END) AS sum_of_listed_regions
FROM harms h
WHERE h.specific_measure = 'Overall numbers' AND h.time_period = 'By year' AND h.unit = 'Number'
  AND h.substance = 'Opioids' AND h.xaxislabels = '2024'
  AND h.region NOT IN ('Northern and rural Manitoba', 'Winnipeg, Manitoba', 'Whitehorse, Yukon', 'Yellowknife, Northwest Territories')
GROUP BY h.source;

-- 6. Quarters do not add up to the published year (Canada, opioid deaths): always a little lower
WITH q AS (
  SELECT SUBSTR(xaxislabels, 1, 4) AS yr, SUM(CAST(value AS REAL)) AS quarters_sum
  FROM harms
  WHERE source = 'Deaths' AND substance = 'Opioids' AND region = 'Canada' AND specific_measure = 'Overall numbers'
    AND time_period = 'By quarter' AND value IS NOT NULL
  GROUP BY 1),
y AS (
  SELECT xaxislabels AS yr, CAST(value AS REAL) AS year_value
  FROM harms
  WHERE source = 'Deaths' AND substance = 'Opioids' AND region = 'Canada' AND specific_measure = 'Overall numbers'
    AND time_period = 'By year' AND unit = 'Number')
SELECT q.yr, q.quarters_sum, y.year_value, y.year_value - q.quarters_sum AS gap
FROM q JOIN y USING (yr)
ORDER BY q.yr;

-- 7. Trend: opioid deaths, hospitalizations, ED visits and EMS responses for Canada by year
SELECT xaxislabels AS year,
       MAX(CASE WHEN source = 'Deaths' THEN CAST(value AS REAL) END) AS deaths,
       MAX(CASE WHEN source = 'Hospitalizations' THEN CAST(value AS REAL) END) AS hospitalizations,
       MAX(CASE WHEN source = 'Emergency Department (ED) Visits' THEN CAST(value AS REAL) END) AS ed_visits,
       MAX(CASE WHEN source = 'Emergency Medical Services (EMS)' THEN CAST(value AS REAL) END) AS ems_responses
FROM harms
WHERE specific_measure = 'Overall numbers' AND time_period = 'By year' AND unit = 'Number'
  AND substance = 'Opioids' AND region = 'Canada'
GROUP BY xaxislabels
ORDER BY xaxislabels;

-- 8. Province comparison: opioid death rate per 100,000 in 2024, with the value status shown
SELECT region,
       CASE WHEN value IS NULL THEN 'Not available' WHEN value = 'Suppr.' THEN 'Suppressed' ELSE value END AS rate_per_100k
FROM harms
WHERE source = 'Deaths' AND substance = 'Opioids' AND specific_measure = 'Overall numbers'
  AND time_period = 'By year' AND unit = 'Crude rate' AND xaxislabels = '2024'
ORDER BY CAST(value AS REAL) DESC;
