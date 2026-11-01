import duckdb

# Open our database file
con = duckdb.connect("northbridge.duckdb")

# Read 00_load.sql and run every statement in it
con.execute(open("sql/00_load.sql").read())

# Count the rows in each table to check everything loaded
for table in ["trans", "account", "disp", "client", "card", "loan"]:
    n = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(table, n)
