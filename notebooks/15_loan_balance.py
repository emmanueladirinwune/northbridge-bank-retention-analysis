import duckdb
con = duckdb.connect("northbridge.duckdb")
con.execute(open("sql/08_loan_balance.sql").read())

# Every loan should have a row (expect 524)
print("loans with balance features:",
      con.execute("SELECT COUNT(*) FROM loan_balance").fetchall()[0][0])

# Do bad loans have weaker balances before the loan? (train only)
result = con.sql("""
SELECT l.bad,
       COUNT(*)                                       AS loans,
       ROUND(MEDIAN(b.min_balance), 0)                AS min_balance,
       ROUND(MEDIAN(b.avg_balance), 0)                AS avg_balance,
       ROUND(MEDIAN(b.min_balance_in_payments), 2)    AS min_bal_in_payments,
       ROUND(100.0 * AVG(CASE WHEN b.min_balance < 0 THEN 1 ELSE 0 END), 1) AS pct_ever_negative
FROM loan_balance b JOIN loans l USING (loan_id)
WHERE l.split = 'train'
GROUP BY l.bad
ORDER BY l.bad
""")
print(result.df().to_string(index=False))
