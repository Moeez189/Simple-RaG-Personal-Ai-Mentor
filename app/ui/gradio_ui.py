import gradio as gr

from app.chat.chatbot import ask_question


def _format_sources_footer(sources):
    if not sources:
        return ""

    lines = ["**Sources:**"]
    for index, item in enumerate(sources, start=1):
        heading = item.get("heading")
        label = f"{item['source']}" + (f" — {heading}" if heading else "")
        lines.append(f"{index}. `{label}` (score {item['score']})")

    return "\n".join(lines)


def chat(message, history):
    answer, sources = ask_question(message, return_sources=True, history=history)
    footer = _format_sources_footer(sources)

    if footer:
        return f"{answer}\n\n---\n\n{footer}"

    return answer


demo = gr.ChatInterface(
    fn=chat,
    title="Personal AI Mentor",
    description="RAG-based AI mentor for mobile app interview preparation (Chroma + rerank)",
)
