from app.core.llm import safe_llm
from prompts.loader import load_prompt


def simplify_notes(context: str, syllabus: str) -> str:
    system = load_prompt("simplify_prompts.txt") or (
        "You explain topics to lazy students using analogies and exam shortcuts."
    )

    user = f"""
Create a SUPER DETAILED cheat sheet.

Format:
1) 10-line ultra-short summary
2) Key definitions
3) Top 10 most asked questions + how to answer
4) Analogies (nerd explaining to idiot friend)
5) Mistakes/traps
6) Last-minute memory hacks / mnemonics
7) 5 practice mini-questions with answers

SYLLABUS:
{syllabus}

CONTEXT:
{context}
"""
    return safe_llm(system, user, temperature=0.55).strip()
