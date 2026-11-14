"""G10 - Fixed Python workflow (baseline, no AI model).

Every question goes through the same three steps, always in the same order:
    1. list_datasets   - does the dataset exist?
    2. inspect_schema  - which columns and types?
    3. check_quality   - missing values and duplicate IDs?
"""
import re
import time
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


# ---------- the three steps ----------

def list_datasets():
    return [f.name for f in DATA_DIR.glob("*.csv")]


def inspect_schema(dataset):
    df = pd.read_csv(DATA_DIR / dataset)
    columns = [f"{col} ({df[col].dtype})" for col in df.columns]
    return f"{len(df)} rows. Columns: {', '.join(columns)}"


def check_quality(dataset):
    df = pd.read_csv(DATA_DIR / dataset)
    lines = []

    for col, n in df.isna().sum().items():
        if n > 0:
            lines.append(f"Missing {col}: {n}")

    for emp_id, rows in df[df["employee_id"].duplicated(keep=False)].groupby("employee_id"):
        kind = "exact copy" if len(rows.drop_duplicates()) == 1 else "conflicting data"
        lines.append(f"Duplicate ID {emp_id}: {len(rows)}x, {kind}")

    return "\n".join(lines)


# ---------- the fixed workflow ----------

def fixed_workflow(question):
    match = re.search(r"\w+\.csv", question)            # find "<name>.csv" in the question
    if not match:
        return "ERROR: no dataset named in the question.", 0

    dataset = match.group()
    available = list_datasets()
    if dataset not in available:
        return f"ERROR: {dataset} not found. Available: {', '.join(available)}", 1

    report = inspect_schema(dataset) + "\n" + check_quality(dataset)
    return report, 3                                     # report, number of steps used


# ---------- evaluation ----------
# Each question with the facts a correct answer must contain (the known errors in the CSV).

QUESTIONS = [
    ("Q1", "Which columns in employees.csv have missing values, and how many?",
     ["Missing department: 2", "Missing age: 2", "Missing salary: 3",
      "Missing start_date: 1", "Missing email: 2"]),
    ("Q2", "Are there duplicate employee IDs in employees.csv?",
     ["Duplicate ID 6", "Duplicate ID 8", "Duplicate ID 12", "conflicting data"]),
    ("Q3", "What columns and data types does employees.csv have?",
     ["employee_id", "name", "department", "age", "salary", "start_date", "email"]),
    ("Q4", "Is the data clean enough to analyse salaries?",            # no dataset named
     ["Missing salary: 3", "Duplicate ID"]),
    ("Q5", "Check the quality of customers.csv.",                      # dataset does not exist
     ["customers.csv not found"]),
]

print("| Question | Success | Facts found | Steps | Runtime (ms) |")
print("|---|---|---|---|---|")
for qid, question, facts in QUESTIONS:
    start = time.perf_counter()
    report, steps = fixed_workflow(question)
    ms = (time.perf_counter() - start) * 1000

    found = sum(fact in report for fact in facts)
    success = "yes" if found == len(facts) else "no"
    print(f"| {qid} | {success} | {found}/{len(facts)} | {steps} | {ms:.1f} |")
