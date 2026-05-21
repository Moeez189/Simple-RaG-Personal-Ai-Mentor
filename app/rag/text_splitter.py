from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    MarkdownHeaderTextSplitter
)

from langchain_core.documents import Document


def split_documents(documents):

    markdown_headers = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]

    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=markdown_headers
    )

    recursive_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50,
        separators=[
            "\n\n",
            "\n",
            ". ",
            "? ",
            "! ",
            " "
        ]
    )

    final_chunks = []

    for doc in documents:
        md_chunks = markdown_splitter.split_text(doc.page_content)

        if md_chunks:
            md_docs = [
                Document(
                    page_content=chunk.page_content,
                    metadata={**doc.metadata, **chunk.metadata},
                )
                for chunk in md_chunks
            ]
        else:
            md_docs = [doc]

        split_chunks = recursive_splitter.split_documents(md_docs)
        final_chunks.extend(split_chunks)

    return [
        chunk
        for chunk in final_chunks
        if chunk.page_content and chunk.page_content.strip()
    ]