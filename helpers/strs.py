import re


def replace_multiple_newlines(text):
    return re.sub(r"\n{3,}", r"\n\n", text)


def escape_markdown(text):
    """
    Избирательно экранирует специальные символы Markdown, сохраняя разметку
    """
    # Символы, которые могут начинать Markdown-конструкции
    start_chars = r"*_-#+>`[~<"

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


def postprocess_text(text):
    """
    Убирает артефакты форматирования после конвертации:
    - Лишние пробелы внутри скобок: ( Type ) -> (Type)
    - Лишние пробелы перед точками: Type . -> Type.
    - Другие частые случаи с пробелами вокруг пунктуации
    """
    # Убираем пробелы внутри скобок
    text = re.sub(r"\(\s+", "(", text)
    text = re.sub(r"\s+\)", ")", text)

    # Убираем пробелы перед точками, запятыми и другими знаками препинания
    text = re.sub(r"\s+([.,;?])", r"\1", text)
    text = re.sub(r" :{1}", ":", text)

    # Убираем пробелы после открывающих кавычек и перед закрывающими
    # text = re.sub(r'["]\s+', r"\1", text)
    # text = re.sub(r'\s+["]', r"\1", text)

    # Исправляем специфические случаи с admonition
    text = re.sub(r'[".]:::', "\n:::", text)
    text = re.sub(r"(\w+):::", r"\1\n:::", text)
    text = re.sub(r"[>]:::", ">\n:::", text)
    # text = re.sub(r"\\*:::", ":::", text)
    # text = re.sub(r"\\*\(", "(", text)
    # text = re.sub(r"\\*\)", ")", text)

    # Убираем пробелы в конце строк перед знаками препинания
    # text = re.sub(r"\s+\n([.,:;!?])", r"\1\n", text)

    # Исправляем артефакты вокруг ссылок
    text = re.sub(r"\(\s+", "(", text)
    text = re.sub(r"\s+\)", ")", text)
    # text = clear_admonitions(text)
    return text


# def postprocess_text(text):
#     """
#     Убирает артефакты форматирования после конвертации с защитой admonitions
#     """
#     # Защищаем блоки admonitions перед обработкой
#     protected_blocks = []

#     def protect_admonitions(match):
#         protected_blocks.append(match.group(0))
#         return f"__PROTECTED_ADMONITION_{len(protected_blocks)-1}__"

#     # Находим и "защищаем" все блоки admonitions
#     text = re.sub(
#         r"(?:::+)[^\n]*(?:\n(?!:::).*)*\n:::+",
#         protect_admonitions,
#         text,
#         flags=re.DOTALL,
#     )

#     # Основные замены
#     # Убираем пробелы внутри скобок
#     text = re.sub(r"\(\s+", "(", text)
#     text = re.sub(r"\s+\)", ")", text)

#     # Убираем пробелы перед точками, запятыми и другими знаками препинания
#     # Исключаем случаи, где знак препинания является частью admonition
#     text = re.sub(r"\s+([.,;?])", r"\1", text)

#     # Убираем пробелы в конце строк перед знаками препинания
#     # text = re.sub(r"\s+\n([.,:;!?])", r"\1\n", text)

#     # Исправляем артефакты вокруг ссылок
#     text = re.sub(r"\(\s+", "(", text)
#     text = re.sub(r"\s+\)", ")", text)

#     # Восстанавливаем защищенные блоки admonitions
#     def restore_admonitions(match):
#         idx = int(match.group(1))
#         return protected_blocks[idx] if idx < len(protected_blocks) else ""

#     text = re.sub(r"__PROTECTED_ADMONITION_(\d+)__", restore_admonitions, text)

#     # Гарантируем разделение блоков admonitions пустой строкой
#     text = re.sub(r"(:::[^\n]*\n(?:[^:]*|:[^:])*?)\n(:::[^\n]*\n)", r"\1\n\n\2", text)

#     # Фиксим склеенные admonitions
#     text = re.sub(r":{5,}", ":::", text)

#     return text


def clear_admonitions(page_text: str) -> str:
    res = page_text
    if page_text.find("::::"):
        res = page_text.replace("::::", ":::\n\n:")
    return res
