-- One row per loan: behaviour before the loan, plus the loan's own terms.
-- Averages are per month, so customers with 4 months and 12 months compare fairly.
CREATE OR REPLACE TABLE loan_features AS
WITH behaviour AS (
  SELECT loan_id,
         COUNT(*)                                          AS months_history,
         AVG(inflow)                                       AS avg_inflow,
         AVG(outflow)                                      AS avg_outflow,
         AVG(n_txn)                                        AS avg_txn,
         STDDEV_SAMP(inflow) / NULLIF(AVG(inflow), 0)      AS inflow_cv,
         STDDEV_SAMP(net_outflow) / NULLIF(AVG(inflow), 0) AS net_swing,
         AVG(CASE WHEN net_outflow > 0 THEN 1.0 ELSE 0 END) AS overspend_share,
         AVG(CASE WHEN n_txn = 0 THEN 1.0 ELSE 0 END)       AS quiet_share,
         COUNT(*) FILTER (WHERE inflow_mom < 0 AND rn <= 6) AS falling_months_6m,
         MAX(inflow_roll_3m) FILTER (WHERE rn = 1)
           / NULLIF(MAX(inflow_roll_3m) FILTER (WHERE rn = 4), 0) AS inflow_trend
  FROM loan_trended
  GROUP BY loan_id
)
SELECT l.loan_id, l.split, l.bad,
       b.* EXCLUDE (loan_id),
       l.amount   AS loan_amount,
       l.duration AS loan_duration,
       l.payments AS loan_payment,
       l.payments / NULLIF(b.avg_inflow, 0) AS payment_to_income   -- affordability
FROM loans l
JOIN behaviour b USING (loan_id);
