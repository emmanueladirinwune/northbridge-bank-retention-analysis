import duckdb
con = duckdb.connect("northbridge.duckdb")
con.execute(open("sql/03_trends.sql").read())

print(con.sql("""
SELECT month, inflow, inflow_roll_3m, inflow_mom, rn
FROM trended
WHERE account_id = 1 AND split = 'train'
ORDER BY month
"""))
