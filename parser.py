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
    postprocess_text,
    replace_multiple_newlines,
    escape_markdown,
    sanitize_filename,
)
from html_table_parse import fix_links_in_element


FORMAT = "%(asctime)s %(message)s"
logging.basicConfig(
    format=FORMAT,
    level="INFO",
    encoding="utf-8",
    # filename="logs.log",
    #   filemode="w"
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

        if node.find_parent(name="table"):
            return convert_children(node) + "<br/> "
        return convert_children(node) + "\n\n"

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
    # if node_name == "div" and "table-responsive" in class_str:
    #     logger.info(f"Found tag: table")
    if node_name == "div" and "table-responsive" in class_list:
        return convert_resp_table(node)

    if node_name == "table":
        parent = node.find_parent("div", class_="table-responsive")

        if parent:
            logger.info("TABLE found")
            return convert_resp_table(parent)

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
        return f"[{text}]({link}) "

    if node_name == "span":
        return convert_span(node)

    if "breadcrumb" in class_str:
        return ""

    # Рекурсивная обработка дочерних элементов
    return convert_children(node)


def convert_resp_table(node: Tag):
    logger.info("converting table")

    res = ""

    # Фиксируем ссылки в таблице
    fix_links_in_element(node, PAGE_NAME)
    # Сохраняем обертку и таблицу как HTML
    res += '<div class="table-responsive">'
    res += str(node)
    res += "</div>"
    res += ""
    logger.info("Table responsive")
    return res


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
        # logger.info(f"Content adm: {content}")
        # logger.info(f"Content tagp: {node.getText().strip()} ")
        # logger.info(f"Len cont: {len(content)}")

        if len(content) == 0 and node.getText():
            content = node.getText().strip()

        if node.find_parent("td"):
            return f"ℹ️ {content}"
        span_danger = node.find("span", attrs={"style": "color: red;"}, recursive=True)
        # Определяем тип admonition (note/warning)
        if span_danger:
            return f"\n:::danger[{span_danger.getText().strip()}]\n{content}\n:::\n\n"
        return f"\n:::note\n{content}\n:::\n\n"

    # logger.info(f"Converting p tag: \n {convert_children(node)}")
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


# def convert_table(node):
#     """
#     Улучшенная версия конвертера с лучшей обработкой rowspan/colspan
#     """


def convert_table_to_html(node):
    """Конвертирует сложные таблицы с объединенными ячейками в HTML"""
    rows = node.find_all("tr")
    if not rows:
        return ""

    # Определяем количество столбцов
    max_cols = 0
    for tr in rows:
        col_count = 0
        for cell in tr.find_all(["th", "td"]):
            colspan = int(cell.get("colspan", "1"))
            col_count += colspan
        max_cols = max(max_cols, col_count)

    # Создаем HTML-таблицу
    output = "\n\n<table>\n"

    for tr in rows:
        output += "  <tr>\n"
        for cell in tr.find_all(["th", "td"]):
            # Получаем параметры ячейки
            tag = "th" if cell.name == "th" else "td"
            colspan = f' colspan="{cell.get("colspan")}"' if cell.get("colspan") else ""
            rowspan = f' rowspan="{cell.get("rowspan")}"' if cell.get("rowspan") else ""
            style = f' style="{cell.get("style")}"' if cell.get("style") else ""

            # Конвертируем содержимое
            cell_content = convert_children(cell).strip()

            output += f"    <{tag}{colspan}{rowspan}{style}>{cell_content}</{tag}>\n"
        output += "  </tr>\n"

    output += "</table>\n\n"
    return output


def convert_table(node):
    rows = node.find_all("tr")
    if not rows:
        return ""

    has_complex_cells = False
    for tr in rows:
        for cell in tr.find_all(["th", "td"]):
            if int(cell.get("rowspan", "1")) > 1 or int(cell.get("colspan", "1")) > 1:
                has_complex_cells = True
                break
        if has_complex_cells:
            break

    if has_complex_cells:
        return convert_table_to_html(node)

    # Определяем максимальное количество столбцов
    max_cols = 0
    for tr in rows:
        col_count = 0
        for cell in tr.find_all(["th", "td"]):
            colspan = int(cell.get("colspan", "1"))
            col_count += colspan
        max_cols = max(max_cols, col_count)

    # Создаем матрицу для представления таблицы
    table_matrix = []
    for _ in range(len(rows)):
        table_matrix.append([None] * max_cols)

    # Заполняем матрицу данными
    row_idx = 0
    rowspans = {}  # Текущие активные rowspan

    for tr in rows:
        col_idx = 0

        # Обрабатываем активные rowspans
        for c in range(max_cols):
            if rowspans.get(c, 0) > 0:
                rowspans[c] -= 1
                if rowspans[c] == 0:
                    del rowspans[c]
                # Пропускаем ячейку, занятую rowspan
                col_idx += 1
                continue
            if table_matrix[row_idx][c] is not None:
                col_idx += 1

        # Обрабатываем ячейки текущей строки
        for cell in tr.find_all(["th", "td"]):
            # Пропускаем занятые ячейки
            while col_idx < max_cols and table_matrix[row_idx][col_idx] is not None:
                col_idx += 1
            if col_idx >= max_cols:
                break

            # Получаем параметры ячейки
            colspan = int(cell.get("colspan", "1"))
            rowspan = int(cell.get("rowspan", "1"))

            # Обрабатываем содержимое
            cell_content = convert_children(cell).strip()
            cell_content = " ".join(cell_content.split())

            # Записываем содержимое в основную ячейку
            table_matrix[row_idx][col_idx] = cell_content

            # Помечаем объединенные ячейки
            for r in range(rowspan):
                for c in range(colspan):
                    if r == 0 and c == 0:
                        continue  # Основная ячейка уже заполнена
                    if row_idx + r < len(table_matrix) and col_idx + c < max_cols:
                        table_matrix[row_idx + r][col_idx + c] = ""

            # Сохраняем rowspan для следующих строк
            if rowspan > 1:
                rowspans[col_idx] = rowspan - 1

            col_idx += colspan

        row_idx += 1

    # Генерируем Markdown таблицу
    output = "\n\n"

    # Заголовок таблицы
    header = table_matrix[0]
    output += "| " + " | ".join(header) + " |\n"

    # Разделитель
    output += "| " + " | ".join(["---"] * max_cols) + " |\n"

    # Тело таблицы
    for row in table_matrix[1:]:
        # Заменяем None на пустые строки
        row_data = [cell if cell is not None else "" for cell in row]
        output += "| " + " | ".join(row_data) + " |\n"

    return output + "\n"


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
    node_local_cls = node.get("class", []) or []
    node_local_clr_str = " ".join(node_local_cls)

    if "alert-warning" in node_local_clr_str:
        return f"\n:::warning[Внимание]\n{convert_children(node).strip()}\n:::\n"

    md_text = "\n:::info[Информация]\n"
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
    final = postprocess_text(final)
    if PAGE_NAME:
        os.makedirs(f"{SAVE_DIR_PATH}{PAGE_NAME}", exist_ok=True)
        with open(f"{SAVE_DIR_PATH}{PAGE_NAME}/output.md", "w", encoding="utf-8") as f:
            f.write(final)

        os.makedirs(f"my-website/docs/{PAGE_NAME}", exist_ok=True)
        with open(f"my-website/docs/{PAGE_NAME}/index.md", "w", encoding="utf-8") as f:
            f.write(final)
        logger.info(
            f"Успешно спарсил {PAGE_NAME}\n------------------------------------------------------------------------"
        )
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
