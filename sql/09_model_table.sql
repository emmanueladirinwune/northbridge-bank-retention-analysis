-- Final modelling table: one row per loan, every feature in one place.
CREATE OR REPLACE TABLE model_table AS
SELECT f.*,
       b.min_balance,
       b.avg_balance,
       b.last_balance,
       b.negative_share,
       b.min_balance_in_payments
FROM loan_features f
JOIN loan_balance b USING (loan_id);
