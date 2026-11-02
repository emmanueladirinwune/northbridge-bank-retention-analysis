import duckdb
import numpy as np
import pandas as pd
import shap
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

con = duckdb.connect("northbridge.duckdb")
df = con.sql("SELECT * FROM model_table").df()
df["inflow_trend"] = df["inflow_trend"].fillna(1.0)

features = [c for c in df.columns if c not in ("loan_id", "split", "bad")]
train = df[df["split"] == "train"]
test = df[df["split"] == "test"].reset_index(drop=True)

# Final model: unweighted logistic regression (best calibrated, see 22_calibration.py)
model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
model.fit(train[features], train["bad"])
scaler, clf = model[0], model[-1]

# SHAP explains each prediction as a sum of feature contributions.
# For a linear model this is exact: each feature's push = coefficient x (value - average).
X_train = scaler.transform(train[features])
X_test = scaler.transform(test[features])
masker = shap.maskers.Independent(X_train, max_samples=len(X_train))
explainer = shap.LinearExplainer(clf, masker)
# one row per test loan, one column per feature
sv = explainer.shap_values(X_test)

# 1. Global: which features matter most across all test loans?
importance = pd.Series(np.abs(sv).mean(
    axis=0), index=features).sort_values(ascending=False)
print("average impact on risk (mean |SHAP|), top 8:")
print(importance.head(8).round(3).to_string())

# 2. Local: the top 3 reasons for each of the 5 riskiest test customers.
#    This is what a relationship manager would see before contacting them.
test["risk"] = model.predict_proba(test[features])[:, 1]
print("\nreasons for the 5 highest-risk customers:")
for i in test["risk"].nlargest(5).index:
    reasons = pd.Series(sv[i], index=features).nlargest(3)
    text = ", ".join(f"{f} (+{v:.2f})" for f, v in reasons.items())
    print(f"  loan {test.loc[i, 'loan_id']:>5} | risk {test.loc[i, 'risk']:.2f} | "
          f"actually bad: {test.loc[i, 'bad']} | {text}")
