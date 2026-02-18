import streamlit as st
import requests
import hashlib

API_URL = "http://127.0.0.1:8000"


# -------------------------
# STYLE (Bloomberg-ish)
# -------------------------
TERMINAL_CSS = """
<style>
html, body, [class*="css"]  { background-color: #0b0f14 !important; color: #e6edf3 !important; }
.block-container { padding-top: 1.2rem; }
h1, h2, h3 { color: #e6edf3 !important; }
.small-muted { color: #9aa4b2; font-size: 0.9rem; }
.panel {
  border: 1px solid #1f2937;
  background: #0f1620;
  padding: 14px 14px;
  border-radius: 10px;
}
.kpi {
  border: 1px solid #1f2937;
  background: #0b1220;
  padding: 10px 12px;
  border-radius: 10px;
}
.badge {
  display:inline-block; padding: 2px 8px; border-radius: 999px;
  border: 1px solid #334155; background:#0b1220; color:#e2e8f0; font-size: 12px;
}
hr { border-color: #1f2937 !important; }
</style>
"""


# -------------------------
# FILE EXTRACTION HELPERS
# -------------------------
def _file_cache_key(uploaded_file) -> str:
    return hashlib.sha256(uploaded_file.getvalue()).hexdigest()


def extract_text_via_api(uploaded_file) -> str:
    cache = st.session_state.setdefault("extract_cache", {})
    key = _file_cache_key(uploaded_file)

    if key in cache:
        return cache[key]

    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
    r = requests.post(f"{API_URL}/extract_text", files=files, timeout=180)

    if r.status_code != 200:
        raise RuntimeError(r.text)

    text = (r.json().get("text") or "").strip()
    cache[key] = text
    return text


def text_with_upload(label, key, height=120):
    text = st.text_area(label, key=f"{key}_text", height=height)
    uploads = st.file_uploader(
        f"Upload → {label}",
        type=["pdf", "png", "jpg", "jpeg", "txt", "md"],
        accept_multiple_files=True,
        key=f"{key}_upload",
    )

    extracted = []
    if uploads:
        for f in uploads:
            try:
                t = extract_text_via_api(f)
                if t:
                    extracted.append(f"\n\n--- FILE: {f.name} ---\n{t}")
            except Exception as e:
                extracted.append(f"\n\n--- FILE: {f.name} OCR/Extract ERROR ---\n{e}")

    return (text or "") + "".join(extracted)


# -------------------------
# UI
# -------------------------
st.set_page_config(page_title="Exam AI — Investor Demo", layout="wide")
st.markdown(TERMINAL_CSS, unsafe_allow_html=True)

st.markdown(
    "<div class='panel'>"
    "<h1>EXAM AI <span class='badge'>Investor Demo</span></h1>"
    "<div class='small-muted'>Bloomberg-style exam prediction terminal — paste or upload PDFs/images/handwritten notes.</div>"
    "</div>",
    unsafe_allow_html=True
)

st.write("")

colA, colB, colC = st.columns([1.2, 1.2, 1.0])

with colA:
    st.markdown("<div class='kpi'><b>Mode</b><br>Text + Upload Hybrid</div>", unsafe_allow_html=True)
with colB:
    st.markdown("<div class='kpi'><b>Output</b><br>Predicted Paper • Strategy • Mindmap • Cheat Sheet</div>", unsafe_allow_html=True)
with colC:
    st.markdown("<div class='kpi'><b>Target</b><br>College exams + JEE/NEET/CAT/UPSC later</div>", unsafe_allow_html=True)

st.write("")

left, right = st.columns(2)

with left:
    st.markdown("<div class='panel'><h3>INPUTS — Academic Context</h3></div>", unsafe_allow_html=True)
    subject = st.text_input("Subject", value="Operating Systems")
    exam_type = st.text_input("Exam Type", value="Midterm")

    syllabus = text_with_upload("Syllabus / Units / Chapters", "syllabus", 140)
    weightage = text_with_upload("Weightage / Marking Scheme", "weightage", 90)

    prof_now = text_with_upload("Professor Important Topics (NOW)", "prof_now", 90)
    prof_last = text_with_upload("Professor Important Topics (LAST YEAR)", "prof_last", 90)

with right:
    st.markdown("<div class='panel'><h3>INPUTS — Your Material</h3></div>", unsafe_allow_html=True)
    notes = text_with_upload("Notes (paste OR upload)", "notes", 150)
    last_year = text_with_upload("Last Year Paper (paste OR upload)", "last_year", 150)
    old_subject = text_with_upload("Professor Old Subject Paper (if changed)", "old_subject", 150)
    extra = text_with_upload("Extra Instructions", "extra", 90)

st.write("")
run = st.button("🚀 RUN TERMINAL", use_container_width=True)

if run:
    payload = {
        "subject": subject,
        "exam_type": exam_type,
        "syllabus": syllabus,
        "weightage": weightage,
        "professor_hints_now": prof_now,
        "professor_hints_last_year": prof_last,
        "notes_text": notes,
        "last_year_paper_text": last_year,
        "old_subject_paper_text": old_subject,
        "extra_instructions": extra,
    }

    with st.spinner("Thinking like your topper friend..."):
        r = requests.post(f"{API_URL}/analyse_text", json=payload, timeout=300)

    if r.status_code != 200:
        st.error(f"API ERROR {r.status_code}")
        st.code(r.text)
        st.stop()

    data = r.json()

    tabs = st.tabs([
        "🎯 Predicted Paper",
        "🧠 Strategy (Pass / 60–70 / Topper + Time Left)",
        "👨‍🏫 Professor Fingerprint",
        "🗺️ Mindmap",
        "🧾 Cheat Sheet",
        "🔎 Raw JSON"
    ])

    with tabs[0]:
        st.markdown("### 🎯 Predicted Paper")
        st.write(data.get("predicted_paper", ""))

    with tabs[1]:
        st.markdown("### 🧠 Strategy")
        st.write(data.get("strategy", ""))

    with tabs[2]:
        st.markdown("### 👨‍🏫 Professor Fingerprint (Human-readable + JSON at end)")
        st.write(data.get("professor_profile", ""))

    with tabs[3]:
        st.markdown("### 🗺️ Mindmap (Mermaid)")
        st.code(data.get("mindmap_mermaid", ""), language="markdown")
        st.caption("Tip: paste into Mermaid Live Editor to render.")

    with tabs[4]:
        st.markdown("### 🧾 Cheat Sheet")
        st.write(data.get("cheatsheet", ""))

    with tabs[5]:
        st.json(data)
