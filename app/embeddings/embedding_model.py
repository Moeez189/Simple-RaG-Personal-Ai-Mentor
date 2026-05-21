import os

from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

def get_embedding_model():

    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={
            "token": HF_TOKEN
        }
    )