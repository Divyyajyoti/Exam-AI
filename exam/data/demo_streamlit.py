import streamlit as st
from pipeline.ingest import load_pdf, chunk_docs
from pipeline.rag import build_db, get_context
from pipeline.professor import extract_professor_profile
from pipeline.strategy import generate_strategy

st.title("Exam AI — Professor Prediction Demo")

notes_file = st.file_uploader("Upload notes PDF")
paper_file = st.file_uploader("Upload last year exam")
syllabus = st.text_area("Paste syllabus")

if st.button("Analyse Exam"):
    notes_docs = load_pdf(notes_file)
    paper_docs = load_pdf(paper_file)

    docs = chunk_docs(notes_docs + paper_docs)
    db = build_db(docs)

    context = get_context(db, "Differentiation")

    professor_profile = extract_professor_profile(
        "\n".join([d.page_content for d in paper_docs])
    )

    strategy = generate_strategy(
        context,
        professor_profile,
        syllabus
    )

    st.subheader("Professor Style")
    st.write(professor_profile)

    st.subheader("Exam Strategy")
    st.write(strategy)
