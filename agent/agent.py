from dotenv import load_dotenv
from groq import Groq

from harness import PROJECT_DIR, run_agent, save_trace

MODEL = "openai/gpt-oss-120b"

load_dotenv(PROJECT_DIR / ".env")
client = Groq()

instructions = (
    "You answer questions about CSV datasets. "
    "Use the tools to get the facts and do not guess. "
    "If no dataset is named, call list_datasets first."
)

questions = {
    "Q1": "Which columns in employees.csv have missing values, and how many?",
    "Q2": "Are there duplicate employee IDs in employees.csv?",
    "Q3": "What columns and data types does employees.csv have?",
    "Q4": "Is the data clean enough to analyse salaries?",
    "Q5": "Check the quality of customers.csv.",
}

for question_id, question in questions.items():
    trace = run_agent(client, MODEL, instructions, question)
    save_trace(trace, question_id)

    print("=" * 60)
    print(question_id + ": " + question)
    for step in trace["steps"]:
        print("  tool: " + step["tool"] + " " + str(step["arguments"]))
    print("Answer: " + str(trace["answer"]))
