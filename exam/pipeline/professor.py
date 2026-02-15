from openai import OpenAI
from prompts.loader import load_prompt

client = OpenAI()

def extract_professor_profile(paper_text: str) -> str:
    """
    Analyses last year's exam paper and extracts
    professor exam-setting behaviour.
    """

    prompt_template = load_prompt("professor_prompt")

    full_prompt = f"""
{prompt_template}

EXAM PAPER:
{paper_text}
"""

    response = client.responses.create(
        model="gpt-4o-mini",
        input=full_prompt
    )

    return response.output_text
