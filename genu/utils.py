import re


def text_clean(text):
    text = re.sub(r"\n\n+", "\n\n", text)
    text = re.sub(r"\t+", "\t", text)
    text = re.sub(r"\s+", " ", text)
    return text
