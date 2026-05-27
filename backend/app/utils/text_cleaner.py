import re


def clean_text(raw_text: str) -> str:
    text = raw_text.lower()
    text = re.sub(r"[^a-z0-9+#.\s-]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

