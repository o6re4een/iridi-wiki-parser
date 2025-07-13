import re


def replace_multiple_newlines(text):
    return re.sub(r"\n{3,}", r"\n\n", text)


def escape_file_name(text):
    escape_chars = r"\/*?<>:|()+-"
    for char in escape_chars:
        text = text.replace(char, "")
    return text


def escape_markdown(text):
    """
    Экранирует специальные символы Markdown в тексте
    """
    # Список символов, которые нужно экранировать
    escape_chars = r"\*_{}[]()#+-.!|`~<>"
    # Экранируем каждый специальный символ
    for char in escape_chars:
        text = text.replace(char, "\\" + char)
    return text
