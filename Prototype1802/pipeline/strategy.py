from app.core.llm import safe_llm
from prompts.loader import load_prompt


def generate_strategy(context: str, professor_profile: str, syllabus: str, hints: str = "") -> str:
    system = load_prompt("strategy_prompts.txt") or (
        "You generate exam prep strategies with different scoring targets."
    )

    user = f"""
Create a strategy split by GOAL and TIME LEFT.

GOALS:
A) Pass only
B) 60–70% scoring
C) Topper

TIME LEFT VERSIONS:
1) 1 month
2) 1 week
3) 1 day
4) 1 hour

For each goal:
- What to study first (80/20)
- What to skip
- How to write answers (structure, diagrams, keywords)
- Daily plan (or hourly if 1 hour)
- Checklist

Use the professor fingerprint if provided.

SYLLABUS:
{syllabus}

PROFESSOR FINGERPRINT:
{professor_profile}

IMPORTANT HINTS:
{hints}

CONTEXT:
{context}
"""
    return safe_llm(system, user, temperature=0.35).strip()
