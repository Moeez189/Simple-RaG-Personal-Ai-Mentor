import re


def clean_text(text):
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)

    lines = []
    for line in text.split("\n"):
        lines.append(re.sub(r" +", " ", line).strip())

    return "\n".join(lines).strip()
