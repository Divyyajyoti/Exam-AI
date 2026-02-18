from __future__ import annotations
from typing import Optional, List
import os

from fastapi import UploadFile

from app.core.config import settings
from app.services.extraction_service import extract_text_from_upload


async def ingest_files(notes: Optional[UploadFile], paper: Optional[UploadFile], old_subject: Optional[UploadFile] = None):
    """
    For this demo version: ingestion returns extracted text blocks.
    (Stable + avoids Chroma/LangChain failures during demo)
    """
    os.makedirs(settings.DATA_DIR, exist_ok=True)

    blocks: List[str] = []

    if notes:
        t = await extract_text_from_upload(notes, data_dir=settings.DATA_DIR)
        if t.strip():
            blocks.append(f"[NOTES_FILE: {notes.filename}]\n{t}")

    if paper:
        t = await extract_text_from_upload(paper, data_dir=settings.DATA_DIR)
        if t.strip():
            blocks.append(f"[PAST_PAPER_FILE: {paper.filename}]\n{t}")

    if old_subject:
        t = await extract_text_from_upload(old_subject, data_dir=settings.DATA_DIR)
        if t.strip():
            blocks.append(f"[OLD_SUBJECT_PAPER_FILE: {old_subject.filename}]\n{t}")

    return "\n\n".join(blocks).strip()
