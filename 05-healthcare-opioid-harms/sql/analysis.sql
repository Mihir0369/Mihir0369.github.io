-- TEMPLATE. Run fetch_harms.py, read the printed columns, then replace the <placeholders>:
--   <period>     time column      <region>   province/territory column
--   <measure>    event type (hospitalizations / EMS / deaths) column
--   <substance>  substance column <value>    numeric count or rate column

-- 1. Row counts by measure and region
SELECT <measure>, <region>, COUNT(*) AS rows
FROM harms
GROUP BY <measure>, <region>
ORDER BY <measure>, <region>;

-- 2. Trend by period for one measure
SELECT <period>, SUM(<value>) AS events
FROM harms
WHERE <measure> = '<chosen measure>'
  AND <region> = 'Canada'
GROUP BY <period>
ORDER BY <period>;

-- 3. Province comparison for the latest period
SELECT <region>, <value>
FROM harms
WHERE <measure> = '<chosen measure>'
  AND <period> = (SELECT MAX(<period>) FROM harms)
ORDER BY <value> DESC;

-- 4. Data-quality checks
SELECT COUNT(*) AS rows_total,
       SUM(CASE WHEN <value> IS NULL THEN 1 ELSE 0 END) AS null_values
FROM harms;
