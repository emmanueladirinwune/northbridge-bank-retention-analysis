import duckdb
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

con = duckdb.connect("northbridge.duckdb")
df = con.sql("SELECT * FROM model_table").df()
df["inflow_trend"] = df["inflow_trend"].fillna(1.0)
features = [c for c in df.columns if c not in ("loan_id", "split", "bad")]

# Gender and age of the account OWNER at the loan date.
# These are NOT model inputs; we only use them to check the model treats groups fairly.
people = con.sql("""
SELECT l.loan_id,
       c.gender,
       FLOOR(date_diff('day', c.birth, l.granted) / 365.25) AS age
FROM loans l
JOIN disp d   ON d.account_id = l.account_id AND d.type = 'OWNER'
JOIN client c ON c.client_id = d.client_id
""").df()
people["age_band"] = pd.cut(people["age"], [0, 35, 50, 120], labels=[
                            "under 35", "35-49", "50+"])
df = df.merge(people, on="loan_id", how="left")

train = df[df["split"] == "train"]
test = df[df["split"] == "test"].copy()

# Final model (unweighted logistic regression)
model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
model.fit(train[features], train["bad"])
test["risk"] = model.predict_proba(test[features])[:, 1]

# The bank contacts the riskiest 20% of all test borrowers
cutoff = test["risk"].quantile(0.8)
test["flagged"] = (test["risk"] >= cutoff).astype(int)

for col in ["gender", "age_band"]:
    g = test.groupby(col, observed=True)
    table = pd.DataFrame({
        "loans": g.size(),
        "actual_bad_rate": g["bad"].mean(),
        "avg_predicted": g["risk"].mean(),
        "flagged_rate": g["flagged"].mean(),
        # of the customers who really went bad, what share did we flag?
        "recall": g.apply(lambda x: x.loc[x["bad"] == 1, "flagged"].mean()
                          if x["bad"].sum() else np.nan, include_groups=False),
        "bad_loans": g["bad"].sum(),
    }).round(3)
    print(f"\nby {col}:")
    print(table.to_string())
