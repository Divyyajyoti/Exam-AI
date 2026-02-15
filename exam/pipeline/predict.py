from openai import OpenAI
from prompts.loader import load_prompt

client = OpenAI()

def predict_exam_paper(context: str, professor_profile: str, syllabus: str) -> str:
    """
    Generates a predicted exam paper structure + likely questions.
    """

    prompt_template = load_prompt("predict_prompt")

    full_prompt = f"""
{prompt_template}

PROFESSOR STYLE:
{professor_profile}

SYLLABUS:
{syllabus}

CONTEXT FROM NOTES & PAST PAPERS:
{context}
"""

    response = client.responses.create(
        model="gpt-4o-mini",
        input=full_prompt
    )

    return response.output_text
