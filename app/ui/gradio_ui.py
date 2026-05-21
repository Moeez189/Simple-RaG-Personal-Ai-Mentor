import gradio as gr

from app.chat.chatbot import ask_question

def chat(message, history):

    response = ask_question(message)

    return response

demo = gr.ChatInterface(
    fn=chat,
    title="Personal AI Mentor",
    description="RAG-based AI mentor for mobile app interview preparation"
)

demo.launch()