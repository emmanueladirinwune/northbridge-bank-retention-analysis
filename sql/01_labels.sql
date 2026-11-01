CREATE OR REPLACE TABLE labels AS
WITH inflow AS (
  SELECT account_id, dt, amount FROM trans
  WHERE type = 'PRIJEM' AND TRIM(COALESCE(k_symbol, '')) <> 'UROK'
),
windows AS (
  SELECT 'train' AS split, DATE '1997-07-01' AS b0, DATE '1997-12-31' AS b1,
         DATE '1998-01-01' AS a0, DATE '1998-06-30' AS a1
  UNION ALL
  SELECT 'test', DATE '1998-01-01', DATE '1998-06-30',
         DATE '1998-07-01', DATE '1998-12-31'
)
SELECT w.split, i.account_id,
       SUM(amount) FILTER (WHERE dt BETWEEN w.b0 AND w.b1) AS in_before,
       COALESCE(SUM(amount) FILTER (WHERE dt BETWEEN w.a0 AND w.a1), 0) AS in_after,
       CASE WHEN COALESCE(SUM(amount) FILTER (WHERE dt BETWEEN w.a0 AND w.a1), 0)
                 <= 0.5 * SUM(amount) FILTER (WHERE dt BETWEEN w.b0 AND w.b1)
            THEN 1 ELSE 0 END AS churn
FROM inflow i CROSS JOIN windows w
GROUP BY w.split, i.account_id
HAVING SUM(amount) FILTER (WHERE dt BETWEEN w.b0 AND w.b1) > 0;
