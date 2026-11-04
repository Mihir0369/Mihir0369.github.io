-- Project 2 analysis queries. Run against ncdb.db (built by load_ncdb.py).
-- Every number here is reconciled with the Power BI measures: 185,772 collisions, 3,225 fatal, 463,630 people.
-- "Fatal share" = fatal collisions / (fatal + injury collisions). The file holds fatal and injury collisions only.

-- 1. Totals by year: collisions fell 24.4% in 2020, fatal collisions only 1.3%
SELECT year,
       COUNT(*)                                                         AS collisions,
       SUM(severity = 'Fatal')                                          AS fatal,
       SUM(severity = 'Injury')                                         AS injury,
       ROUND(100.0 * SUM(severity = 'Fatal') / COUNT(*), 2)             AS fatal_share_pct
FROM collisions
GROUP BY year
ORDER BY year;

-- 2. Where the 2020 decline came from: injury collisions are 99.9% of the 25,792 fewer collisions
WITH y AS (
    SELECT severity,
           SUM(year = 2019) AS c2019,
           SUM(year = 2020) AS c2020
    FROM collisions
    GROUP BY severity
)
SELECT severity, c2019, c2020, c2020 - c2019 AS change,
       ROUND(100.0 * (c2020 - c2019) / c2019, 1) AS pct_change,
       ROUND(100.0 * (c2019 - c2020) / (SELECT SUM(c2019 - c2020) FROM y), 1) AS pct_of_decline
FROM y;

-- 3. Fatal share by hour (the heat map on the When page). Hour is NULL for about 1% of collisions.
SELECT hour,
       COUNT(*)                                             AS collisions,
       ROUND(100.0 * SUM(severity = 'Fatal') / COUNT(*), 2) AS fatal_share_pct
FROM collisions
WHERE hour IS NOT NULL
GROUP BY hour
ORDER BY hour;

-- 4. Night (10 pm to 6 am) against the rest: 3.4% against 1.5%
SELECT CASE WHEN hour >= 22 OR hour < 6 THEN 'Night (10 pm to 6 am)'
            WHEN hour < 22 THEN 'Day (6 am to 10 pm)' END       AS part_of_day,
       COUNT(*)                                             AS collisions,
       SUM(severity = 'Fatal')                              AS fatal,
       ROUND(100.0 * SUM(severity = 'Fatal') / COUNT(*), 2) AS fatal_share_pct
FROM collisions
WHERE hour IS NOT NULL
GROUP BY part_of_day;

-- 5. Fatal share by condition (the inputs to the what-if scenario on the Conditions page)
SELECT 'Traffic control' AS factor, traffic_control AS level, COUNT(*) AS collisions, SUM(severity = 'Fatal') AS fatal,
       ROUND(100.0 * SUM(severity = 'Fatal') / COUNT(*), 2) AS fatal_share_pct
FROM collisions WHERE traffic_control <> 'Unknown or not reported' GROUP BY traffic_control
UNION ALL
SELECT 'Road alignment', CASE WHEN road_alignment LIKE 'Curved%' THEN 'Curved' WHEN road_alignment LIKE 'Straight%' THEN 'Straight' ELSE 'Hill' END,
       COUNT(*), SUM(severity = 'Fatal'), ROUND(100.0 * SUM(severity = 'Fatal') / COUNT(*), 2)
FROM collisions WHERE road_alignment <> 'Unknown or not reported' GROUP BY 2
UNION ALL
SELECT 'Collision group', configuration_group, COUNT(*), SUM(severity = 'Fatal'), ROUND(100.0 * SUM(severity = 'Fatal') / COUNT(*), 2)
FROM collisions WHERE configuration_group <> 'Unknown or not reported' GROUP BY configuration_group
ORDER BY factor, fatal_share_pct DESC;

-- 6. What-if, signals on uncontrolled roads: fatal collisions avoided if "No control" had the fatal share of "Signals"
--    avoided = fatal on no-control x (1 - signals share / no-control share) x share of the gap closed (here 100%). About 1,744.
WITH r AS (
    SELECT traffic_control, COUNT(*) AS n, SUM(severity = 'Fatal') AS fatal,
           1.0 * SUM(severity = 'Fatal') / COUNT(*) AS share
    FROM collisions
    WHERE traffic_control IN ('No control', 'Signals')
    GROUP BY traffic_control
)
SELECT a.fatal AS fatal_no_control,
       ROUND(a.share * 100, 2) AS share_no_control_pct,
       ROUND(b.share * 100, 2) AS share_signals_pct,
       ROUND(a.fatal * (1 - b.share / a.share), 0) AS fatal_avoided_at_100pct
FROM r a JOIN r b ON a.traffic_control = 'No control' AND b.traffic_control = 'Signals';

-- 7. People: fatality rate by road user (deaths / people in reported collisions)
SELECT user_type,
       COUNT(*)                                                   AS people,
       SUM(person_severity = 'Fatality')                          AS deaths,
       ROUND(100.0 * SUM(person_severity = 'Fatality') / COUNT(*), 2) AS fatality_pct
FROM persons
GROUP BY user_type
ORDER BY fatality_pct DESC;

-- 8. Occupants (drivers and passengers): safety device used against not used. 7.0% against 0.43%, about 16 times.
SELECT safety_device,
       COUNT(*)                                                   AS occupants,
       SUM(person_severity = 'Fatality')                          AS deaths,
       ROUND(100.0 * SUM(person_severity = 'Fatality') / COUNT(*), 2) AS fatality_pct
FROM persons
WHERE user_type IN ('Driver', 'Passenger')
GROUP BY safety_device
ORDER BY fatality_pct DESC;

-- 9. Does the safety-device gap survive a check by age band? It does: 7.0% to 10.8% against 0.3% to 1.05% in every band.
SELECT age_band,
       SUM(safety_device = 'No safety device used')                                            AS n_no_device,
       ROUND(100.0 * SUM(safety_device = 'No safety device used' AND person_severity = 'Fatality')
             / SUM(safety_device = 'No safety device used'), 2)                                AS pct_no_device,
       SUM(safety_device = 'Safety device used')                                               AS n_device,
       ROUND(100.0 * SUM(safety_device = 'Safety device used' AND person_severity = 'Fatality')
             / SUM(safety_device = 'Safety device used'), 2)                                   AS pct_device
FROM persons
WHERE user_type IN ('Driver', 'Passenger') AND age_band <> 'Unknown or not reported'
GROUP BY age_band
ORDER BY age_band;

-- 10. Fatality rate by age band
SELECT age_band,
       COUNT(*)                                                   AS people,
       SUM(person_severity = 'Fatality')                          AS deaths,
       ROUND(100.0 * SUM(person_severity = 'Fatality') / COUNT(*), 2) AS fatality_pct
FROM persons
GROUP BY age_band
ORDER BY age_band;

-- 11. Data checks that the model also enforces: unique collision ID, every person has a collision
SELECT (SELECT COUNT(*) FROM collisions)                                        AS collisions,
       (SELECT COUNT(DISTINCT collision_id) FROM collisions)                    AS distinct_ids,
       (SELECT COUNT(*) FROM persons WHERE collision_id NOT IN (SELECT collision_id FROM collisions)) AS orphan_people;
