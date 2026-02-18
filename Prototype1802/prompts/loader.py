import os

BASE = "prompts"

def load_prompt(name: str):
    path = os.path.join(BASE, name)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
