import re
from app.core.subject_knowledge import SUBJECT_KNOWLEDGE

ALIASES = {
    "os": "operating systems",
    "operating system": "operating systems",
    "dsa": "data structures",
    "ds": "data structures",
    "data strcutures": "data structures",
    "computer network": "computer networks",
    "cn": "computer networks",
}


def normalize(text: str) -> str:
    text = (text or "").lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def resolve_subject(subject: str) -> str:
    s = normalize(subject)
    return ALIASES.get(s, s)


def get_subject_grounding(subject: str, user_material: str) -> tuple[str, str]:
    """
    Returns: (grounding_text, source_tag)
    source_tag in {"curated", "user_material_only", "none"}
    """
    s = resolve_subject(subject)

    if s in SUBJECT_KNOWLEDGE:
        return SUBJECT_KNOWLEDGE[s].strip(), "curated"

    # if user provided a lot of material, we can rely on that and avoid inventing
    if user_material and len(user_material) > 500:
        return "", "user_material_only"

    # unknown + no material
    return "", "none"
