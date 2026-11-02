import duckdb
con = duckdb.connect("northbridge.duckdb")
con.execute(open("sql/09_model_table.sql").read())

df = con.sql("SELECT * FROM model_table").df()

print("rows:", len(df), "| columns:", len(df.columns))
print(df.groupby("split")["bad"].agg(["count", "sum"]).to_string())

# Missing values per column: anything above 0 needs a decision before modelling
missing = df.isna().sum()
print("\ncolumns with missing values:")
print(missing[missing > 0].to_string() if missing.any() else "none")
