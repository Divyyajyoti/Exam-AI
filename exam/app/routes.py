from fastapi import APIRouter, UploadFile, File
from pipeline.ingest import load_pdf, chunk_docs
from pipeline.rag import build_db, get_context
from pipeline.professor import extract_professor_profile
from pipeline.strategy import generate_strategy
from pipeline.predict import predict_exam_paper

router = APIRouter()

@router.post("/analyse")
async def analyse_exam(
    notes: UploadFile = File(...),
    paper: UploadFile = File(...),
    syllabus: str = ""
):
    notes_path = f"data/{notes.filename}"
    paper_path = f"data/{paper.filename}"

    with open(notes_path, "wb") as f:
        f.write(await notes.read())

    with open(paper_path, "wb") as f:
        f.write(await paper.read())

    notes_docs = load_pdf(notes_path)
    paper_docs = load_pdf(paper_path)

    docs = chunk_docs(notes_docs + paper_docs)
    db = build_db(docs)

    context = get_context(db, "exam")

    paper_text = "\n".join([d.page_content for d in paper_docs])

    professor_profile = extract_professor_profile(paper_text)

    strategy = generate_strategy(
        context=context,
        professor_profile=professor_profile,
        syllabus=syllabus
    )

    predicted_paper = predict_exam_paper(
        context=context,
        professor_profile=professor_profile,
        syllabus=syllabus
    )

    return {
        "professor_profile": professor_profile,
        "strategy": strategy,
        "predicted_paper": predicted_paper
    }
