import re


def replace_multiple_newlines(text):
    return re.sub(r"\n{3,}", r"\n\n", text)


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


import re
import unicodedata


def sanitize_filename(filename, replace_spaces=True):
    """
    Форматирует строку в безопасное для файлового пути представление.

    Параметры:
        filename (str): Исходная строка с названием файла/папки.
        replace_spaces (bool): Заменять пробелы на подчёркивания (по умолчанию True).

    Возвращает:
        str: Безопасное для файловой системы отформатированное имя.
    """
    # Нормализация Unicode (преобразует символы в их эквиваленты)
    cleaned = unicodedata.normalize("NFKD", filename)

    # Удаление непечатаемых символов и символов управления
    cleaned = "".join(c for c in cleaned if not unicodedata.category(c).startswith("C"))

    # Замена недопустимых символов
    if replace_spaces:
        cleaned = cleaned.replace(" ", "_")

    # Список запрещённых символов для файловых систем
    illegal_chars = r'[<>:"/\\|?*\x00-\x1F]'
    cleaned = re.sub(illegal_chars, "_", cleaned)

    # Удаление двойных подчёркиваний
    cleaned = re.sub(r"_{2,}", "_", cleaned)

    # Удаление подчёркиваний с начала/конца
    cleaned = cleaned.strip("_")

    # Удаление зарезервированных имён Windows
    windows_reserved = [
        "CON",
        "PRN",
        "AUX",
        "NUL",
        "COM1",
        "COM2",
        "COM3",
        "COM4",
        "COM5",
        "COM6",
        "COM7",
        "COM8",
        "COM9",
        "LPT1",
        "LPT2",
        "LPT3",
        "LPT4",
        "LPT5",
        "LPT6",
        "LPT7",
        "LPT8",
        "LPT9",
    ]
    if cleaned.upper() in windows_reserved:
        cleaned = "_" + cleaned

    # Максимальная длина для Windows (255 символов)
    return cleaned[:255]
