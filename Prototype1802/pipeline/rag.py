# pipeline/rag.py

import os
from dotenv import load_dotenv

# 🔥 CRITICAL: Load env BEFORE importing embeddings
load_dotenv()

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma


# Create embeddings safely
def get_embeddings():
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment")

    return OpenAIEmbeddings(
        model="text-embedding-3-large",
        openai_api_key=api_key
    )


# Build vector database
def build_db(docs):

    embeddings = get_embeddings()

    db = Chroma.from_documents(
        docs,
        embeddings,
        persist_directory="vector_db"
    )

    return db


# Retrieve context
def get_context(db, query):

    results = db.similarity_search(query, k=5)

    return "\n\n".join([doc.page_content for doc in results])
