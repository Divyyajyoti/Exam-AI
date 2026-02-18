from app.core.llm import chat_completion
from prompts.loader import load_prompt

def predict_exam_paper(context, professor_profile, syllabus, hints=""):
    system = load_prompt("predict_prompts.txt")

    user = f"""
Context:
{context}

Professor:
{professor_profile}

Syllabus:
{syllabus}

Important hints before exam:
{hints}
"""

    return chat_completion(system, user)
