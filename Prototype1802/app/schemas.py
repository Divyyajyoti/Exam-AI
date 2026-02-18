from pydantic import BaseModel
from typing import Optional

class AnalyseTextRequest(BaseModel):
    subject: str = ""
    exam_type: str = ""
    syllabus: str = ""
    weightage: str = ""
    professor_hints_now: str = ""
    professor_hints_last_year: str = ""
    notes_text: str = ""
    last_year_paper_text: str = ""
    old_subject_paper_text: str = ""
    extra_instructions: str = ""
