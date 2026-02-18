from pipeline.strategy import generate_strategy as _generate

def generate_strategy(context: str, professor_profile: str, syllabus: str, hints: str = ""):
    return _generate(
        context=context,
        professor_profile=professor_profile,
        syllabus=syllabus,
        hints=hints
    )
