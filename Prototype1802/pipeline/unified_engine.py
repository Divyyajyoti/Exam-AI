from __future__ import annotations
import json
from typing import Any, Dict

from app.core.llm import call_llm
from app.core.subject_resolver import get_subject_grounding, resolve_subject


def _grounding_score(subject: str, syllabus: str, notes: str, paper: str, hints: str) -> int:
    score = 0
    if subject: score += 10
    if syllabus and len(syllabus) > 30: score += 25
    if notes and len(notes) > 80: score += 25
    if paper and len(paper) > 80: score += 25
    if hints and len(hints) > 30: score += 15
    return min(score, 100)


def _offline_fallback(subject: str, exam_type: str, syllabus: str, hints: str, grounding_source: str, grounding_score: int) -> Dict[str, Any]:
    # Used when API quota / key fails so demo still shows something coherent.
    subj = resolve_subject(subject) or "your subject"
    return {
        "grounding": {"source": grounding_source, "score": grounding_score},
        "professor_profile": {
            "question_length_preference": "medium",
            "marks_distribution_pattern": "mixed",
            "conceptual_vs_numerical_ratio": "mixed",
            "repetition_tendency": "unknown",
            "favourite_question_types": ["explanation", "compare", "example"],
            "difficulty_level": "medium",
            "trick_questions_present": "unknown",
            "step_marking_importance": "high",
        },
        "strategy": {
            "time_windows": {
                "1_month": {
                    "pass": {
                        "goal": "Pass",
                        "confidence": 0.35,
                        "topics": ["Use your syllabus to list 6–8 most important units"],
                        "order": ["Unit-wise coverage", "Weekly revision", "Solve last year paper"],
                        "time_allocation": "2h/day fundamentals + 30m revision; 2 mocks/week",
                        "expected_marks": "Pass if syllabus is accurate",
                        "how_to_answer": "Use definition → diagram/table → example → 2-3 bullet points",
                        "do_not_do": "Don’t over-index on random topics without syllabus evidence",
                    },
                    "score_60_70": {
                        "goal": "Score 60–70%",
                        "confidence": 0.30,
                        "topics": ["High-ROI units from syllabus + last year patterns"],
                        "order": ["Top 3 units deep", "Next 2 units medium", "Rest skim"],
                        "time_allocation": "3h/day + 1 mock on weekends",
                        "expected_marks": "60–70% if patterns match",
                        "how_to_answer": "Write structured answers: compare tables, stepwise algorithms, diagrams",
                        "do_not_do": "Don’t memorize without solving 1–2 papers",
                    },
                    "topper": {
                        "goal": "Topper (85–100%)",
                        "confidence": 0.20,
                        "topics": ["Full syllabus + tricky edge-cases + proofs/derivations if any"],
                        "order": ["Full coverage", "3+ mocks", "Error log + repeat weak areas"],
                        "time_allocation": "4–6h/day plus timed writing practice",
                        "expected_marks": "85% possible only with strong syllabus + materials",
                        "how_to_answer": "Add crisp intros, labelled diagrams, and 'why' explanations",
                        "do_not_do": "Don’t ignore presentation and time management",
                    }
                },
                "1_week": {},
                "1_day": {},
                "1_hour": {},
            }
        },
        "predicted_paper": [
            {
                "question": f"(Offline demo) List 5–7 likely questions for {subj} based on syllabus/hints.",
                "marks": 10,
                "confidence": 0.25,
                "why": "No LLM quota; placeholder output",
                "evidence": ["[SYSTEM] Offline fallback mode"],
            }
        ],
        "mindmap_mermaid": "mindmap\n  root((Upload syllabus/notes for real mindmap))",
        "cheatsheet": f"Offline mode.\nSubject: {subj}\nExam: {exam_type}\nSyllabus: {syllabus}\nHints: {hints}\n\nAdd syllabus + notes for real predictions.",
        "errors": ["OpenAI unavailable (quota/key). Showing offline fallback."],
    }


def generate_unified_json(payload: Dict[str, Any]) -> Dict[str, Any]:
    subject = (payload.get("subject") or "").strip()
    exam_type = (payload.get("exam_type") or "").strip()
    syllabus = (payload.get("syllabus") or "").strip()
    weightage = (payload.get("weightage") or "").strip()
    notes_text = (payload.get("notes_text") or "").strip()
    last_year_paper = (payload.get("last_year_paper_text") or "").strip()
    old_subject_paper = (payload.get("old_subject_paper_text") or "").strip()
    prof_now = (payload.get("professor_hints_now") or "").strip()
    prof_last = (payload.get("professor_hints_last_year") or "").strip()
    extra = (payload.get("extra_instructions") or "").strip()

    user_material = "\n\n".join([
        f"[SYLLABUS]\n{syllabus}" if syllabus else "",
        f"[WEIGHTAGE]\n{weightage}" if weightage else "",
        f"[NOTES]\n{notes_text}" if notes_text else "",
        f"[LAST_YEAR_PAPER]\n{last_year_paper}" if last_year_paper else "",
        f"[OLD_SUBJECT_PAPER]\n{old_subject_paper}" if old_subject_paper else "",
        f"[PROF_HINTS_NOW]\n{prof_now}" if prof_now else "",
        f"[PROF_HINTS_LAST_YEAR]\n{prof_last}" if prof_last else "",
        f"[EXTRA]\n{extra}" if extra else "",
    ]).strip()

    grounding_text, grounding_source = get_subject_grounding(subject, user_material)
    gscore = _grounding_score(subject, syllabus, notes_text, last_year_paper, prof_now)

    # If we have no curated grounding AND weak user material, enforce safe behavior.
    safe_mode = (grounding_source == "none" and gscore < 40)

    context = f"""
SUBJECT: {resolve_subject(subject) or subject}

SUBJECT_GROUNDING_SOURCE: {grounding_source}
SUBJECT_GROUNDING:
{grounding_text}

USER_MATERIAL:
{user_material}
""".strip()

    schema = r"""
Return STRICT JSON only. No markdown. No extra keys.

Schema:
{
  "grounding": { "source": "curated|user_material_only|none", "score": 0 },
  "professor_profile": {
    "question_length_preference": "short|medium|long|unknown",
    "marks_distribution_pattern": "equal|unequal|mixed|unknown",
    "conceptual_vs_numerical_ratio": "high_conceptual_low_numerical|mixed|high_numerical_low_conceptual|unknown",
    "repetition_tendency": "none|some|high|unknown",
    "favourite_question_types": ["explanation","diagram","example","compare","numerical","proof","derivation"],
    "difficulty_level": "easy|medium|hard|unknown",
    "trick_questions_present": "yes|no|unknown",
    "step_marking_importance": "low|medium|high|unknown"
  },
  "strategy": {
    "time_windows": {
      "1_month": {
        "pass": {
          "goal": "Pass",
          "confidence": 0.0,
          "topics": [],
          "order": [],
          "time_allocation": "",
          "expected_marks": "",
          "how_to_answer": "",
          "do_not_do": ""
        },
        "score_60_70": { "goal": "Score 60–70%", "confidence": 0.0, "topics": [], "order": [], "time_allocation": "", "expected_marks": "", "how_to_answer": "", "do_not_do": "" },
        "topper": { "goal": "Topper (85–100%)", "confidence": 0.0, "topics": [], "order": [], "time_allocation": "", "expected_marks": "", "how_to_answer": "", "do_not_do": "" }
      },
      "1_week": {
        "pass": { "goal": "Pass", "confidence": 0.0, "topics": [], "order": [], "time_allocation": "", "expected_marks": "", "how_to_answer": "", "do_not_do": "" },
        "score_60_70": { "goal": "Score 60–70%", "confidence": 0.0, "topics": [], "order": [], "time_allocation": "", "expected_marks": "", "how_to_answer": "", "do_not_do": "" },
        "topper": { "goal": "Topper (85–100%)", "confidence": 0.0, "topics": [], "order": [], "time_allocation": "", "expected_marks": "", "how_to_answer": "", "do_not_do": "" }
      },
      "1_day": {
        "pass": { "goal": "Pass", "confidence": 0.0, "topics": [], "order": [], "time_allocation": "", "expected_marks": "", "how_to_answer": "", "do_not_do": "" },
        "score_60_70": { "goal": "Score 60–70%", "confidence": 0.0, "topics": [], "order": [], "time_allocation": "", "expected_marks": "", "how_to_answer": "", "do_not_do": "" },
        "topper": { "goal": "Topper (85–100%)", "confidence": 0.0, "topics": [], "order": [], "time_allocation": "", "expected_marks": "", "how_to_answer": "", "do_not_do": "" }
      },
      "1_hour": {
        "pass": { "goal": "Pass", "confidence": 0.0, "topics": [], "order": [], "time_allocation": "", "expected_marks": "", "how_to_answer": "", "do_not_do": "" },
        "score_60_70": { "goal": "Score 60–70%", "confidence": 0.0, "topics": [], "order": [], "time_allocation": "", "expected_marks": "", "how_to_answer": "", "do_not_do": "" },
        "topper": { "goal": "Topper (85–100%)", "confidence": 0.0, "topics": [], "order": [], "time_allocation": "", "expected_marks": "", "how_to_answer": "", "do_not_do": "" }
      }
    }
  },
  "predicted_paper": [
    {
      "question": "...",
      "marks": 10,
      "confidence": 0.0,
      "why": "...",
      "evidence": ["[NOTES] ...", "[LAST_YEAR_PAPER] ...", "[PROF_HINTS_NOW] ..."]
    }
  ],
  "mindmap_mermaid": "mindmap\n  root((...))",
  "cheatsheet": "..."
}
"""

    rules = f"""
Rules:
- Use ONLY concepts of the SUBJECT shown in the context. Never switch subjects.
- Evidence must come from USER_MATERIAL blocks; if not available, say evidence is weak and lower confidence.
- If in SAFE MODE (low grounding), keep predictions short + low confidence + explicitly ask user to upload syllabus/notes.

SAFE MODE: {str(safe_mode).lower()}
GROUNDING_SCORE: {gscore}
"""

    prompt = f"""{schema}

{rules}

INPUTS:
Subject: {subject}
Exam type: {exam_type}

CONTEXT:
{context}
"""

    try:
        raw = call_llm(prompt)
        data = json.loads(raw)

        # Always enforce grounding fields (even if model forgets)
        data["grounding"] = {"source": grounding_source, "score": gscore}

        # Hard safety: if safe mode, clamp confidences
        if safe_mode:
            for tw in data.get("strategy", {}).get("time_windows", {}).values():
                for tier in ["pass", "score_60_70", "topper"]:
                    if tier in tw and isinstance(tw[tier], dict):
                        tw[tier]["confidence"] = min(float(tw[tier].get("confidence", 0.2) or 0.2), 0.35)

            for q in data.get("predicted_paper", []) or []:
                if isinstance(q, dict):
                    q["confidence"] = min(float(q.get("confidence", 0.2) or 0.2), 0.35)
                    if not q.get("evidence"):
                        q["evidence"] = ["[SYSTEM] Weak evidence. Upload syllabus/notes/past paper."]

        return data

    except Exception as e:
        # Quota/API/JSON parse errors -> offline fallback
        return _offline_fallback(
            subject=subject,
            exam_type=exam_type,
            syllabus=syllabus,
            hints=prof_now,
            grounding_source=grounding_source,
            grounding_score=gscore,
        )
