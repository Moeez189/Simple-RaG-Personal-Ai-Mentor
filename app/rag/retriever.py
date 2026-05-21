from langchain_chroma import Chroma
from app.embeddings.embedding_model import get_embedding_model

def get_vector_store():

    embedding_model = get_embedding_model()

    return Chroma(
        persist_directory="chroma_db",
        embedding_function=embedding_model
    )