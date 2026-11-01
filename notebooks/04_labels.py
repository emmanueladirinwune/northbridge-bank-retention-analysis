import duckdb
con = duckdb.connect("northbridge.duckdb")
con.sql(open("sql/01_labels.sql").read())
print(con.sql("""
SELECT split, COUNT(*) AS n, ROUND(100.0 * AVG(churn), 1) AS churn_pct
FROM labels
GROUP BY split
"""))
