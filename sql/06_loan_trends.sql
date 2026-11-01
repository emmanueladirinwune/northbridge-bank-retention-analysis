-- Same window functions as 03_trends.sql, but each loan is its own partition.
CREATE OR REPLACE TABLE loan_trended AS
SELECT *,
       AVG(inflow) OVER (PARTITION BY loan_id ORDER BY month
                         ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS inflow_roll_3m,
       inflow - LAG(inflow) OVER (PARTITION BY loan_id ORDER BY month) AS inflow_mom,
       outflow - inflow AS net_outflow,   -- positive = spent more than came in
       ROW_NUMBER() OVER (PARTITION BY loan_id ORDER BY month DESC) AS rn
FROM loan_monthly;
