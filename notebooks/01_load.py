import duckdb
con = duckdb.connect("northbridge.duckdb")

con.sql("""
CREATE OR REPLACE TABLE trans AS
SELECT *, strptime(CAST(date AS VARCHAR), '%y%m%d')::DATE AS dt
FROM read_csv('data/raw/trans.csv', delim=';', header=true)
""")

print(con.sql("""
WITH cust AS (
  SELECT * FROM trans
  WHERE TRIM(COALESCE(k_symbol, '')) NOT IN ('UROK', 'SLUZBY', 'SANKC. UROK')
),
eligible AS (
  SELECT DISTINCT account_id FROM cust
  WHERE dt BETWEEN '1997-10-01' AND '1997-12-31'
),
kept AS (
  SELECT DISTINCT account_id FROM cust
  WHERE dt BETWEEN '1998-01-01' AND '1998-06-30'
)
SELECT COUNT(*) AS customers,
       ROUND(100.0 * SUM(CASE WHEN k.account_id IS NULL THEN 1 ELSE 0 END) / COUNT(*), 1) AS churn_pct
FROM eligible e LEFT JOIN kept k USING (account_id)
"""))
