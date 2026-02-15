from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings

def build_db(docs):
    embeddings = OpenAIEmbeddings()
    db = Chroma.from_documents(
        docs,
        embeddings,
        persist_directory="vector_db"
    )
    return db

def get_context(db, query):
    retriever = db.as_retriever(search_kwargs={"k":5})
    docs = retriever.get_relevant_documents(query)
    return "\n".join([d.page_content for d in docs])
