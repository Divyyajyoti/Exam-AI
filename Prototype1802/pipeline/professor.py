from app.core.llm import safe_llm
from prompts.loader import load_prompt


def extract_professor_profile(paper_text: str) -> str:
    system = load_prompt("professor_prompts.txt") or (
        "You analyze professor exam-setting patterns."
    )

    user = f"""
Analyse the professor's exam-setting pattern.

Output MUST be:
1) A normal-text paragraph summary (human readable)
2) Bullet points: question style, difficulty, repetition, favorite topics, marking style
3) A small JSON block at the end under heading 'JSON_FINGERPRINT' (for machines)

PAST PAPER TEXT:
{paper_text}
"""
    out = safe_llm(system, user, temperature=0.2).strip()
    return out
