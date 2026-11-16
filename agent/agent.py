import json
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

from tools import check_quality, inspect_schema, list_datasets, tool_descriptions

PROJECT_DIR = Path(__file__).resolve().parent.parent
MODEL = "openai/gpt-oss-120b"

# Load GROQ_API_KEY from the .env file, Groq() then finds it automatically
load_dotenv(PROJECT_DIR / ".env")
client = Groq()

tools = {
    "list_datasets": list_datasets,
    "inspect_schema": inspect_schema,
    "check_quality": check_quality,
}

instructions = (
    "You answer questions about CSV datasets. "
    "Use the tools to get the facts and do not guess. "
    "If no dataset is named, call list_datasets first."
)


def run_tool(name, arguments):
    
    if name not in tools:
        return "ERROR: there is no tool called " + name
    
    if name == "list_datasets":
        return ", ".join(list_datasets())
    
    dataset = arguments.get("dataset")

    if dataset not in list_datasets():
        return "ERROR: " + str(dataset) + " not found. Available: " + ", ".join(list_datasets())
    
    return tools[name](dataset)


def run_agent(question):
    messages = [
        {"role": "system", "content": instructions},
        {"role": "user", "content": question},
    ]
    trace = {"question": question, "model": MODEL, "steps": []}

    for step in range(5):
        response = client.chat.completions.create(model=MODEL, messages=messages, tools=tool_descriptions)
        message = response.choices[0].message

        if not message.tool_calls:
            trace["answer"] = message.content
            return trace

        messages.append({
            "role": "assistant",
            "content": message.content or "",
            "tool_calls": [
                {"id": call.id, "type": "function",
                 "function": {"name": call.function.name, "arguments": call.function.arguments}}
                for call in message.tool_calls
            ],
        })
        for call in message.tool_calls:
            name = call.function.name
            arguments = json.loads(call.function.arguments or "{}")
            result = run_tool(name, arguments)

            trace["steps"].append({"tool": name, "arguments": arguments, "result": result})
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})

    trace["answer"] = "STOPPED: no answer after 5 rounds"
    return trace


def save_trace(trace, name):
    folder = PROJECT_DIR / "traces"
    folder.mkdir(exist_ok=True)
    with open(folder / (name + ".json"), "w") as file:
        json.dump(trace, file, indent=2)


# =====================================================================
# Run the five questions
# =====================================================================

questions = {
    "Q1": "Which columns in employees.csv have missing values, and how many?",
    "Q2": "Are there duplicate employee IDs in employees.csv?",
    "Q3": "What columns and data types does employees.csv have?",
    "Q4": "Is the data clean enough to analyse salaries?",
    "Q5": "Check the quality of customers.csv.",
}

for question_id, question in questions.items():
    trace = run_agent(question)
    save_trace(trace, question_id)

    print("=" * 60)
    print(question_id + ": " + question)
    for step in trace["steps"]:
        print("  tool: " + step["tool"] + " " + str(step["arguments"]))
    print("Answer: " + str(trace["answer"]))
