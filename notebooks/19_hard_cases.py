import duckdb
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import average_precision_score, roc_auc_score

con = duckdb.connect("northbridge.duckdb")
df = con.sql("SELECT * FROM model_table").df()
df["inflow_trend"] = df["inflow_trend"].fillna(1.0)

features = [c for c in df.columns if c not in ("loan_id", "split", "bad")]
train = df[df["split"] == "train"]
test = df[df["split"] == "test"]

# Same model as 17_baseline.py
model = make_pipeline(StandardScaler(),
                      LogisticRegression(class_weight="balanced", max_iter=1000))
model.fit(train[features], train["bad"])
test = test.assign(p=model.predict_proba(test[features])[:, 1])

# The hard cases: borrowers whose balance never went negative.
# No simple rule flags them, so this is where the model has to earn its keep.
hard = test[test["negative_share"] == 0]
y, p = hard["bad"].to_numpy(), hard["p"].to_numpy()

top = np.argsort(-p)[: int(0.2 * len(p))]
print(
    f"hard cases: {len(y)} loans | bad: {y.sum()} | base rate: {y.mean():.3f}")
print(
    f"PR-AUC:  {average_precision_score(y, p):.3f}   (random guessing = {y.mean():.3f})")
print(f"ROC-AUC: {roc_auc_score(y, p):.3f}   (random guessing = 0.500)")
print(
    f"recall in top 20%: {y[top].sum() / y.sum():.2f}   (random guessing = 0.20)")
