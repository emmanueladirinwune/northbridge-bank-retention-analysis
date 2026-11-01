-- Collapse each customer's 12 months into one row of activity features.
CREATE OR REPLACE TABLE activity AS
SELECT split, account_id,
       SUM(inflow)  FILTER (WHERE rn <= 3)            AS inflow_3m,
       SUM(inflow)  FILTER (WHERE rn BETWEEN 4 AND 6) AS inflow_prev_3m,
       SUM(inflow)                                    AS inflow_12m,
       SUM(outflow) FILTER (WHERE rn <= 3)            AS outflow_3m,
       SUM(n_txn)   FILTER (WHERE rn <= 3)            AS txn_3m,
       SUM(n_txn)                                     AS txn_12m,
       STDDEV_SAMP(inflow)                            AS inflow_volatility,
       COUNT(*) FILTER (WHERE n_txn = 0)              AS quiet_months_12m,
       COUNT(*) FILTER (WHERE inflow_mom < 0 AND rn <= 6) AS falling_months_6m,
       MAX(inflow_roll_3m) FILTER (WHERE rn = 1)
         / NULLIF(MAX(inflow_roll_3m) FILTER (WHERE rn = 4), 0) AS inflow_trend
FROM trended
GROUP BY split, account_id;
