import copy
import os
import sys
from typing import List
from bs4 import BeautifulSoup, Comment
from bs4.element import NavigableString, Tag, PageElement
import re
import requests
import logging
from requests.adapters import HTTPAdapter
from helpers.download_img import download_img
from helpers.CONSTANTS import SAVE_DIR_PATH, SOURCE_URL, DOCUS_IMAGE_BASE_PATH
from helpers.strs import (
    clean_pp_limit,
    replace_multiple_newlines,
    escape_markdown,
    sanitize_filename,
)


FORMAT = "%(asctime)s %(message)s"
logging.basicConfig(
    format=FORMAT, filename="logs.log", level="INFO", encoding="utf-8", filemode="w"
)

logger = logging.getLogger(__name__)

PAGE_NAME = None
IS_SPEC_TAG = False


def get_node_class_str(node: Tag) -> str:
    cls_list = node.get("class", []) or []
    cls_str = " ".join(cls_list)
    return cls_str


def html_to_markdown(html_content):
    # global PAGE_NAME
    soup = BeautifulSoup(html_content, "html.parser")
    content_div = soup.find("div", id="mw-content-text")
    # PAGE_NAME = soup.find_all("span", "mw-headline")[1].get_attribute_list("id")[0]
    # print(PAGE_NAME)
    if content_div is None:
        return ""
    return convert_node(content_div).strip()


def convert_node(node):
    global PAGE_NAME
    if isinstance(node, NavigableString):
        text = re.sub(r"\n\s+", " ", node.string.replace("\xa0", " ").strip())

        # Проверяем, не находится ли узел внутри блока кода
        parent = node.parent
        in_code_block = False
        while parent:
            if parent.name in ["pre", "code"]:
                in_code_block = True
                break
            parent = parent.parent

        # Экранируем только вне блоков кода
        if not in_code_block and text:
            text = escape_markdown(text)

        return text + " " if text else ""

    if isinstance(node, Comment):
        return ""

    node_name = node.name.lower() if node.name else ""
    class_list = node.get("class", []) or []
    class_str = " ".join(class_list)

    if "mw-pt-languages" in class_str:
        return ""

    # Обработка заголовков
    if node_name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
        level = int(node_name[1]) + 1

        return f"{'#' * level} {convert_children(node)}\n\n"

    # Обработка параграфов
    # Обработка прорывов строк
    if node_name == "br":
        return "\n\n"

    if node_name == "p":
        return convert_p(node)
    # Обработка полужирных
    if node_name == "b":
        return f"**{convert_children(node).strip()}** "
    if node_name == "i":
        return convert_i(node)

    # Обработка списков
    if node.name == "ul" or node.name == "ol":
        return convert_list(node)

    # Обработка изображений
    if node_name == "img":

        src = node.get("src", "")
        alt = node.get("alt", "")
        title = node.get("title", "")

        return download_img(src, PAGE_NAME)

    # Обработка таблиц
    if node_name == "table":
        return convert_table(node)

    # Обработка блоков кода
    if node_name == "pre":
        div_class = node.parent
        class_list_code = div_class.get("class", []) or None
        code_lang = ""
        if class_list_code:
            code_lang = class_list_code[0]
        return convert_code_block(node, code_lang)
    if node_name == "code":
        return f"`{node.getText()}` "

    # Обработка специальных блоков
    if node_name == "div" and "panel" in class_str and "panel-default" in class_str:
        return convert_panel(node)
    if "alert" in class_str:
        return convert_alert(node)

    if "thumbnail" in class_str:
        main_heading = node.find("h1")
        if main_heading:
            logger.info(f"Название файла {PAGE_NAME}")

            return f"---\nid: {sanitize_filename(PAGE_NAME)}\ntitle: {PAGE_NAME}\n---\n# {main_heading.text}\n\n"
        return convert_thumbnail(node)

    # Обработка ссылок
    if node_name == "a":
        href = node.get("href", "")
        link = ""
        if href.find("http") != -1:
            link = href
        else:
            link = SOURCE_URL + href
        text = convert_children(node).strip()
        return f"[{text}]({link})"

    if node_name == "span":
        return convert_span(node)

    if "breadcrumb" in class_str:
        return ""

    # if node_name == "span" and "glyphicon" in class_str:
    #     print(f"Node: {node_name} \n Class: {class_str}, NODE {node}")
    #     if "glyphicon-info-sign" in class_str:
    #         return "ℹ️ "
    #     if "glyphicon-download" in class_str:
    #         return "⭳ "
    #     return ""

    # Рекурсивная обработка дочерних элементов
    return convert_children(node)


def convert_span(node: Tag) -> str:
    node_class_list = node.get("class", []) or []
    node_class_str = " ".join(node_class_list)

    if "label-default" in node_class_str:
        return f"`{node.get_text()}` "

    if "glyphicon" in node_class_str:
        # Для иконок внутри таблиц возвращаем символ
        if node.find_parent("td"):
            return "ℹ️ "
        # Для остальных случаев - пустую строку (обрабатывается в convert_p)
        return ""

    return f"{convert_children(node)} "


def convert_i(node: Tag) -> str:
    # Проверяем, не содержит ли курсив специальную иконку
    if node.find("span", class_="glyphicon-info-sign"):
        # Если содержит - обработаем как часть admonition
        return convert_children(node)
    return f"*{convert_children(node).strip()}* "


def convert_p(node: Tag) -> str:
    # Проверяем, содержит ли параграф специальную иконку
    icon_span = node.find("span", class_="glyphicon-info-sign")
    if icon_span:
        # Создаем копию узла для безопасной модификации
        p_copy = copy.copy(node)

        # Удаляем иконку из копии
        icon_span = p_copy.find("span", class_="glyphicon-info-sign")
        if icon_span:
            icon_span.decompose()

        # Разворачиваем теги <i> сохраняя их содержимое
        for i_tag in p_copy.find_all("i"):
            i_tag.unwrap()

        # Извлекаем текст и обрабатываем
        content = convert_children(p_copy).strip()
        logger.info(f"Content adm: {content}")
        logger.info(f"Content tagp: {node.getText().strip()} ")
        logger.info(f"Len cont: {len(content)}")

        if len(content) == 0 and node.getText():
            content = node.getText().strip()

        # Определяем тип admonition (note/warning)
        if node.find_all("span", attrs={"style": "color: red;"}):
            return f":::warning\n{content}\n:::\n\n"
        return f":::note\n{content}\n:::\n\n"

    return f"{convert_children(node)}\n\n"


def convert_children(node):

    output = ""
    for child in node.children:

        result = convert_node(child)
        if result is not None:
            output += result

    return output


def convert_list(node, level=0):
    output = ""
    list_type = "ol" if node.name == "ol" else "ul"

    for li in node.find_all("li", recursive=False):
        # Обрабатываем содержимое текущего пункта
        item_content = ""
        for child in li.children:
            if child.name in ["ul", "ol"]:
                # Рекурсивно обрабатываем вложенный список
                item_content += "\n" + convert_list(child, level + 1)
            else:
                item_content += convert_node(child)

        # Форматируем пункт с учетом уровня вложенности
        indent = "  " * level
        prefix = "1. " if list_type == "ol" else "- "
        output += f"{indent}{prefix}{item_content.strip()}\n"

        # Обработка текста после вложенного списка
        for sibling in li.next_siblings:
            if sibling.name in ["ul", "ol"]:
                continue
            if sibling.name is None and not sibling.strip():
                continue
            if sibling.name != "li":
                text = convert_node(sibling)
                if text:
                    output += f"{indent}  {text.strip()}\n"

    # Добавляем отступы для вложенных списков
    if level > 0:
        output = (
            "\n"
            + "\n".join(
                "  " + line if line.strip() else line for line in output.splitlines()
            )
            + "\n"
        )

    return output + "\n"


# def convert_table(node):
#     # Собираем строки таблицы
#     rows = []
#     for tr in node.find_all("tr"):
#         cells = []
#         for cell in tr.find_all(["th", "td"]):
#             # Обрабатываем вложенное содержимое ячейки
#             cell_content = convert_children(cell).strip()
#             # Упрощаем переносы строк внутри ячеек
#             cell_content = " ".join(cell_content.split())
#             cells.append(cell_content)
#         rows.append(cells)

#     if not rows:
#         return ""

#     # Определяем количество столбцов
#     num_columns = max(len(row) for row in rows)

#     # Создаем Markdown-таблицу
#     output = "\n\n"  # Отступ перед таблицей

#     # Заголовок таблицы
#     header = rows[0]
#     output += "| " + " | ".join(header) + " |\n"

#     # Разделитель заголовка
#     output += "| " + " | ".join(["---"] * num_columns) + " |\n"

#     # Тело таблицы
#     for row in rows[1:]:
#         # Дополняем строки до нужного количества столбцов
#         padded_row = row + [""] * (num_columns - len(row))
#         output += "| " + " | ".join(padded_row) + " |\n"

#     return output + "\n"


def convert_table(node):
    """
    Улучшенная версия конвертера с лучшей обработкой rowspan/colspan
    """
    rows = node.find_all("tr")
    if not rows:
        return ""

    # Определяем максимальное количество столбцов
    max_cols = 0
    for tr in rows:
        col_count = 0
        for cell in tr.find_all(["th", "td"]):
            colspan = int(cell.get("colspan", "1"))
            col_count += colspan
        max_cols = max(max_cols, col_count)

    # Создаем таблицу
    table_data = []

    for row_idx, tr in enumerate(rows):
        row_data = []
        col_idx = 0

        for cell in tr.find_all(["th", "td"]):
            # Обрабатываем содержимое ячейки
            cell_content = convert_children(cell).strip()
            cell_content = " ".join(cell_content.split())

            # Получаем параметры объединения
            colspan = int(cell.get("colspan", "1"))
            rowspan = int(cell.get("rowspan", "1"))

            # Добавляем содержимое в основную ячейку
            row_data.append(cell_content)

            # Для colspan добавляем пустые ячейки
            for _ in range(colspan - 1):
                row_data.append("")

            # Примечание: rowspan в Markdown не поддерживается напрямую
            # Можно добавить комментарий или обработать по-другому
            if rowspan > 1:
                row_data[-colspan] = f"{cell_content} (объединено {rowspan} строк)"

        # Дополняем строку до максимального количества столбцов
        while len(row_data) < max_cols:
            row_data.append("")

        table_data.append(row_data)

    # Генерируем Markdown
    if not table_data:
        return ""

    markdown_output = "\n\n"

    for i, row in enumerate(table_data):
        markdown_output += "| " + " | ".join(row) + " |\n"

        # Добавляем разделитель после первой строки
        if i == 0:
            markdown_output += (
                "|" + "|".join([" --- " for _ in range(max_cols)]) + "|\n"
            )

    markdown_output += "\n"

    return markdown_output


def convert_code_block(node: Tag, lang: str | None = None):
    code_str = ""
    for node_child in node.children:
        if isinstance(node_child, NavigableString):
            text = node_child.text
            code_str += text if text else ""
        if isinstance(node_child, Tag):
            text = node_child.text
            code_str += text
        # print(f"\n {node_child} type: {type(node_child)}\n")
    # code_str = ""
    # for code_node_item in code_nodes:
    #     code_str += convert_node(code_node_item).strip()

    # print(code_str)
    # ... (реализация обработки блоков кода)
    # return f"```{code_str}```"
    return f"```{lang}\n{code_str}\n```\n\n"


def convert_panel(node: Tag):
    # Извлекаем заголовок панели
    heading = node.find(class_="panel-heading")
    heading_text = ""
    if heading:
        # Удаляем ненужные элементы из заголовка
        for element in heading.find_all(["div, span"]):
            if element is not None and isinstance(element, NavigableString) != True:
                if "mw-headline" in element.get("class", []) or element.get("id"):
                    element.decompose()
        heading_text = convert_children(heading).strip()

    # Обрабатываем тело панели
    body = node.find(class_="panel-body")
    body_content = convert_children(body) if body else ""

    # Форматируем как раскрывающийся блок Docusaurus
    return f"""
<details>
<summary>{heading_text}</summary>
<div>

{body_content}

</div>
</details>
"""


def convert_alert(node: Tag):
    md_text = ":::tip\n"
    md_text += convert_children(node)
    # for child in node.children:
    #     if isinstance(child, NavigableString):
    #         md_text += child.strip()
    #         continue
    #     md_text += convert_node(child.text).strip()
    return md_text + "\n:::\n\n"


def convert_thumbnail(node: Tag):
    global PAGE_NAME, DOCUS_IMAGE_BASE_PATH
    img_block = node.find("img")
    if img_block:
        img_src = img_block.get_attribute_list("src")[0]
        return download_img(img_src, PAGE_NAME)
    # ... (реализация обработки изображений)
    return "Image Eror"


def parse_many():
    links = []
    with open("to_parse.txt", "r") as f:
        for line in f:
            link = line.strip()
            links.append(link)
    for link in links:
        if link:
            logger.info(f"Parsing {link}")
            parse_single(link)


def parse_single(link: str):
    global PAGE_NAME
    PAGE_NAME = None
    PAGE_NAME = sanitize_filename(link.split("/")[-1])
    headers = {
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Content-Language": "ru",
    }
    cookies = {
        "irmob_wiki3language": "ru",
    }
    html = None
    sessions = requests.Session()
    local_adapter = HTTPAdapter(2, 2, 3)
    sessions.mount("urllb", local_adapter)
    with sessions as ses:
        try:
            html = ses.get(link, headers=headers, cookies=cookies, timeout=6).content
        except Exception as _e:
            logger.exception(f"Error get page content: {_e}")
            os._exit(1)
    # with open("input.html", "r", encoding="utf-8") as f:
    #     html = f.read()
    markdown = html_to_markdown(html)
    final = clean_pp_limit(replace_multiple_newlines(markdown))
    if PAGE_NAME:
        os.makedirs(f"{SAVE_DIR_PATH}{PAGE_NAME}", exist_ok=True)
        with open(f"{SAVE_DIR_PATH}{PAGE_NAME}/output.md", "w", encoding="utf-8") as f:
            f.write(final)

        os.makedirs(f"my-website/docs/{PAGE_NAME}", exist_ok=True)
        with open(f"my-website/docs/{PAGE_NAME}/index.md", "w", encoding="utf-8") as f:
            f.write(final)
        logger.info(f"Успешно спарсил {PAGE_NAME}")
    else:
        logger.error(f"Error not found page name {link}")


if __name__ == "__main__":
    # html = requests.get(PAGE_URL).content
    # # with open("input.html", "r", encoding="utf-8") as f:
    # #     html = f.read()

    # markdown = html_to_markdown(html)
    # final = replace_multiple_newlines(markdown)

    # # print(PAGE_NAME)
    # if PAGE_NAME:
    #     os.makedirs(f"{SAVE_DIR_PATH}{PAGE_NAME}", exist_ok=True)
    #     with open(f"{SAVE_DIR_PATH}{PAGE_NAME}/output.md", "w", encoding="utf-8") as f:
    #         f.write(final)
    #     print(f"Успешно спарсил {PAGE_NAME}")
    #     os.makedirs(f"my-website/docs/{PAGE_NAME}", exist_ok=True)
    #     with open(f"my-website/docs/{PAGE_NAME}/index.md", "w", encoding="utf-8") as f:
    #         f.write(final)
    # else:
    #     print(f"Error not found page name")

    parse_many()
