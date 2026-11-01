import duckdb
con = duckdb.connect("northbridge.duckdb")
con.execute(open("sql/05_loan_monthly.sql").read())

# The loans we study
print(con.sql("""
SELECT split, COUNT(*) AS loans, SUM(bad) AS bad, ROUND(100.0 * AVG(bad), 1) AS bad_pct
FROM loans GROUP BY split ORDER BY split DESC
"""))

# How many months of history each loan has (should range from about 3 to 12)
print(con.sql("""
SELECT months_history, COUNT(*) AS loans
FROM (SELECT loan_id, COUNT(*) AS months_history FROM loan_monthly GROUP BY loan_id)
GROUP BY months_history ORDER BY months_history
"""))
