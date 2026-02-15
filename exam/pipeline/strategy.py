from openai import OpenAI
from prompts.loader import load_prompt

client = OpenAI()

def generate_strategy(context: str, professor_profile: str, syllabus: str) -> str:
    """
    Generates high-impact exam study strategy.
    """

    prompt_template = load_prompt("strategy_prompt")

    full_prompt = f"""
{prompt_template}

PROFESSOR STYLE:
{professor_profile}

SYLLABUS:
{syllabus}

CONTEXT:
{context}
"""

    response = client.responses.create(
        model="gpt-4o-mini",
        input=full_prompt
    )

    return response.output_text
