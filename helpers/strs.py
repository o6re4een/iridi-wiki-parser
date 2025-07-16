import re


def replace_multiple_newlines(text):
    return re.sub(r"\n{3,}", r"\n\n", text)


def escape_markdown(text):
    """
    Избирательно экранирует специальные символы Markdown, сохраняя разметку
    """
    # Символы, которые могут начинать Markdown-конструкции
    start_chars = r"*_-#+>`[~"

    # Экранируем только если символ:
    # 1. В начале строки
    # 2. После пробела
    # 3. Перед ним нет обратного слеша
    escaped = []
    for i, char in enumerate(text):
        if char in start_chars:
            # Проверяем контекст символа
            prev_char = text[i - 1] if i > 0 else " "
            next_char = text[i + 1] if i < len(text) - 1 else " "

            # Условия, когда нужно экранировать:
            if (
                (prev_char in ("\n", " ", "\t") or i == 0)  # Начало строки/слова
                or (char == ">" and prev_char == "\n")  # Цитаты
                or (
                    char == "`" and "`" not in (prev_char, next_char)
                )  # Одиночные backticks
            ):
                # Не экранируем, если это часть корректной разметки
                if not (
                    (
                        char == "*" and next_char == "*" and text[i + 2 : i + 3] != " "
                    )  # **bold**
                    or (
                        char == "_" and next_char == "_" and text[i + 2 : i + 3] != " "
                    )  # __bold__
                    or (
                        char == "~" and next_char == "~" and text[i + 2 : i + 3] != " "
                    )  # ~~strike~~
                    or (
                        char == "[" and next_char == "]" and text[i + 2 : i + 3] == "("
                    )  # [link]()
                ):
                    escaped.append("\\" + char)
                    continue

        escaped.append(char)

    return "".join(escaped)


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
    illegal_chars = r'[<>:"/\\|?*\x00-\x1F]+'
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


def clean_pp_limit(text: str):
    regex = re.compile(r"(NewPP).*$", flags=re.MULTILINE | re.DOTALL)
    text = re.sub(regex, "", text)
    return text


# def clear_admonitions(page_text: str) -> str:
#     first_repl = re.sub("\W")
#     return first_repl
