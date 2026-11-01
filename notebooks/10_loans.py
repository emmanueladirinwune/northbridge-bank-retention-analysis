import duckdb
con = duckdb.connect("northbridge.duckdb")
con.execute(open("sql/00_load.sql").read())

# How many loans in each outcome?
print(con.sql("""
SELECT status,
       CASE status WHEN 'A' THEN 'finished, repaid'
                   WHEN 'B' THEN 'finished, NOT repaid'
                   WHEN 'C' THEN 'running, on track'
                   WHEN 'D' THEN 'running, in arrears' END AS meaning,
       COUNT(*) AS loans
FROM loan
GROUP BY status
ORDER BY status
"""))

# When were loans granted, and how many went bad each year?
print(con.sql("""
SELECT YEAR(granted) AS year,
       COUNT(*) AS loans,
       SUM(CASE WHEN status IN ('B', 'D') THEN 1 ELSE 0 END) AS bad,
       ROUND(100.0 * AVG(CASE WHEN status IN ('B', 'D') THEN 1 ELSE 0 END), 1) AS bad_pct
FROM loan
GROUP BY year
ORDER BY year
"""))
