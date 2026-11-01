import duckdb
con = duckdb.connect("northbridge.duckdb")

print(con.sql("""
WITH cust AS (
  SELECT * FROM trans
  WHERE TRIM(COALESCE(k_symbol, '')) NOT IN ('UROK', 'SLUZBY', 'SANKC. UROK')
),
counts AS (
  SELECT account_id,
         COUNT(*) FILTER (WHERE dt BETWEEN '1997-07-01' AND '1997-12-31') AS before_n,
         COUNT(*) FILTER (WHERE dt BETWEEN '1998-01-01' AND '1998-06-30') AS after_n
  FROM cust
  GROUP BY account_id
)
SELECT COUNT(*) AS customers,
       ROUND(100.0 * AVG(CASE WHEN after_n <= 0.7 * before_n THEN 1 ELSE 0 END), 1) AS drop_30,
       ROUND(100.0 * AVG(CASE WHEN after_n <= 0.5 * before_n THEN 1 ELSE 0 END), 1) AS drop_50,
       ROUND(100.0 * AVG(CASE WHEN after_n <= 0.3 * before_n THEN 1 ELSE 0 END), 1) AS drop_70
FROM counts
WHERE before_n >= 6
"""))
