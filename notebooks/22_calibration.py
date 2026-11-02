import duckdb
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import average_precision_score, brier_score_loss

con = duckdb.connect("northbridge.duckdb")
df = con.sql("SELECT * FROM model_table").df()
df["inflow_trend"] = df["inflow_trend"].fillna(1.0)

features = [c for c in df.columns if c not in ("loan_id", "split", "bad")]
train = df[df["split"] == "train"]
test = df[df["split"] == "test"]
y = test["bad"].to_numpy()

# Two versions of the same model:
#  "balanced" (what we used so far) up-weights bad loans so the model pays attention to them,
#  "unweighted" treats every loan equally, so its probabilities should be closer to reality.
models = {
    "balanced":   LogisticRegression(class_weight="balanced", max_iter=1000),
    "unweighted": LogisticRegression(max_iter=1000),
}

for name, clf in models.items():
    model = make_pipeline(StandardScaler(), clf).fit(
        train[features], train["bad"])
    p = model.predict_proba(test[features])[:, 1]

    # Group test loans into 5 bands by predicted risk, then compare
    # the average predicted risk with the share that actually went bad.
    bands = pd.qcut(p, 5, labels=["1 lowest", "2", "3", "4", "5 highest"])
    table = (pd.DataFrame({"band": bands, "predicted": p, "actual": y})
               .groupby("band", observed=True)
               .agg(loans=("actual", "size"),
                    avg_predicted=("predicted", "mean"),
                    actual_bad_rate=("actual", "mean"))
               .round(3))

    print(f"\n{name}:  PR-AUC {average_precision_score(y, p):.3f} | "
          f"Brier {brier_score_loss(y, p):.3f} (lower = better) | "
          f"mean predicted {p.mean():.3f} vs actual {y.mean():.3f}")
    print(table.to_string())
