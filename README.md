# Datasets

## employees.csv — answer key

Small, hand-made dataset with **known** quality problems, so tool/model outputs can be checked against ground truth.

- **23 rows**, 7 columns, **20 unique** `employee_id`s

### Missing values (10 cells total)

| Column       | Missing | Affected `employee_id`s |
|--------------|---------|-------------------------|
| `department` | 2       | 7, 17                   |
| `age`        | 2       | 3, 13                   |
| `salary`     | 3       | 5, 11, 19               |
| `start_date` | 1       | 9                       |
| `email`      | 2       | 4, 11                   |
| `employee_id`, `name` | 0 | –                    |

### Duplicate IDs (3 IDs, 3 extra rows)

| `employee_id` | Kind | Notes |
|---------------|------|-------|
| 6  | Exact duplicate row | identical to the first occurrence |
| 12 | Exact duplicate row | identical to the first occurrence |
| 8  | **Conflicting** duplicate | same ID, different spelling of name/email, age 35 vs 36, salary 68000 vs 69000 |

So `df.duplicated().sum()` gives **2** (full-row duplicates), but
`df["employee_id"].duplicated().sum()` gives **3** (duplicate IDs). That difference is a good test of whether the quality tool checks the right thing.
