import duckdb
con = duckdb.connect("northbridge.duckdb")

print(con.sql("""
WITH p AS (
  SELECT account_id,
    SUM(amount) FILTER (WHERE type = 'PRIJEM' AND TRIM(COALESCE(k_symbol,'')) <> 'UROK'
                        AND dt BETWEEN '1997-07-01' AND '1997-12-31') AS in_before,
    SUM(amount) FILTER (WHERE type = 'PRIJEM' AND TRIM(COALESCE(k_symbol,'')) <> 'UROK'
                        AND dt BETWEEN '1998-01-01' AND '1998-06-30') AS in_after,
    AVG(balance) FILTER (WHERE dt BETWEEN '1997-07-01' AND '1997-12-31') AS bal_before,
    AVG(balance) FILTER (WHERE dt BETWEEN '1998-01-01' AND '1998-06-30') AS bal_after
  FROM trans
  GROUP BY account_id
)
SELECT COUNT(*) AS customers,
  ROUND(100.0 * AVG(CASE WHEN COALESCE(in_after,0) <= 0.5 * in_before THEN 1 ELSE 0 END), 1) AS inflow_drop_50,
  ROUND(100.0 * AVG(CASE WHEN COALESCE(bal_after,0) <= 0.5 * bal_before THEN 1 ELSE 0 END), 1) AS balance_drop_50,
  ROUND(100.0 * AVG(CASE WHEN COALESCE(in_after,0) <= 0.5 * in_before
                          OR COALESCE(bal_after,0) <= 0.5 * bal_before THEN 1 ELSE 0 END), 1) AS either
FROM p
WHERE in_before > 0
"""))
