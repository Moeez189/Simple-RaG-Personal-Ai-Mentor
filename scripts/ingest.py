from app.loaders.document_loader import load_documents
from app.rag.text_splitter import split_documents
from app.embeddings.embedding_model import get_embedding_model
from app.rag.vector_store import create_vector_store

def main():

    print("Loading documents...")
    documents = load_documents()

    print(f"Loaded {len(documents)} documents")

    print("Splitting documents...")
    chunks = split_documents(documents)

    print(f"Created {len(chunks)} chunks")

    if not chunks:
        raise ValueError(
            "No text chunks to ingest. Check data/ files and splitting settings."
        )

    print("Loading embeddings...")
    embedding_model = get_embedding_model()

    print("Creating vector database...")
    create_vector_store(chunks, embedding_model)

    print("Done!")

if __name__ == "__main__":
    main()