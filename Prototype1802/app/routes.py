from fastapi import APIRouter, UploadFile, File, Form, Body
from typing import Optional

from app.schemas import AnalyseTextRequest
from app.core.config import settings
from app.services.extraction_service import extract_text_from_upload
from app.services.ingestion_service import ingest_files
from app.services.context_service import fetch_context
from app.services.professor_service import analyze_professor_text
from app.services.strategy_service import generate_strategy
from app.services.prediction_service import predict_exam

from pipeline.subject_context import generate_subject_context
from pipeline.mindmap import generate_mindmap
from pipeline.simplify import simplify_notes

router = APIRouter()


@router.get("/")
def root():
    return {"status": "ok", "name": "Exam AI Investor Demo"}


@router.post("/extract_text")
async def extract_text(file: UploadFile = File(...)):
    text = await extract_text_from_upload(file, data_dir=settings.DATA_DIR)
    return {"filename": file.filename, "text": text}


@router.post("/analyse")
async def analyse_exam(
    subject: str = Form(""),
    exam_type: str = Form(""),
    syllabus: str = Form(""),
    weightage: str = Form(""),
    professor_hints_now: str = Form(""),
    professor_hints_last_year: str = Form(""),
    extra_instructions: str = Form(""),

    notes: Optional[UploadFile] = File(None),
    paper: Optional[UploadFile] = File(None),
    old_subject_paper: Optional[UploadFile] = File(None),
):
    # extract uploads into text
    uploads_blob = await ingest_files(notes, paper, old_subject_paper)

    # subject grounding (anti-hallucination)
    subject_grounding = generate_subject_context(subject)

    # assemble context
    context = f"""
SUBJECT_GROUNDING:
{subject_grounding}

USER_INPUT:
Subject: {subject}
Exam type: {exam_type}
Syllabus: {syllabus}
Weightage: {weightage}
Prof hints now: {professor_hints_now}
Prof hints last year: {professor_hints_last_year}
Extra instructions: {extra_instructions}

UPLOADS_EXTRACTED_TEXT:
{uploads_blob}
""".strip()

    # professor fingerprint: prefer paper upload if exists
    professor_profile = ""
    if uploads_blob:
        # paper content likely inside uploads_blob; still good enough for demo
        professor_profile = analyze_professor_text(uploads_blob)

    strategy = generate_strategy(
        context=context,
        professor_profile=professor_profile,
        syllabus=syllabus or subject,
        hints=professor_hints_now
    )

    predicted_paper = predict_exam(
        context=context,
        professor_profile=professor_profile,
        syllabus=syllabus or subject,
        hints=professor_hints_now
    )

    mindmap = generate_mindmap(context=context, syllabus=syllabus or subject)
    cheatsheet = simplify_notes(context=context, syllabus=syllabus or subject)

    return {
        "subject": subject,
        "exam_type": exam_type,
        "syllabus": syllabus,
        "weightage": weightage,
        "professor_profile": professor_profile,
        "strategy": strategy,
        "predicted_paper": predicted_paper,
        "mindmap_mermaid": mindmap,
        "cheatsheet": cheatsheet,
    }


@router.post("/analyse_text")
async def analyse_text(payload: AnalyseTextRequest = Body(...)):
    subject_grounding = generate_subject_context(payload.subject)

    blocks = []

    if payload.syllabus:
        blocks.append(f"SYLLABUS:\n{payload.syllabus}")
    if payload.weightage:
        blocks.append(f"WEIGHTAGE:\n{payload.weightage}")
    if payload.professor_hints_now:
        blocks.append(f"PROF_HINTS_NOW:\n{payload.professor_hints_now}")
    if payload.professor_hints_last_year:
        blocks.append(f"PROF_HINTS_LAST_YEAR:\n{payload.professor_hints_last_year}")
    if payload.notes_text:
        blocks.append(f"NOTES_TEXT:\n{payload.notes_text}")
    if payload.last_year_paper_text:
        blocks.append(f"LAST_YEAR_PAPER_TEXT:\n{payload.last_year_paper_text}")
    if payload.old_subject_paper_text:
        blocks.append(f"OLD_SUBJECT_PAPER_TEXT:\n{payload.old_subject_paper_text}")
    if payload.extra_instructions:
        blocks.append(f"EXTRA_INSTRUCTIONS:\n{payload.extra_instructions}")

    user_material = "\n\n".join(blocks).strip()

    context = f"""
SUBJECT_GROUNDING:
{subject_grounding}

USER_MATERIAL:
{user_material}
""".strip()

    professor_profile = analyze_professor_text(payload.last_year_paper_text or payload.old_subject_paper_text or "")

    strategy = generate_strategy(
        context=context,
        professor_profile=professor_profile,
        syllabus=payload.syllabus or payload.subject,
        hints=payload.professor_hints_now or ""
    )

    predicted_paper = predict_exam(
        context=context,
        professor_profile=professor_profile,
        syllabus=payload.syllabus or payload.subject,
        hints=payload.professor_hints_now or ""
    )

    mindmap = generate_mindmap(context=context, syllabus=payload.syllabus or payload.subject)
    cheatsheet = simplify_notes(context=context, syllabus=payload.syllabus or payload.subject)

    return {
        "subject": payload.subject,
        "exam_type": payload.exam_type,
        "syllabus": payload.syllabus,
        "professor_profile": professor_profile,
        "strategy": strategy,
        "predicted_paper": predicted_paper,
        "mindmap_mermaid": mindmap,
        "cheatsheet": cheatsheet,
    }
