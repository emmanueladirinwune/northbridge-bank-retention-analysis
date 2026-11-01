import duckdb
con = duckdb.connect("northbridge.duckdb")
con.execute(open("sql/07_loan_features.sql").read())

# Do bad loans look different before they were granted? (train only)
result = con.sql("""
SELECT bad,
       COUNT(*)                             AS loans,
       ROUND(MEDIAN(avg_inflow), 0)         AS avg_inflow,
       ROUND(MEDIAN(inflow_cv), 2)          AS inflow_cv,
       ROUND(MEDIAN(net_swing), 2)          AS net_swing,
       ROUND(MEDIAN(overspend_share), 2)    AS overspend_share,
       ROUND(MEDIAN(payment_to_income), 3)  AS payment_to_income,
       ROUND(MEDIAN(loan_amount), 0)        AS loan_amount
FROM loan_features
WHERE split = 'train'
GROUP BY bad
ORDER BY bad
""")

# .df() turns the result into a pandas table; .to_string() prints every column
print(result.df().to_string(index=False))
