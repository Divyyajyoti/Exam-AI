from app.core.llm import safe_llm
from prompts.loader import load_prompt


def generate_mindmap(context: str, syllabus: str) -> str:
    system = load_prompt("mindmap_prompts.txt") or (
        "You create very good study mindmaps.\n"
        "Output ONLY Mermaid mindmap syntax."
    )

    user = f"""
Make a creative, exam-oriented Mermaid mindmap.

Rules:
- Output ONLY Mermaid mindmap.
- Use 4-7 top level branches.
- Add mnemonics, common traps, common question types.
- Keep it structured and scannable.

SYLLABUS:
{syllabus}

CONTEXT (notes/papers/hints):
{context}
"""
    out = safe_llm(system, user, temperature=0.45)

    # safety: ensure it starts with mindmap
    if "mindmap" not in out.lower():
        return "mindmap\n  root((Exam Mindmap))\n    MissingOutput((LLM did not return Mermaid mindmap))"
    return out.strip()
