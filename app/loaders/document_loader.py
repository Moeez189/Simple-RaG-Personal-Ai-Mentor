from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import Docx2txtLoader
from app.utils.preprocess import clean_text


def load_documents():
    documents = []

    txt_loader = DirectoryLoader(
        "data",
        glob="**/*.txt",
        loader_cls=TextLoader
    )

    md_loader = DirectoryLoader(
        "data",
        glob="**/*.md",
        loader_cls=TextLoader
    )

    pdf_loader = DirectoryLoader(
        "data",
        glob="**/*.pdf",
        loader_cls=PyPDFLoader
    )

    docx_loader = DirectoryLoader(
        "data",
        glob="**/*.docx",
        loader_cls=Docx2txtLoader
    )

    documents.extend(txt_loader.load())
    documents.extend(md_loader.load())
    documents.extend(pdf_loader.load())
    documents.extend(docx_loader.load())

    documents = [
        document
        for document in documents
        if not document.metadata.get("source", "").endswith("data/README.md")
    ]

    for doc in documents:
        doc.page_content = clean_text(doc.page_content)

    return documents
