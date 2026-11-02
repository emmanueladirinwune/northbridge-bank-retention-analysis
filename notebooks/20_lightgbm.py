import duckdb
import numpy as np
import lightgbm as lgb
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


def scores(y, p):
    top = np.argsort(-p)[: int(0.2 * len(p))]
    return (average_precision_score(y, p), roc_auc_score(y, p), y[top].sum() / y.sum())


# Model 1: the logistic regression baseline (same as before)
logreg = make_pipeline(StandardScaler(),
                       LogisticRegression(class_weight="balanced", max_iter=1000))
logreg.fit(train[features], train["bad"])

# Model 2: LightGBM, kept deliberately small because we only have 328 training loans.
# Shallow trees (num_leaves=7) and min_child_samples=10 stop it memorising the training set.
lgbm = lgb.LGBMClassifier(n_estimators=200, learning_rate=0.05, num_leaves=7,
                          min_child_samples=10, subsample=0.8, subsample_freq=1,
                          colsample_bytree=0.8, class_weight="balanced",
                          random_state=42, verbose=-1)
lgbm.fit(train[features], train["bad"])

hard_mask = (test["negative_share"] == 0).to_numpy()
y_all = test["bad"].to_numpy()

print(f"{'model':<22}{'set':<12}{'PR-AUC':>8}{'ROC-AUC':>9}{'top20%':>8}")
for name, m in [("logistic regression", logreg), ("LightGBM", lgbm)]:
    p = m.predict_proba(test[features])[:, 1]
    for label, mask in [("all test", np.ones_like(hard_mask)), ("hard cases", hard_mask)]:
        pr, roc, rec = scores(y_all[mask], p[mask])
        print(f"{name:<22}{label:<12}{pr:>8.3f}{roc:>9.3f}{rec:>8.2f}")
