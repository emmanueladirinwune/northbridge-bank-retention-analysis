import duckdb
con = duckdb.connect("northbridge.duckdb")

# The label changed, so rebuild everything that depends on it, in order
for path in ["sql/01_labels.sql", "sql/02_monthly.sql",
             "sql/03_trends.sql", "sql/04_activity.sql"]:
    con.execute(open(path).read())
    print("ran", path)

# New churn rates
print(con.sql("""
SELECT split, COUNT(*) AS n, ROUND(100.0 * AVG(churn), 1) AS churn_pct
FROM labels GROUP BY split ORDER BY split DESC
"""))

# Repeat the check: are churners still mostly high-volatility customers?
print(con.sql("""
SELECT l.churn,
       COUNT(*) AS customers,
       ROUND(MEDIAN(a.inflow_trend), 2)      AS median_trend,
       ROUND(MEDIAN(a.inflow_volatility), 0) AS median_volatility,
       ROUND(MEDIAN(a.inflow_12m / 12), 0)   AS median_monthly_inflow,
       ROUND(AVG(a.falling_months_6m), 2)    AS avg_falling_months
FROM activity a JOIN labels l USING (split, account_id)
WHERE a.split = 'train'
GROUP BY l.churn ORDER BY l.churn
"""))


print(con.sql("""
WITH x AS (
  SELECT l.churn,
         a.inflow_volatility / NULLIF(a.inflow_12m / 12, 0) AS cv,
         NTILE(4) OVER (ORDER BY a.inflow_12m) AS income_quartile
  FROM activity a JOIN labels l USING (split, account_id)
  WHERE a.split = 'train'
)
SELECT income_quartile,
       COUNT(*) AS customers,
       ROUND(100.0 * AVG(churn), 1) AS churn_pct,
       ROUND(MEDIAN(cv) FILTER (WHERE churn = 0), 2) AS cv_stayed,
       ROUND(MEDIAN(cv) FILTER (WHERE churn = 1), 2) AS cv_churned
FROM x
GROUP BY income_quartile
ORDER BY income_quartile
"""))
