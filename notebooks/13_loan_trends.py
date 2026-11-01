import duckdb
con = duckdb.connect("northbridge.duckdb")
con.execute(open("sql/06_loan_trends.sql").read())

# One bad loan and one good loan, side by side, last 6 months before the loan
for label in [1, 0]:
    print("bad loan" if label else "good loan")
    print(con.sql(f"""
    SELECT month, inflow, outflow, net_outflow, inflow_mom, rn
    FROM loan_trended
    WHERE loan_id = (SELECT MIN(loan_id) FROM loans WHERE bad = {label})
      AND rn <= 6
    ORDER BY month
    """))
