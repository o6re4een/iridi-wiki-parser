import re


def replace_multiple_newlines(text):
    return re.sub(r"\n{3,}", r"\n\n", text)
