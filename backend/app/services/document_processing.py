import os
import tempfile
from typing import List
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from fastapi import UploadFile

def process_document(uploaded_file: UploadFile) -> List[Document]:
    # Save to temp; PyMuPDFLoader requires a file path
    suffix = ".pdf"
    with tempfile.NamedTemporaryFile("wb", suffix=suffix, delete=False) as tmp:
        content = uploaded_file.file.read()
        tmp.write(content)
        temp_path = tmp.name

    loader = PyMuPDFLoader(temp_path)
    docs = loader.load()
    os.unlink(temp_path)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", "?", "!", " ", ""],
    )
    return splitter.split_documents(docs)
