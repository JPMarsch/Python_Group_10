"""
G10 - The three tools for the agent.

The functions are the same as in fixed_workflow.py.
Below them are the tool descriptions. The model never sees our code,
it only reads these descriptions to decide which tool to use.
"""

from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


# =====================================================================
# PART 1: Tools
# =====================================================================

def list_datasets():
    # Return the names of all CSV files in the data folder
    names = []
    for file in DATA_DIR.glob("*.csv"):
        names.append(file.name)
    return names


def inspect_schema(dataset):
    # Number of rows, column names and data types
    table = pd.read_csv(DATA_DIR / dataset)

    text = "Rows: " + str(len(table)) + "\n"
    text = text + "Columns:\n"
    for column in table.columns:
        data_type = str(table[column].dtype)
        text = text + "  " + column + " (" + data_type + ")\n"
    return text


def check_quality(dataset):
    # Count missing values per column and duplicate IDs
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
# PART 2: Tool descriptions (what the model sees)
# =====================================================================

tool_descriptions = [
    {
        "type": "function",
        "function": {
            "name": "list_datasets",
            "description": "Shows which CSV files we have.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "inspect_schema",
            "description": "Shows the columns of a dataset, their data types and how many rows it has.",
            "parameters": {
                "type": "object",
                "properties": {
                    "dataset": {"type": "string", "description": "The file name, for example employees.csv"},
                },
                "required": ["dataset"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_quality",
            "description": "Checks a dataset for missing values and duplicate employee IDs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "dataset": {"type": "string", "description": "The file name, for example employees.csv"},
                },
                "required": ["dataset"],
            },
        },
    },
]
