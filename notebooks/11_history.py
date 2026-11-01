import duckdb
con = duckdb.connect("northbridge.duckdb")

# How much transaction history does each customer have before their loan?
print(con.sql("""
SELECT YEAR(l.granted) AS year,
       COUNT(*) AS loans,
       MIN(date_diff('month', a.opened, l.granted)) AS min_months_history,
       ROUND(MEDIAN(date_diff('month', a.opened, l.granted)), 0) AS median_months_history,
       SUM(CASE WHEN date_diff('month', a.opened, l.granted) >= 12 THEN 1 ELSE 0 END) AS with_12m
FROM loan l JOIN account a USING (account_id)
GROUP BY year
ORDER BY year
"""))
