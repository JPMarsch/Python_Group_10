"""
G10 - Fixed Python workflow (baseline, no AI model).

Every question goes through the same three steps, always in the same order:
    1. list_datasets   - does the dataset exist?
    2. inspect_schema  - which columns and data types?
    3. check_quality   - missing values and duplicate IDs?

Afterwards, each report is checked against the correct answer counted by hand.
"""

import time
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


# =====================================================================
# PART 1: 3-Step Check
# =====================================================================

def list_datasets():
    # Return the names of all CSV files in the data folder
    names = []
    for file in DATA_DIR.glob("*.csv"):
        names.append(file.name)
    return names


def inspect_schema(dataset):
    # number of rows, column names and data types
    table = pd.read_csv(DATA_DIR / dataset)

    text = "Rows: " + str(len(table)) + "\n"
    text = text + "Columns:\n"
    for column in table.columns:
        data_type = str(table[column].dtype)
        text = text + "  " + column + " (" + data_type + ")\n"
    return text


def check_quality(dataset):
    # Count missing values per column or duplicate IDs
    table = pd.read_csv(DATA_DIR / dataset)
    text = ""

    # --- Missing values ---
    for column in table.columns:
        number_missing = table[column].isna().sum()
        if number_missing > 0:
            text = text + "Missing " + column + ": " + str(number_missing) + "\n"

    # --- Duplicate IDs ---
    id_counts = table["employee_id"].value_counts()
    for employee_id in sorted(id_counts.index):
        count = id_counts[employee_id]
        if count > 1:
            rows_with_this_id = table[table["employee_id"] == employee_id]
            different_rows = rows_with_this_id.drop_duplicates()
            if len(different_rows) == 1:
                kind = "exact copy"
            else:
                kind = "conflicting data"
            text = text + "Duplicate ID " + str(employee_id) + ": " + str(count) + "x, " + kind + "\n"

    return text


# =====================================================================
# PART 2: Fixed Workflow
# =====================================================================

def find_dataset_name(question):
    # Return the first word in the question that ends with '.csv', or None."
    for word in question.split():
        word = word.strip(".,?!")          # remove punctuation, e.g. "customers.csv." -> "customers.csv"
        if word.endswith(".csv"):
            return word
    return None


def fixed_workflow(question):

    # Look for a file name in the question.
    dataset = find_dataset_name(question)
    if dataset is None:
        report = "ERROR: no dataset named in the question."
        return report, 0

    # Step 1: does the dataset exist?
    available = list_datasets()
    if dataset not in available:
        report = "ERROR: " + dataset + " not found. Available: " + ", ".join(available)
        return report, 1

    # Step 2 and step 3: always both, whatever the question asked.
    report = inspect_schema(dataset) + check_quality(dataset)
    return report, 3


# =====================================================================
# PART 3: Question + Answer key
# =====================================================================

questions = [
    {
        "id": "Q1",
        "question": "Which columns in employees.csv have missing values, and how many?",
        "expected_facts": ["Missing department: 2", "Missing age: 2", "Missing salary: 3",
                           "Missing start_date: 1", "Missing email: 2"],
    },
    {
        "id": "Q2",
        "question": "Are there duplicate employee IDs in employees.csv?",
        "expected_facts": ["Duplicate ID 6", "Duplicate ID 8", "Duplicate ID 12", "conflicting data"],
    },
    {
        "id": "Q3",
        "question": "What columns and data types does employees.csv have?",
        "expected_facts": ["employee_id", "name", "department", "age", "salary", "start_date", "email"],
    },
    {
        "id": "Q4",
        "question": "Is the data clean enough to analyse salaries?",   # no dataset named
        "expected_facts": ["Missing salary: 3", "Duplicate ID"],
    },
    {
        "id": "Q5",
        "question": "Check the quality of customers.csv.",             # dataset does not exist
        "expected_facts": ["customers.csv not found"],
    },
]


# =====================================================================
# PART 4: Run each question and check report
# =====================================================================

results = []

for q in questions:
    print("=" * 60)
    print(q["id"] + ": " + q["question"])

    # Measure time per workflow 
    start = time.perf_counter()
    report, steps = fixed_workflow(q["question"])
    runtime_ms = (time.perf_counter() - start) * 1000

    print("--- Report ---")
    print(report)

    # Check every expected fact of the current question
    print("--- Check against answer key ---")
    found = 0
    for fact in q["expected_facts"]:
        if fact in report:
            print("  found:     " + fact)
            found = found + 1
        else:
            print("  NOT found: " + fact)

    total = len(q["expected_facts"])
    if found == total:
        success = "yes"
    else:
        success = "no"

    results.append([q["id"], success, str(found) + "/" + str(total), str(steps), f"{runtime_ms:.1f}"])


# Print the summary table.
print("=" * 60)
print("| Question | Success | Facts found | Steps | Runtime (ms) |")
print("|---|---|---|---|---|")
for row in results:
    print("| " + " | ".join(row) + " |")