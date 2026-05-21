from langchain_ollama import ChatOllama

def get_llm():

    return ChatOllama(
        model="llama3:8b",
        temperature=0.3
    )