import duckdb
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import average_precision_score, roc_auc_score

con = duckdb.connect("northbridge.duckdb")
df = con.sql("SELECT * FROM model_table").df()

# inflow_trend is missing when history is too short to measure a trend.
# 1.0 means "no change", the neutral value.
df["inflow_trend"] = df["inflow_trend"].fillna(1.0)

features = [c for c in df.columns if c not in ("loan_id", "split", "bad")]
train = df[df["split"] == "train"]
test = df[df["split"] == "test"]

# Scale features, then fit. class_weight="balanced" stops the model ignoring the rare bad loans.
model = make_pipeline(StandardScaler(),
                      LogisticRegression(class_weight="balanced", max_iter=1000))
model.fit(train[features], train["bad"])

# Score the test loans (1997), which the model has never seen
p = model.predict_proba(test[features])[:, 1]
y = test["bad"].to_numpy()

# Recall in the top 20%: if the bank can only contact the riskiest 20% of borrowers,
# what share of the bad loans does it reach?
top = np.argsort(-p)[: int(0.2 * len(p))]
recall_top20 = y[top].sum() / y.sum()

print(f"test loans: {len(y)} | bad: {y.sum()} | base rate: {y.mean():.3f}")
print(
    f"PR-AUC:  {average_precision_score(y, p):.3f}   (random guessing = {y.mean():.3f})")
print(f"ROC-AUC: {roc_auc_score(y, p):.3f}   (random guessing = 0.500)")
print(f"recall in top 20%: {recall_top20:.2f}   (random guessing = 0.20)")

# Which features push risk up (+) or down (-)? Scaled, so sizes are comparable.
coefs = model[-1].coef_[0]
order = np.argsort(-np.abs(coefs))
print("\nstrongest features:")
for i in order[:8]:
    print(f"  {features[i]:<26} {coefs[i]:+.2f}")
