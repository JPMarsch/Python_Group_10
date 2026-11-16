import json
import sys
import time
from pathlib import Path

# Use the questions and the workflow from fixed_workflow.py
ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT / "fixed_workflow"))
from fixed_workflow import questions, fixed_workflow


def clean(text):
    # make the text easy to compare: small letters, no Markdown, no ":"
    text = text.lower()
    for sign in ["**", "|", ":", "`"]:
        text = text.replace(sign, " ")
    text = text.replace("couldn't find", "not found")
    text = text.replace("couldn’t find", "not found")
    return text


def rate(text, expected_facts):
    # A fact counts as found if all of its words are somewhere in the text
    text = clean(text)
    found = 0
    for fact in expected_facts:
        words = clean(fact).split()
        if all(word in text for word in words):
            found = found + 1
    return found


print()
print("=" * 60)
print("RATING: same check for fixed workflow and agent")
print("| Question | Fixed: facts | Agent: facts | Fixed: steps | Agent: steps | Fixed: time (ms) | Agent: time (ms) |")
print("|---|---|---|---|---|---|---|")

fixed_solved = 0
agent_solved = 0

for q in questions:
    total = len(q["expected_facts"])

    # fixed workflow: the report (and how long it takes)
    start = time.perf_counter()
    report, steps = fixed_workflow(q["question"])
    fixed_time = (time.perf_counter() - start) * 1000
    fixed_found = rate(report, q["expected_facts"])

    # agent: the final answer from the trace (time was saved by agent.py)
    with open(ROOT / "traces" / (q["id"] + ".json")) as file:
        trace = json.load(file)
    agent_found = rate(trace["answer"], q["expected_facts"])
    agent_time = trace.get("runtime_ms", "n/a")
    agent_steps = len(trace["steps"])   # number of tool calls

    # a question is solved if all facts were found
    if fixed_found == total:
        fixed_solved = fixed_solved + 1
    if agent_found == total:
        agent_solved = agent_solved + 1

    print("| " + q["id"]
          + " | " + str(fixed_found) + "/" + str(total)
          + " | " + str(agent_found) + "/" + str(total)
          + " | " + str(steps) + " | " + str(agent_steps)
          + " | " + f"{fixed_time:.1f}" + " | " + str(agent_time) + " |")

print()
print("Solved questions: fixed workflow " + str(fixed_solved) + "/" + str(len(questions))
      + ", agent " + str(agent_solved) + "/" + str(len(questions)))
