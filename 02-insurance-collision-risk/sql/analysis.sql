-- Totals by year
SELECT year,
       COUNT(*) AS collisions,
       SUM(CASE WHEN severity = 'Fatal' THEN 1 ELSE 0 END) AS fatal,
       ROUND(100.0 * SUM(CASE WHEN severity = 'Fatal' THEN 1 ELSE 0 END) / COUNT(*), 2) AS fatal_share_pct
FROM collisions
GROUP BY year
ORDER BY year;

-- Fatal share by weather
SELECT weather,
       COUNT(*) AS collisions,
       ROUND(100.0 * SUM(CASE WHEN severity = 'Fatal' THEN 1 ELSE 0 END) / COUNT(*), 2) AS fatal_share_pct
FROM collisions
WHERE weather IS NOT NULL
GROUP BY weather
ORDER BY collisions DESC;

-- Fatal share by road surface
SELECT road_surface,
       COUNT(*) AS collisions,
       ROUND(100.0 * SUM(CASE WHEN severity = 'Fatal' THEN 1 ELSE 0 END) / COUNT(*), 2) AS fatal_share_pct
FROM collisions
WHERE road_surface IS NOT NULL
GROUP BY road_surface
ORDER BY collisions DESC;

-- Collisions by hour of day
SELECT hour,
       COUNT(*) AS collisions,
       ROUND(100.0 * SUM(CASE WHEN severity = 'Fatal' THEN 1 ELSE 0 END) / COUNT(*), 2) AS fatal_share_pct
FROM collisions
WHERE hour IS NOT NULL
GROUP BY hour
ORDER BY hour;

-- Person severity by age band
SELECT age_band,
       COUNT(*) AS people,
       ROUND(100.0 * SUM(CASE WHEN person_severity = 'Fatality' THEN 1 ELSE 0 END) / COUNT(*), 2) AS fatality_pct
FROM persons
WHERE age_band <> 'nan'
GROUP BY age_band
ORDER BY age_band;

-- Severity vs vehicle age
SELECT CASE WHEN vehicle_age IS NULL THEN 'Unknown'
            WHEN vehicle_age <= 3 THEN '0-3'
            WHEN vehicle_age <= 7 THEN '4-7'
            WHEN vehicle_age <= 12 THEN '8-12'
            ELSE '13+' END AS vehicle_age_band,
       COUNT(*) AS people,
       ROUND(100.0 * SUM(CASE WHEN person_severity = 'Fatality' THEN 1 ELSE 0 END) / COUNT(*), 2) AS fatality_pct
FROM persons
GROUP BY vehicle_age_band
ORDER BY vehicle_age_band;
