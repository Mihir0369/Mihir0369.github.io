-- Run fetch_banking_data.py first; it prints the distinct values of each table's dimension columns.
-- Statistics Canada tables use: ref_date, geo, <dimension columns>, value.

-- 1. Rates: yearly averages
SELECT substr(month, 1, 4) AS year,
       ROUND(AVG(overnight_target), 2) AS avg_overnight_target,
       ROUND(AVG(prime_rate), 2)       AS avg_prime,
       ROUND(AVG(mortgage_5y), 2)      AS avg_5y_mortgage
FROM rates_monthly
GROUP BY year
ORDER BY year;

-- 2. Explore the credit table: which categories exist?
-- Replace <category_column> with the dimension column name printed by the loader.
-- SELECT DISTINCT <category_column> FROM credit_liabilities_households;

-- 3. Monthly credit balance next to rates (TEMPLATE: set the category filter)
-- SELECT c.ref_date,
--        c.value AS balance,
--        r.prime_rate,
--        r.mortgage_5y
-- FROM credit_liabilities_households c
-- JOIN rates_monthly r ON r.month = c.ref_date
-- WHERE c.geo = 'Canada'
--   AND c.<category_column> = '<chosen category>'
-- ORDER BY c.ref_date;

-- 4. Year-over-year growth (TEMPLATE, same filter as above)
-- SELECT cur.ref_date,
--        ROUND(100.0 * (cur.value - prev.value) / prev.value, 2) AS yoy_pct
-- FROM credit_liabilities_households cur
-- JOIN credit_liabilities_households prev
--   ON prev.geo = cur.geo
--  AND prev.<category_column> = cur.<category_column>
--  AND prev.ref_date = strftime('%Y-%m', date(cur.ref_date || '-01', '-1 year'))
-- WHERE cur.geo = 'Canada' AND cur.<category_column> = '<chosen category>'
-- ORDER BY cur.ref_date;

-- 5. Data-quality checks
SELECT COUNT(*) AS months,
       SUM(CASE WHEN prime_rate IS NULL THEN 1 ELSE 0 END) AS missing_prime,
       SUM(CASE WHEN mortgage_5y IS NULL THEN 1 ELSE 0 END) AS missing_mortgage_5y
FROM rates_monthly;
