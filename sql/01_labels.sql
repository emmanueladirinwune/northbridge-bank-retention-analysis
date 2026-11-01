-- Churn label, version 2.
-- A customer churns if their TYPICAL (median) monthly income in the 6 months
-- after the cutoff is half or less of their typical income in the 6 months before.
-- Medians ignore one-off spikes such as bonuses or property sales.
-- Customers with no income in the last 3 months before the cutoff are excluded:
-- they have already left, so there is nothing left to predict.
CREATE OR REPLACE TABLE labels AS
WITH windows AS (
  SELECT 'train' AS split, DATE '1997-07-01' AS b0, DATE '1997-12-31' AS b1,
         DATE '1998-01-01' AS a0, DATE '1998-06-30' AS a1
  UNION ALL
  SELECT 'test', DATE '1998-01-01', DATE '1998-06-30',
         DATE '1998-07-01', DATE '1998-12-31'
),
inflow AS (  -- income only, excluding bank interest
  SELECT account_id, date_trunc('month', dt) AS month, SUM(amount) AS amount
  FROM trans
  WHERE type = 'PRIJEM' AND TRIM(COALESCE(k_symbol, '')) <> 'UROK'
  GROUP BY account_id, date_trunc('month', dt)
),
grid AS (  -- every account x every month from Jul 1997 to Dec 1998
  SELECT a.account_id,
         UNNEST(generate_series(TIMESTAMP '1997-07-01', TIMESTAMP '1998-12-01',
                                INTERVAL 1 MONTH))::DATE AS month
  FROM (SELECT DISTINCT account_id FROM trans) a
),
monthly_in AS (  -- zero-filled monthly income
  SELECT g.account_id, g.month, COALESCE(i.amount, 0) AS amount
  FROM grid g LEFT JOIN inflow i USING (account_id, month)
)
SELECT w.split, m.account_id,
       MEDIAN(amount) FILTER (WHERE month BETWEEN w.b0 AND w.b1) AS med_before,
       MEDIAN(amount) FILTER (WHERE month BETWEEN w.a0 AND w.a1) AS med_after,
       SUM(amount)    FILTER (WHERE month BETWEEN w.b0 AND w.b1) AS in_before,
       CASE WHEN MEDIAN(amount) FILTER (WHERE month BETWEEN w.a0 AND w.a1)
                 <= 0.5 * MEDIAN(amount) FILTER (WHERE month BETWEEN w.b0 AND w.b1)
            THEN 1 ELSE 0 END AS churn
FROM monthly_in m CROSS JOIN windows w
GROUP BY w.split, m.account_id
HAVING MEDIAN(amount) FILTER (WHERE month BETWEEN w.b0 AND w.b1) > 0
      AND SUM(amount) FILTER (WHERE month > w.b1 - INTERVAL 3 MONTH AND month <= w.b1) > 0
   AND COUNT(*) FILTER (WHERE month BETWEEN w.b0 AND w.b1 AND amount > 0) = 6;

