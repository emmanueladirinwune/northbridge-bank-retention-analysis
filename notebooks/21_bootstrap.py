import duckdb
import numpy as np
import lightgbm as lgb
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import average_precision_score

con = duckdb.connect("northbridge.duckdb")
df = con.sql("SELECT * FROM model_table").df()
df["inflow_trend"] = df["inflow_trend"].fillna(1.0)

features = [c for c in df.columns if c not in ("loan_id", "split", "bad")]
train = df[df["split"] == "train"]
test = df[df["split"] == "test"]

# The same two models as 20_lightgbm.py
logreg = make_pipeline(StandardScaler(),
                       LogisticRegression(class_weight="balanced", max_iter=1000))
logreg.fit(train[features], train["bad"])
lgbm = lgb.LGBMClassifier(n_estimators=200, learning_rate=0.05, num_leaves=7,
                          min_child_samples=10, subsample=0.8, subsample_freq=1,
                          colsample_bytree=0.8, class_weight="balanced",
                          random_state=42, verbose=-1)
lgbm.fit(train[features], train["bad"])

y = test["bad"].to_numpy()
p_lr = logreg.predict_proba(test[features])[:, 1]
p_gb = lgbm.predict_proba(test[features])[:, 1]
hard = (test["negative_share"] == 0).to_numpy()

# Bootstrap: redraw the test set 2,000 times WITH replacement and re-score.
# Both models are scored on the SAME redraw each time ("paired"),
# so the difference between them is a fair comparison.
rng = np.random.default_rng(42)


def bootstrap(mask):
    idx_all = np.flatnonzero(mask)
    lr, gb = [], []
    for _ in range(2000):
        idx = rng.choice(idx_all, size=len(idx_all), replace=True)
        if y[idx].sum() == 0:        # a redraw with no bad loans can't be scored
            continue
        lr.append(average_precision_score(y[idx], p_lr[idx]))
        gb.append(average_precision_score(y[idx], p_gb[idx]))
    lr, gb = np.array(lr), np.array(gb)
    return lr, gb, lr - gb


def ci(a):
    lo, hi = np.percentile(a, [2.5, 97.5])
    return f"{np.median(a):.3f}  [{lo:.3f}, {hi:.3f}]"


for label, mask in [("all test", np.ones_like(hard)), ("hard cases", hard)]:
    lr, gb, diff = bootstrap(mask)
    print(f"\n{label}  (PR-AUC, median and 95% interval)")
    print(f"  logistic regression   {ci(lr)}")
    print(f"  LightGBM              {ci(gb)}")
    print(f"  difference (LR - GB)  {ci(diff)}")
    print(f"  share of redraws where LR wins: {(diff > 0).mean():.0%}")
