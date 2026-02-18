import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import UnstructuredImageLoader
from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def load_file(path: str):
    ext = os.path.splitext(path)[1].lower()

    if ext == ".pdf":
        return PyPDFLoader(path).load()

    if ext in [".png", ".jpg", ".jpeg"]:
        return UnstructuredImageLoader(path).load()

    if ext in [".docx", ".doc"]:
        return UnstructuredWordDocumentLoader(path).load()

    if ext in [".txt", ".md"]:
        return TextLoader(path, encoding="utf-8").load()

    raise ValueError(f"Unsupported file type: {ext}")


def chunk_docs(docs):
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120)
    return splitter.split_documents(docs)
