-- Balance behaviour in the months before each loan (same window as loan_monthly).
-- The balance column includes bank entries, so all transactions are used here.
CREATE OR REPLACE TABLE loan_balance AS
WITH bounds AS (
  SELECT loan_id, account_id, payments,
         date_trunc('month', granted) AS loan_month,
         GREATEST(date_trunc('month', opened),
                  date_trunc('month', granted) - INTERVAL 12 MONTH) AS first_month
  FROM loans
)
SELECT b.loan_id,
       MIN(t.balance)                                    AS min_balance,
       AVG(t.balance)                                    AS avg_balance,
       arg_max(t.balance, t.dt)                          AS last_balance,
       AVG(CASE WHEN t.balance < 0 THEN 1.0 ELSE 0 END)  AS negative_share,
       MIN(t.balance) / NULLIF(MAX(b.payments), 0)       AS min_balance_in_payments
FROM bounds b
JOIN trans t
  ON t.account_id = b.account_id
 AND t.dt >= b.first_month
 AND t.dt <  b.loan_month          -- strictly before the loan month: no leakage
GROUP BY b.loan_id;
