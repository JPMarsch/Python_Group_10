from dotenv import load_dotenv
from groq import Groq

from harness import PROJECT_DIR, run_agent, save_trace

MODEL = "openai/gpt-oss-120b"

load_dotenv(PROJECT_DIR / ".env")
client = Groq()

# True  = with the repair for Q6
# False = without the repair, Q6 fails and is saved as traces/Q6_Fail.json
REPAIR = True

instructions = (
    "You answer questions about CSV datasets. "
    "Use the tools to get the facts and do not guess. "
    "If no dataset is named, call list_datasets first."
)

# Repair for Q6: without it the agent only calls inspect_schema,
# reads "Rows: 23" and says 23 employees (correct: 20, because of duplicate IDs).
if REPAIR:
    instructions = instructions + (
        " Rows are not the same as unique records: before you count records, "
        "also call check_quality and take duplicate IDs into account."
    )

questions = {
    "Q1": "Which columns in employees.csv have missing values, and how many?",
    "Q2": "Are there duplicate employee IDs in employees.csv?",
    "Q3": "What columns and data types does employees.csv have?",
    "Q4": "Is the data clean enough to analyse salaries?",
    "Q5": "Check the quality of customers.csv.",
    "Q6": "How many employees are in employees.csv?",
}

for question_id, question in questions.items():
    trace = run_agent(client, MODEL, instructions, question)
    trace["repair"] = REPAIR

    if question_id == "Q6" and not REPAIR:
        question_id = "Q6_Fail"
    save_trace(trace, question_id)

    print("=" * 60)
    print(question_id + ": " + question)
    for step in trace["steps"]:
        print("  tool: " + step["tool"] + " " + str(step["arguments"]))
    print("Answer: " + str(trace["answer"]))
