-- Step A: the loans we study, with their split and outcome.
-- 1998 loans are excluded (censored: too young to have an outcome yet).
CREATE OR REPLACE TABLE loans AS
SELECT l.loan_id, l.account_id, l.granted, l.amount, l.duration, l.payments,
       CASE WHEN YEAR(l.granted) <= 1996 THEN 'train' ELSE 'test' END AS split,
       CASE WHEN l.status IN ('B', 'D') THEN 1 ELSE 0 END AS bad,
       a.opened
FROM loan l JOIN account a USING (account_id)
WHERE YEAR(l.granted) <= 1997;

-- Step B: one row per loan per month, for up to 12 full months BEFORE the loan month.
-- Customers with less history get fewer months; nothing on or after the loan month is used.
CREATE OR REPLACE TABLE loan_monthly AS
WITH bounds AS (
  SELECT loan_id, account_id,
         date_trunc('month', granted) - INTERVAL 1 MONTH AS last_month,
         GREATEST(date_trunc('month', opened),
                  date_trunc('month', granted) - INTERVAL 12 MONTH) AS first_month
  FROM loans
),
grid AS (
  SELECT loan_id, account_id,
         UNNEST(generate_series(first_month::TIMESTAMP, last_month::TIMESTAMP,
                                INTERVAL 1 MONTH))::DATE AS month
  FROM bounds
),
cust AS (  -- customer-initiated transactions only
  SELECT account_id, dt, type, amount
  FROM trans
  WHERE TRIM(COALESCE(k_symbol, '')) NOT IN ('UROK', 'SLUZBY', 'SANKC. UROK')
)
SELECT g.loan_id, g.account_id, g.month,
       COALESCE(SUM(t.amount) FILTER (WHERE t.type = 'PRIJEM'), 0) AS inflow,
       COALESCE(SUM(t.amount) FILTER (WHERE t.type <> 'PRIJEM'), 0) AS outflow,
       COUNT(t.dt) AS n_txn
FROM grid g
LEFT JOIN cust t
  ON t.account_id = g.account_id AND date_trunc('month', t.dt) = g.month
GROUP BY g.loan_id, g.account_id, g.month;
