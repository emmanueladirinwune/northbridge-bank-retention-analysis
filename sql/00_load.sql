-- Load the raw Berka files into DuckDB tables with proper dates.
-- Berka dates are stored as YYMMDD (e.g. 930101 = 1 Jan 1993).

CREATE OR REPLACE TABLE trans AS
SELECT *, strptime(CAST(date AS VARCHAR), '%y%m%d')::DATE AS dt
FROM read_csv('data/raw/trans.csv', delim = ';', header = true);

CREATE OR REPLACE TABLE account AS
SELECT account_id::INT AS account_id, frequency,
       strptime(date, '%y%m%d')::DATE AS opened
FROM read_csv('data/raw/account.csv', delim = ';', header = true, all_varchar = true);

CREATE OR REPLACE TABLE disp AS
SELECT disp_id::INT AS disp_id, client_id::INT AS client_id,
       account_id::INT AS account_id, type
FROM read_csv('data/raw/disp.csv', delim = ';', header = true, all_varchar = true);

-- birth_number is YYMMDD; women have 50 added to the month
CREATE OR REPLACE TABLE client AS
SELECT client_id::INT AS client_id,
       make_date(1900 + SUBSTR(birth_number, 1, 2)::INT,
                 SUBSTR(birth_number, 3, 2)::INT % 50,
                 SUBSTR(birth_number, 5, 2)::INT) AS birth,
       CASE WHEN SUBSTR(birth_number, 3, 2)::INT > 50 THEN 'F' ELSE 'M' END AS gender
FROM read_csv('data/raw/client.csv', delim = ';', header = true, all_varchar = true);

CREATE OR REPLACE TABLE card AS
SELECT disp_id::INT AS disp_id,
       strptime(LEFT(issued, 6), '%y%m%d')::DATE AS issued
FROM read_csv('data/raw/card.csv', delim = ';', header = true, all_varchar = true);

CREATE OR REPLACE TABLE loan AS
SELECT loan_id::INT AS loan_id,
       account_id::INT AS account_id,
       strptime(date, '%y%m%d')::DATE AS granted,
       amount::DOUBLE AS amount,
       duration::INT AS duration,
       payments::DOUBLE AS payments,
       status
FROM read_csv('data/raw/loan.csv', delim = ';', header = true, all_varchar = true);

