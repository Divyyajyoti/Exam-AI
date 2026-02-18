from pipeline.professor import extract_professor_profile

def analyze_professor_text(text: str) -> str:
    if not (text or "").strip():
        return "No professor past paper provided."
    return extract_professor_profile(text)
