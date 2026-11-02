-- Works on stg_requests built by load_311.py (2023-2025).
-- The source has no close date, so these queries measure demand and request outcome (status), not time to close.

-- q1_volume_by_year
SELECT year, COUNT(*) AS requests
FROM stg_requests
GROUP BY year
ORDER BY year;

-- q2_status_by_year (share of requests by outcome group)
SELECT year, status_group,
       COUNT(*) AS requests,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY year), 1) AS pct_of_year
FROM stg_requests
GROUP BY year, status_group
ORDER BY year, status_group;

-- q3_top_service_types (2025)
SELECT service_request_type,
       COUNT(*) AS requests,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_of_total
FROM stg_requests
WHERE year = 2025
GROUP BY service_request_type
ORDER BY requests DESC
LIMIT 15;

-- q4_fastest_growing_types (2024 vs 2023: type names changed in January 2025, so 2025 cannot be compared by type)
SELECT service_request_type,
       SUM(CASE WHEN year = 2023 THEN 1 ELSE 0 END) AS y2023,
       SUM(CASE WHEN year = 2024 THEN 1 ELSE 0 END) AS y2024,
       ROUND(100.0 * (SUM(CASE WHEN year = 2024 THEN 1 ELSE 0 END) - SUM(CASE WHEN year = 2023 THEN 1 ELSE 0 END))
             / SUM(CASE WHEN year = 2023 THEN 1 ELSE 0 END), 1) AS growth_pct
FROM stg_requests
WHERE year IN (2023, 2024)
GROUP BY service_request_type
HAVING SUM(CASE WHEN year = 2023 THEN 1 ELSE 0 END) >= 2000
ORDER BY growth_pct DESC
LIMIT 10;

-- q5_division_scorecard (2025; division_group joins the Parks/Forestry division renamed in 2025)
SELECT division_group,
       COUNT(*) AS requests,
       ROUND(100.0 * SUM(CASE WHEN status_group = 'Resolved'  THEN 1 ELSE 0 END) / COUNT(*), 1) AS resolved_pct,
       ROUND(100.0 * SUM(CASE WHEN status_group = 'Cancelled' THEN 1 ELSE 0 END) / COUNT(*), 1) AS cancelled_pct,
       ROUND(100.0 * SUM(CASE WHEN status_group = 'Open'      THEN 1 ELSE 0 END) / COUNT(*), 1) AS open_pct
FROM stg_requests
WHERE year = 2025
GROUP BY division_group
ORDER BY requests DESC;

-- q6_cancel_rate_by_type (2025, at least 5,000 requests)
SELECT service_request_type,
       COUNT(*) AS requests,
       ROUND(100.0 * SUM(CASE WHEN status_group = 'Cancelled' THEN 1 ELSE 0 END) / COUNT(*), 1) AS cancelled_pct
FROM stg_requests
WHERE year = 2025
GROUP BY service_request_type
HAVING COUNT(*) >= 5000
ORDER BY cancelled_pct DESC
LIMIT 10;

-- q7_monthly_volume
SELECT month, COUNT(*) AS requests
FROM stg_requests
GROUP BY month
ORDER BY month;

-- q8_wards_2025
SELECT ward_name,
       COUNT(*) AS requests,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_of_total
FROM stg_requests
WHERE year = 2025 AND ward_name IS NOT NULL
GROUP BY ward_name
ORDER BY requests DESC
LIMIT 10;

-- q9_open_by_age (requests still New/In Progress, by creation year)
SELECT year,
       SUM(CASE WHEN status_group = 'Open' THEN 1 ELSE 0 END) AS still_open,
       ROUND(100.0 * SUM(CASE WHEN status_group = 'Open' THEN 1 ELSE 0 END) / COUNT(*), 1) AS still_open_pct
FROM stg_requests
GROUP BY year
ORDER BY year;

-- q11_open_share_by_division_year
SELECT division_group, year,
       COUNT(*) AS requests,
       ROUND(100.0 * SUM(CASE WHEN status_group = 'Open' THEN 1 ELSE 0 END) / COUNT(*), 1) AS open_pct
FROM stg_requests
GROUP BY division_group, year
HAVING COUNT(*) >= 1000
ORDER BY division_group, year;

-- q12_forestry_open_by_type (2023-2025, Parks/Forestry group, top types)
SELECT service_request_type,
       COUNT(*) AS requests,
       ROUND(100.0 * SUM(CASE WHEN status_group = 'Open' THEN 1 ELSE 0 END) / COUNT(*), 1) AS open_pct
FROM stg_requests
WHERE division_group = 'Parks, Forestry & Environment'
GROUP BY service_request_type
ORDER BY requests DESC
LIMIT 8;

-- q13_first_month_of_selected_types (snow and bin-repair types appear only from January 2025)
SELECT service_request_type, MIN(month) AS first_month, COUNT(*) AS requests
FROM stg_requests
WHERE service_request_type IN ('Sidewalk Snow Clearing Required', 'Road Plowing Request',
      'Driveway Blocked By Plowed Snowbank', 'Residential Bin Lid Damaged')
GROUP BY service_request_type;

-- q14_taxonomy_change (type names that exist only in 2025)
WITH t AS (
  SELECT service_request_type,
         SUM(CASE WHEN year < 2025 THEN 1 ELSE 0 END) AS before_2025,
         SUM(CASE WHEN year = 2025 THEN 1 ELSE 0 END) AS in_2025
  FROM stg_requests
  GROUP BY service_request_type
)
SELECT COUNT(CASE WHEN before_2025 = 0 AND in_2025 > 0 THEN 1 END) AS new_type_names,
       SUM(CASE WHEN before_2025 = 0 THEN in_2025 ELSE 0 END) AS requests_with_new_names,
       SUM(in_2025) AS requests_2025,
       ROUND(100.0 * SUM(CASE WHEN before_2025 = 0 THEN in_2025 ELSE 0 END) / SUM(in_2025), 1) AS pct_with_new_names
FROM t;

-- q10_data_quality
SELECT COUNT(*) AS rows_total,
       SUM(CASE WHEN created_ts IS NULL THEN 1 ELSE 0 END) AS missing_created,
       SUM(CASE WHEN division IS NULL THEN 1 ELSE 0 END) AS missing_division,
       SUM(CASE WHEN ward IS NULL THEN 1 ELSE 0 END) AS missing_ward,
       SUM(CASE WHEN service_request_type IS NULL THEN 1 ELSE 0 END) AS missing_type,
       SUM(CASE WHEN status_group = 'Unknown' THEN 1 ELSE 0 END) AS unknown_status
FROM stg_requests;
