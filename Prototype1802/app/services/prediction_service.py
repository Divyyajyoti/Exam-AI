from pipeline.predict import predict_exam_paper

def predict_exam(context: str, professor_profile: str, syllabus: str, hints: str = ""):
    return predict_exam_paper(
        context=context,
        professor_profile=professor_profile,
        syllabus=syllabus,
        hints=hints
    )
