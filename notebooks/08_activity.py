import duckdb
con = duckdb.connect("northbridge.duckdb")
con.execute(open("sql/04_activity.sql").read())

# Customer 1's features: one row per split
print(con.sql("SELECT * FROM activity WHERE account_id = 1 ORDER BY split DESC"))

# Do churners look different? Compare averages by label
print(con.sql("""
SELECT l.churn,
       COUNT(*) AS customers,
       ROUND(AVG(a.inflow_trend), 2)      AS avg_inflow_trend,
       ROUND(AVG(a.falling_months_6m), 2) AS avg_falling_months,
       ROUND(AVG(a.quiet_months_12m), 2)  AS avg_quiet_months
FROM activity a JOIN labels l USING (split, account_id)
WHERE a.split = 'train'
GROUP BY l.churn
ORDER BY l.churn
"""))

print(con.sql("""
SELECT l.churn,
       ROUND(MEDIAN(a.inflow_trend), 2)                       AS median_trend,
       ROUND(MEDIAN(a.inflow_volatility), 0)                  AS median_volatility,
       ROUND(MEDIAN(a.inflow_12m / 12), 0)                    AS median_monthly_inflow,
       ROUND(100.0 * AVG(CASE WHEN a.inflow_3m = 0 THEN 1 ELSE 0 END), 1) AS pct_zero_recent
FROM activity a JOIN labels l USING (split, account_id)
WHERE a.split = 'train'
GROUP BY l.churn
ORDER BY l.churn
"""))
