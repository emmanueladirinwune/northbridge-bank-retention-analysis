-- Add trend columns to each customer's 12 months using window functions.
CREATE OR REPLACE TABLE trended AS
SELECT *,
       -- average inflow over this month and the 2 before it
       AVG(inflow) OVER (PARTITION BY split, account_id ORDER BY month
                         ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS inflow_roll_3m,
       -- change from the previous month
       inflow - LAG(inflow) OVER (PARTITION BY split, account_id ORDER BY month) AS inflow_mom,
       -- 1 = most recent month, 12 = oldest
       ROW_NUMBER() OVER (PARTITION BY split, account_id ORDER BY month DESC) AS rn
FROM monthly;
