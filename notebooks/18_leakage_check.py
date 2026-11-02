import duckdb
con = duckdb.connect("northbridge.duckdb")

# Check 1: loan repayments ('UVER') should never appear BEFORE a loan month.
# If they do, our features could be seeing the loan itself.
print(con.sql("""
SELECT COUNT(*) AS uver_before_loan
FROM trans t JOIN loans l USING (account_id)
WHERE TRIM(COALESCE(t.k_symbol, '')) = 'UVER'
  AND t.dt < date_trunc('month', l.granted)
""").df().to_string(index=False))

# Check 2: how good is ONE feature on its own? If a single feature nearly
# solves the problem, it deserves a hard look.
print(con.sql("""
SELECT CASE WHEN negative_share > 0 THEN 'went negative' ELSE 'never negative' END AS group_,
       COUNT(*) AS loans,
       SUM(bad) AS bad,
       ROUND(100.0 * AVG(bad), 1) AS bad_pct
FROM model_table
WHERE split = 'test'
GROUP BY group_
""").df().to_string(index=False))
