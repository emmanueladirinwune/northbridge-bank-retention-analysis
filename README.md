# Northbridge Bank Retention Analysis

Leakage-controlled churn prediction and grounded LLM outreach for retail banking.

> **Note:** Northbridge Bank is a fictional bank. Customer and transaction data are
> real anonymised records from the Berka dataset (PKDD'99). Product sheets used by
> the LLM layer are fictional and written for this project.

## Research questions
1. Can 12 months of transaction behaviour predict which customers will become
   inactive in the next 6 months, using only information available at prediction time?
2. Does grounding an LLM in the bank's product documents reduce unsupported claims
   in retention messages, compared with the same LLM without retrieval?

## Data
Berka dataset: about 4,500 accounts and 1 million transactions from a Czech bank,
1993 to 1998. Raw files are not stored in this repository.

## Method (planned)
- Churn defined as 6 months with no customer-initiated transactions
  (bank-generated entries such as interest are excluded)
- Time-based train and test windows to prevent leakage
- SQL feature layer in DuckDB (CTEs, window functions)
- Logistic regression baseline vs LightGBM, judged on PR-AUC, top-decile recall and calibration
- SHAP explanations per customer, plus a fairness check across gender and age groups
- Two-arm ablation: LLM messages with vs without retrieval, scored for unsupported claims
- Human review queue: drafts are never sent automatically

## Status
In progress. Results will be added as each stage is completed.

## Author
Emmanuel Adirinwune, MSc Data Science and Analytics, University of Hertfordshire
