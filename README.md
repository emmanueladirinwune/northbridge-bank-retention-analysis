# Northbridge Bank Retention Analysis

Early warning for customers heading into loan repayment difficulty, built on real anonymised bank data, with an explainable model and (in progress) grounded LLM outreach.

> **Note:** Northbridge Bank is a fictional bank. Customer, transaction and loan data are real anonymised records from the Berka dataset (PKDD'99, a Czech bank, 1993 to 1998). Product sheets used by the LLM layer are fictional and written for this project.

## Key results

- On loans granted in 1997 (held out, never seen in training), the model ranks borrowers so that **the riskiest 20% contain 85% of the customers who later defaulted** (random: 20%).
- **PR-AUC 0.856, 95% CI [0.72, 0.94]**, against 0.133 for random guessing.
- Logistic regression **beat LightGBM** by 0.10 PR-AUC (95% CI [0.01, 0.23]), so the simpler, more explainable model was kept.
- On customers who were **never overdrawn** (the hard cases no simple rule can flag), the model still reached **88% of future defaults in the top 20%**.

## Research questions

1. Can up to 12 months of transaction behaviour before a loan identify customers who will fall into repayment difficulty, using only information available when the loan is granted?
2. Does grounding an LLM in the bank's support-product documents reduce unsupported claims in outreach messages, compared with the same LLM without retrieval? *(in progress)*

## Data and design

| Item | Detail |
|---|---|
| Source | Berka dataset: 4,500 accounts, 1,056,320 transactions, 682 loans |
| Target | Loan status B (finished, unpaid) or D (running, in arrears) = bad |
| Train | Loans granted 1993 to 1996: 328 loans, 46 bad (14.0%) |
| Test | Loans granted 1997: 196 loans, 26 bad (13.3%) |
| Excluded | 158 loans granted in 1998: too recent to have an outcome (censored; bad rate only 2.5%) |
| Features | 19 per loan, built in SQL from up to 12 months **strictly before** the loan month |

**Leakage controls:** features use only transactions before the loan month; a check confirmed **zero** loan repayment transactions appear before any loan month; train and test are split by time, not at random.

## Method

1. **SQL feature layer (DuckDB):** zero-filled monthly grid per loan (`generate_series` + `LEFT JOIN`), window functions (`AVG() OVER`, `LAG`, `ROW_NUMBER`) for trends, and per-loan aggregates: income irregularity, spending swings, overspend share, balance levels, negative-balance share, payment-to-income ratio.
2. **Models:** logistic regression baseline vs LightGBM, kept small (7 leaves) because of the sample size.
3. **Evaluation:** PR-AUC, ROC-AUC and recall in the top 20%; paired bootstrap (2,000 resamples) for 95% intervals.
4. **Calibration:** class-weighted vs unweighted logistic regression.
5. **Explainability:** SHAP (exact for linear models), global and per customer.
6. **Fairness:** error rates by gender and age band (neither is a model input).

## Results

### Model comparison (1997 test loans)

| Model | PR-AUC | ROC-AUC | Recall in top 20% |
|---|---|---|---|
| Logistic regression | **0.850** | **0.960** | **0.85** |
| LightGBM | 0.741 | 0.920 | 0.73 |
| Random guessing | 0.133 | 0.500 | 0.20 |

Bootstrap 95% intervals: logistic regression 0.856 [0.721, 0.943], LightGBM 0.751 [0.581, 0.875]. Logistic regression won in 98% of resamples.

### The negative-balance signal, and the hard cases

Every 1997 borrower whose balance went negative in the year before the loan defaulted (10 of 10). This single rule explains part of the headline score, so the model was also tested on the 186 borrowers who were never overdrawn (16 bad, base rate 8.6%):

| Model | PR-AUC | ROC-AUC | Recall in top 20% |
|---|---|---|---|
| Logistic regression | **0.659** | **0.936** | **0.88** |
| LightGBM | 0.429 | 0.872 | 0.75 |

The difference here is likely but not proven (95% CI [-0.01, 0.42]; logistic regression won in 97% of resamples).

### Calibration: final model choice

| Version | Mean predicted risk | Actual rate | Brier score | PR-AUC |
|---|---|---|---|---|
| Class-weighted | 0.366 | 0.133 | 0.123 | 0.850 |
| **Unweighted (final)** | **0.163** | **0.133** | **0.051** | **0.830** |

Class weighting helped ranking slightly but inflated predicted risk almost threefold. The **unweighted model was chosen**: its probabilities can be used as stated (top band predicted 55%, actual 59%), at a cost in PR-AUC that is well within bootstrap noise.

### What drives risk (SHAP)

Strongest drivers across test loans: **average balance, share of time with a negative balance, and average monthly spending**, followed by transaction activity, lowest balance relative to the loan payment, and income irregularity. Each flagged customer gets their own top reasons, which feed the outreach layer.

Note: SHAP values are in log-odds. A few heavily overdrawn customers receive scores near 1.00, which means "far riskier than everyone else" rather than literal certainty.

### Fairness check (unweighted model, top 20% flagged)

| Group | Actual bad rate | Mean predicted | Flagged | Bad loans caught |
|---|---|---|---|---|
| Women | 14.7% | 17.7% | 21.6% | 12 of 15 |
| Men | 11.7% | 14.7% | 19.1% | 11 of 11 |
| Under 35 | 13.8% | 15.6% | 20.0% | 9 of 11 |
| 35 to 49 | 15.1% | 17.7% | 21.9% | 10 of 11 |
| 50 and over | 9.3% | 15.2% | 18.6% | 4 of 4 |

Prediction error is similar for women and men; the recall gap is 3 customers, too few to separate bias from chance. The model **overestimates risk for customers aged 50 and over**. Here a flag triggers a supportive contact rather than a credit decision, so the harm is an unnecessary message; in a lending decision this bias would need correcting before use.

## What did not work (and why it mattered)

The project began as a **churn** study. Three churn labels were tested and rejected:

| Label | Churn rate | Problem |
|---|---|---|
| 6 months with no activity | 0.1% | Customers almost never fully abandon accounts |
| 50% drop in transaction count | 3.1% | Standing orders keep counts steady even when customers leave |
| 50% drop in income | 5.3% | Driven by irregular income: "churners" had income variation 0.69 to 1.45 vs 0.18 for stayers, so the label measured lumpy income, not leaving |

Restricting to regular earners left 2.8% churn, too little signal. The target was switched to loan difficulty, a real recorded outcome that needs no constructed definition. The project's goal, helping a bank keep customers by reaching them early, stays the same.

## Limitations

- **Small sample:** 26 bad loans in the test set, hence wide confidence intervals.
- **Old, non-UK data:** Czech banking in the 1990s. The method transfers; the specific coefficients do not.
- **Observational:** the model predicts difficulty; it does not show that outreach prevents it. That would need a controlled trial.
- **Censoring:** 1998 loans were excluded because their outcomes are not yet known.

## Project structure

```
sql/          feature pipeline (run in numbered order)
notebooks/    analysis and modelling scripts (run in numbered order)
data/raw/     Berka CSV files (not included; download from Kaggle)
```

## How to run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# place the 8 Berka CSV files in data/raw/
python notebooks/05_check_tables.py   # loads all tables
# then run notebooks 10 to 24 in order
```

## Status

- Push 1 (data, features, model, evaluation): complete
- Push 2 (LLM outreach with retrieval ablation and human review queue): in progress

## Author

Emmanuel Adirinwune, MSc Data Science and Analytics (Distinction), University of Hertfordshire
