
# Transaction Automated ETL and Reconciliation Prototype

## Overview

This repository contains a Python-based prototype for **reconciling transactions** between two source systems (a company cashbook and, bank statements) and generating a **business-ready dashboard** to provide key insights.

## Problem STatement
The cashbook and bank statement can disagree due to timing differences and unrecorded bank entries. This project automates reconciliation by cleaning, standardizing, matching transactions, and reporting unmatched items.

## Dataset

Kaggle Dataset titled "Bank Reconciliation Statement"
https://www.kaggle.com/datasets/fozianazar/bank-reconciliation-statement

---

## Repository Structure

```
fund-recon/
├─ data/                   
│  ├─ 1.Bank Reconciliation Sample.xlsx
│  ├─ df_bs_remaining.csv 
│  ├─ df_cb_remaining.csv
│  ├─ df_cb_unified.csv
│  ├─ df_matched.csv    
│
├─ src/                   # Core Python modules
│  ├─ DataCleaner.py      # reusable data cleaning utilities
│  ├─ recon.py            # ETL + matching logic
│  └─ __int__.py    
│
├─ app/                    # Streamlit dashboard - quick insights for business users
│  └─ streamlit_app.py
│
├─ tests/                  # Unit tests - this is empty for now due to project time constraints
│  └─ test_normalizer.py
│
├─ requirements.txt
└─ README.md
```

## Pipeline Overview
1. Ingest raw data
2. Clean & standardize (dates, amounts, text)
3. Remove balances/totals (store opening balance separately)
4. Create unified cashbook dataframe (receipts/payments) + SIGNED_AMOUNT
5. Convert bank statement debit/credit to SIGNED_AMOUNT
6. Extract transaction numbers from descriptions (cheque/transaction number)
7. Matching strategy (rules)
    - based transaction number + signed amount 
    - since this was a limited data set, this rule was enough
    - in the future, I would build this out to be more robust
        - i.e. for outliers - does any combo of outliers (with similar/ same name) give the signed amount 
        - If bank statements had more info - we could also try to use fuzzy match to help with recon
6. Outputs 

## Results

##### Matched Transactions
found in df_matched.csv 
This table contains transactions that were successfully matched between the cashbook and the bank statement
based on amount, date, and reference. No further action required on these items.

##### Unmatched Cashbook Transactions
found in df_bs_remaining.csv 
This table shows cashbook transactions that are not yet appeared on the bank statement.
Typically **outstanding deposits** or **unpresented payments** and are expected to clear in a future period.

##### Unmatched Bank Statement Transactions
found in df_cb_remaining.csv
This table includes bank statement items that do not appear in the cashbook.
These usually require **journal entries** (e.g. bank charges, direct debits, or interest).

* You can also interact with these databases when you run the streamlit_app

## Setup Instructions

### 1. Open terminal in project folder

- open project folder in File Explorer
- hold shift + right click 
- Select "Open PowerShell window here"

### 2. Create and activate virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

pip install -r requirements.txt

### 4. Verify the required data files
data/
    1. Bank Reconciliation Sample
    df_cb_unified.csv
    df_matched.csv
    df_bs_remaining.csv
    df_cb_remaining.csv

## Running the Reconciliation

Run the reconciliation pipeline from the project root:

```bash
python src/recon.ipynb
```


## Streamlit Dashboard

From the PROJECT ROOT FOLDER run:

streamlit run app/streamlit_app.py

!!! Do not navigate into the app/ folder before running this command

#### If you are experiencing trouble with the streamlit app, you can navigate to additional where you will find a print out of the app


## Data Cleaning

All data cleaning logic is centralized in:

```
src/DataCleaner.py
```

This includes:

* Text normalization (names, labels)
* Numeric normalization (fees, rates)
* Date normalization
* Transaction Number Normalization

This ensures consistent matching across sources.

---

## Testing

Due to time constraints, I have not included unit testing, but in the future, you would run it with:

```bash
pytest
```

---

## Notes & Future Enhancements

* Input data in `data/` is **synthetic** and for demonstration only.
* Due to the simplicity of the dataset, we were abel to matched all possible rows on only one pass
* in real world, messy, data sets, I would add more matching logic based on fuzzy matching of details, date ranges, and combinations of signed amounts 
* In the future, all reconciliation logic should be in a .py file 
* Audit trail and change history
* Integration with cloud storage or APIs - orchestration to automate runs (i.e. prefect/ air flow etc.) at the end of every month 
