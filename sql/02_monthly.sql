-- One row per customer per month, for the 12 months up to each cutoff.
CREATE OR REPLACE TABLE monthly AS
WITH cutoffs AS (
  SELECT 'train' AS split, DATE '1997-12-31' AS cutoff
  UNION ALL
  SELECT 'test', DATE '1998-06-30'
),
cust AS (  -- customer-initiated transactions only
  SELECT account_id, dt, type, amount
  FROM trans
  WHERE TRIM(COALESCE(k_symbol, '')) NOT IN ('UROK', 'SLUZBY', 'SANKC. UROK')
),
grid AS (  -- every labelled customer x each of the 12 months
  SELECT l.split, l.account_id,
         UNNEST(generate_series(date_trunc('month', c.cutoff)::TIMESTAMP - INTERVAL 11 MONTH,
                                date_trunc('month', c.cutoff)::TIMESTAMP,
                                INTERVAL 1 MONTH))::DATE AS month
  FROM labels l JOIN cutoffs c USING (split)
)
SELECT g.split, g.account_id, g.month,
       COALESCE(SUM(t.amount) FILTER (WHERE t.type = 'PRIJEM'), 0) AS inflow,
       COALESCE(SUM(t.amount) FILTER (WHERE t.type <> 'PRIJEM'), 0) AS outflow,
       COUNT(t.dt) AS n_txn
FROM grid g
LEFT JOIN cust t
  ON t.account_id = g.account_id AND date_trunc('month', t.dt) = g.month
GROUP BY g.split, g.account_id, g.month;
