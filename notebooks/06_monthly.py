import duckdb
con = duckdb.connect("northbridge.duckdb")
con.execute(open("sql/02_monthly.sql").read())

# Show one customer's 12 months
print(con.sql("""
SELECT * FROM monthly
WHERE account_id = (SELECT MIN(account_id) FROM monthly) AND split = 'train'
ORDER BY month
"""))

# Every customer should have exactly 12 rows
print(con.sql("SELECT split, COUNT(*) AS rows, COUNT(DISTINCT account_id) AS customers FROM monthly GROUP BY split"))
