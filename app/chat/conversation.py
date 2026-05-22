import re

FOLLOW_UP_HINTS = {
    "example",
    "examples",
    "more",
    "that",
    "those",
    "it",
    "this",
    "also",
    "elaborate",
    "clarify",
    "again",
    "above",
    "previous",
    "same",
    "topic",
}

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "can",
    "do",
    "does",
    "for",
    "give",
    "help",
    "i",
    "in",
    "is",
    "me",
    "my",
    "of",
    "on",
    "or",
    "please",
    "tell",
    "the",
    "there",
    "to",
    "what",
    "when",
    "where",
    "which",
    "with",
    "who",
    "you",
}


def _normalize_message(text):
    lowered_text = text.strip().lower()
    lowered_text = re.sub(r"[^\w\s#+.]", " ", lowered_text)
    return re.sub(r"\s+", " ", lowered_text).strip()


def parse_history(history):
    if not history:
        return []

    turns = []

    for item in history:

        # New Gradio message format
        if isinstance(item, dict):
            role = item.get("role")
            content = item.get("content")

            # Handle list content safely
            if isinstance(content, list):
                text_parts = []

                for part in content:
                    if isinstance(part, str):
                        text_parts.append(part)

                    elif isinstance(part, dict):
                        if part.get("type") == "text":
                            text_parts.append(part.get("text", ""))

                content = " ".join(text_parts)

            # Convert anything else to string
            content = str(content or "").strip()

            if role in {"user", "assistant"} and content:
                turns.append((role, content))

            continue

        # Old tuple/list format
        if isinstance(item, (list, tuple)) and len(item) == 2:
            user_message, assistant_message = item

            if user_message:
                turns.append(("user", str(user_message).strip()))

            if assistant_message:
                turns.append(("assistant", str(assistant_message).strip()))

    return turns


def get_last_user_message(history):
    for role, content in reversed(parse_history(history)):
        if role == "user":
            return content
    return ""


def is_follow_up(message):
    normalized = _normalize_message(message)

    if not normalized:
        return False

    return bool(set(normalized.split()) & FOLLOW_UP_HINTS)


def build_retrieval_query(message, history=None):
    message = message.strip()

    if not message or not history:
        return message

    if not is_follow_up(message):
        return message

    previous_user_message = get_last_user_message(history)
    if not previous_user_message:
        return message

    return f"{previous_user_message} {message}".strip()


def format_conversation_history(history, max_turns=2):
    turns = parse_history(history)

    if not turns:
        return ""

    recent_turns = turns[-(max_turns * 2) :]
    lines = []

    for role, content in recent_turns:
        speaker = "User" if role == "user" else "Assistant"
        lines.append(f"{speaker}: {content}")

    return "\n".join(lines)
