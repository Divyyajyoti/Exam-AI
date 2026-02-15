def load_prompt(name):
    with open(f"prompts/{name}.txt", "r", encoding="utf-8") as f:
        return f.read()
