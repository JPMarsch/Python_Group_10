import json
import time
from pathlib import Path

from tools import check_quality, inspect_schema, list_datasets, tool_descriptions

PROJECT_DIR = Path(__file__).resolve().parent.parent
MAX_ROUNDS = 5

tools = {
    "list_datasets": list_datasets,
    "inspect_schema": inspect_schema,
    "check_quality": check_quality,
}


def run_tool(name, arguments):

    if name not in tools:
        return "ERROR: there is no tool called " + name

    if name == "list_datasets":
        return ", ".join(list_datasets())

    dataset = arguments.get("dataset")

    if dataset not in list_datasets():
        return "ERROR: " + str(dataset) + " not found. Available: " + ", ".join(list_datasets())

    return tools[name](dataset)


def run_agent(client, model, instructions, question):
    start = time.perf_counter()
    messages = [
        {"role": "system", "content": instructions},
        {"role": "user", "content": question},
    ]
    trace = {"question": question, "model": model, "steps": []}

    for step in range(MAX_ROUNDS):
        response = client.chat.completions.create(model=model, messages=messages, tools=tool_descriptions)
        message = response.choices[0].message

        if not message.tool_calls:
            trace["answer"] = message.content
            trace["runtime_ms"] = round((time.perf_counter() - start) * 1000, 1)
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

    trace["answer"] = "STOPPED: no answer after " + str(MAX_ROUNDS) + " rounds"
    trace["runtime_ms"] = round((time.perf_counter() - start) * 1000, 1)
    return trace


def save_trace(trace, name):
    folder = PROJECT_DIR / "traces"
    folder.mkdir(exist_ok=True)
    with open(folder / (name + ".json"), "w") as file:
        json.dump(trace, file, indent=2)
