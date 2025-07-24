import requests
from bs4 import BeautifulSoup
import re
import os
from urllib.parse import urlparse, urljoin
import logging
import uuid
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Настройка логирования
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("html2md")


def create_session():
    """Создает сессию с повторными попытками и увеличенным таймаутом"""
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def ensure_absolute_url(url: str, base_url: str) -> str:
    """Преобразует относительный URL в абсолютный"""
    if not url:
        return ""

    # Убираем дублирование слешей в базовом URL
    base_url = base_url.rstrip("/")

    # Обработка абсолютных URL
    if url.startswith(("http://", "https://")):
        return url

    # Обработка протоколо-независимых URL
    if url.startswith("//"):
        return f"{urlparse(base_url).scheme}:{url}"

    # Обработка якорей и спецссылок
    if url.startswith(("mailto:", "tel:", "#")):
        return url

    # Все остальные случаи - объединяем с базовым URL
    return urljoin(base_url + "/", url.lstrip("/"))


def wrap_in_md_code_block(text: str, language: str = "") -> str:
    """Обертывает текст в блок кода Markdown"""
    return f"```{language}\n{text}\n```"


def get_language_from_classes(classes: list) -> str:
    """Определяет язык программирования по классам"""
    if not classes:
        return ""

    for cls in classes:
        if cls in [
            "javascript",
            "js",
            "python",
            "html",
            "css",
            "java",
            "csharp",
            "php",
        ]:
            return cls
    return ""


def wrap_numbers_in_backticks(text: str) -> str:
    """Оборачивает число в начале строки в обратные кавычки"""
    return re.sub(r"^(\d+\.?\d*)", r"`\1`", text)


def convert_inline_formatting(element, base_url: str):
    """Обрабатывает inline-форматирование: жирный, курсив, ссылки и т.д."""
    from bs4 import NavigableString

    output = []

    for content in element.contents:
        if isinstance(content, NavigableString):
            text = content.strip()
            if text:
                # Оборачиваем числа в обратные кавычки
                text = wrap_numbers_in_backticks(text)
                output.append(text)
        elif content.name in ["b", "strong"]:
            output.append(f"**{content.get_text().strip()}**")
        elif content.name in ["i", "em"]:
            output.append(f"*{content.get_text().strip()}*")
        elif content.name == "a":
            href = content.get("href", "")
            text = content.get_text().strip()
            if href and text:
                # Преобразуем в абсолютный URL
                href = ensure_absolute_url(href, base_url)
                output.append(f"[{text}]({href})")
        elif content.name == "img":
            src = content.get("src", "")
            alt = content.get("alt", "") or "image"
            title = content.get("title", "")
            if src:
                # Преобразуем в абсолютный URL
                src = ensure_absolute_url(src, base_url)
                if title:
                    output.append(f'![{alt}]({src} "{title}")')
                else:
                    output.append(f"![{alt}]({src})")
        elif content.name == "br":
            output.append("\n")
        elif content.name == "code":
            output.append(f"`{content.get_text()}`")
        elif content.name == "span":
            # Пропускаем иконки
            if "glyphicon" not in content.get("class", []):
                output.append(content.get_text().strip())

    return " ".join(output)


def process_list(list_element, base_url: str, indent_level=0):
    """Обрабатывает списки (маркированные и нумерованные)"""
    items = []
    indent = "  " * indent_level
    is_ordered = list_element.name == "ol"

    for i, li in enumerate(list_element.find_all("li", recursive=False), 1):
        # Обрабатываем текст элемента
        text = convert_inline_formatting(li, base_url)

        # Обрабатываем вложенные списки
        sub_lists = li.find(["ul", "ol"], recursive=False)
        if sub_lists:
            sub_items = process_list(sub_lists, base_url, indent_level + 1)
            prefix = f"{i}." if is_ordered else "-"
            items.append(f"{indent}{prefix} {text}")
            items.extend(sub_items)
        else:
            prefix = f"{i}." if is_ordered else "-"
            items.append(f"{indent}{prefix} {text}")

    return items


def fix_links_in_element(element, base_url):
    """Исправляет относительные ссылки и изображения в элементе и его дочерних элементах"""
    if not element:
        return

    # Исправляем изображения
    for img in element.find_all("img"):
        src = img.get("src")
        if src:
            img["src"] = ensure_absolute_url(src, base_url)

    # Исправляем ссылки
    for a in element.find_all("a"):
        href = a.get("href")
        if href:
            a["href"] = ensure_absolute_url(href, base_url)


def process_admonition(element, base_url: str):
    """Обрабатывает специальные блоки для Docusaurus Admonition"""
    classes = element.get("class", [])
    admonition_type = "note"

    if "alert-warning" in classes:
        admonition_type = "warning"
    elif "alert-info" in classes:
        admonition_type = "info"
    elif "alert-danger" in classes:
        admonition_type = "danger"
    elif "alert-success" in classes:
        admonition_type = "success"

    # Удаляем возможные иконки внутри блока
    for icon in element.find_all("span", class_="glyphicon"):
        icon.decompose()

    content = convert_inline_formatting(element, base_url).strip()

    # Удаляем пустые строки в начале и конце
    content = re.sub(r"^\s+|\s+$", "", content)

    # Если после удаления иконок контент пуст, возвращаем пустую строку
    if not content:
        return ""

    return f":::{admonition_type}\n{content}\n:::"


def remove_unwanted_elements(soup):
    """Удаляет ненужные элементы из контента"""
    # Удаляем элементы по ID
    unwanted_ids = [
        "siteSub",
        "contentSub",
        "jump-to-nav",
        "p-search",
        "catlinks",
        "printfooter",
        "visualClear",
        "toc",
    ]

    for element_id in unwanted_ids:
        element = soup.find(id=element_id)
        if element:
            element.decompose()

    # Удаляем элементы по классам
    unwanted_classes = [
        "mw-jump",
        "mw-indicators",
        "vector-page-toolbar",
        "page-actions",
        "page-tools",
        "mw-editsection",
        "dablink",
        "nomobile",
        "noprint",
        "toctoggle",
    ]

    for class_name in unwanted_classes:
        for element in soup.find_all(class_=class_name):
            element.decompose()

    return soup


def download_image(session, img_src: str, output_dir: str, page_name: str) -> str:
    """Скачивает изображение и возвращает относительный путь"""
    if not img_src:
        return ""

    try:
        # Формируем абсолютный URL
        abs_url = ensure_absolute_url(img_src, base_url1)

        # Скачиваем изображение
        img = session.get(abs_url, timeout=10)
        img.raise_for_status()

        # Генерируем имя файла
        file_name = os.path.basename(img_src.split("?")[0])
        if not file_name:
            file_name = f"{uuid.uuid4()}.png"

        # Создаем директории
        os.makedirs(f"{output_dir}/{page_name}", exist_ok=True)
        os.makedirs(f"my-website/static/img/{page_name}", exist_ok=True)

        # Пути для сохранения
        local_path = f"{output_dir}/{page_name}/{file_name}"
        docus_path = f"my-website/static/img/{page_name}/{file_name}"

        # Сохраняем изображение
        with open(local_path, "wb") as f:
            f.write(img.content)
        with open(docus_path, "wb") as f:
            f.write(img.content)

        logger.info(f"Изображение сохранено: {local_path}")
        return f"{DOCUS_IMAGE_BASE_PATH}{page_name}/{file_name}"

    except Exception as e:
        logger.error(f"Ошибка загрузки изображения: {str(e)}")
        return ""


def process_image_element(
    element,
    md_lines: list,
    download_images: bool,
    output_dir: str,
    session,
    page_name: str,
) -> bool:
    """Обрабатывает изображения в различных контейнерах"""
    img = None
    caption = ""
    title = ""

    # Обработка thumbnail контейнеров
    if element.name == "div" and "thumbnail" in element.get("class", []):
        # Ищем изображение внутри
        img = element.find("img")
        if not img:
            a_tag = element.find("a", class_="image")
            if a_tag:
                img = a_tag.find("img")

        # Извлекаем описание
        caption_elem = element.find(class_="caption")
        if caption_elem:
            caption = caption_elem.get_text(strip=True)

    # Обработка figure
    elif element.name == "figure":
        img = element.find("img")
        figcaption = element.find("figcaption")
        if figcaption:
            caption = figcaption.get_text(strip=True)

    # Обработка обычных изображений
    elif element.name == "img":
        img = element

    # Обработка ссылок с изображениями
    elif element.name == "a" and element.find("img"):
        img = element.find("img")
        title = element.get("title", "") or img.get("title", "")

    if not img or not img.get("src"):
        return False

    src = img.get("src")
    alt = img.get("alt", "") or caption or "image"

    # Скачиваем изображение
    local_path = ""
    if download_images and output_dir and session:
        local_path = download_image(session, src, output_dir, page_name)

    # Формируем Markdown
    if local_path:
        md_text = f"![{alt}]({local_path})"
    else:
        abs_url = ensure_absolute_url(src, base_url1)
        md_text = f"![{alt}]({abs_url})"

    md_lines.append(md_text)
    return True


def process_element(
    element,
    base_url,
    md_lines,
    depth=0,
    download_images=False,
    output_dir=None,
    session=None,
    page_name=None,
):
    # Пропускаем скрытые элементы
    if "style" in element.attrs and "display:none" in element["style"]:
        return

    # Сначала проверяем картинки
    if process_image_element(
        element, md_lines, download_images, output_dir, session, page_name
    ):
        md_lines.append("")
        return

    if element.name == "span" and "glyphicon" in element.get("class", []):
        if "glyphicon-info-sign" in element.get("class", []):
            # Собираем информацию из соседних элементов
            info_content = []
            next_node = element.next_sibling

            # Собираем все текстовые элементы до следующего тега
            while next_node and (isinstance(next_node, str) or next_node.name != "br"):
                if isinstance(next_node, str):
                    text = next_node.strip()
                    if text:
                        info_content.append(text)
                elif next_node.name:
                    # Обрабатываем вложенные inline-элементы
                    info_content.append(convert_inline_formatting(next_node, base_url))

                next_node = next_node.next_sibling

            content = " ".join(info_content).strip()
            if not content:
                content = "Важная информация"

            md_lines.append(f":::note\n{content}\n:::")
            md_lines.append("")  # Пустая строка после блока
            return

    # Специальная обработка для таблиц
    if element.name == "table":
        # Фиксируем ссылки в таблице
        fix_links_in_element(element, base_url)
        # Сохраняем таблицу как HTML
        md_lines.append(str(element))
        md_lines.append("")
        return

    # Обработка оберток таблиц
    if element.name == "div" and "table-responsive" in element.get("class", []):
        table = element.find("table")
        if table:
            # Фиксируем ссылки в таблице
            fix_links_in_element(table, base_url)
            # Сохраняем обертку и таблицу как HTML
            md_lines.append('<div class="table-responsive">')
            md_lines.append(str(table))
            md_lines.append("</div>")
            md_lines.append("")
            return

    # Обрабатываем заголовки
    if element.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
        level = int(element.name[1])
        text = convert_inline_formatting(element, base_url)
        md_lines.append("#" * level + " " + text)
        md_lines.append("")
        return

    # Абзацы
    if element.name == "p":
        text = convert_inline_formatting(element, base_url)
        if text:
            md_lines.append(text)
            md_lines.append("")
        return

    # Списки
    if element.name in ["ul", "ol"]:
        items = process_list(element, base_url)
        md_lines.extend(items)
        md_lines.append("")
        return

    # Блоки с кодом
    if element.name == "pre":
        code_block = element.find("code")
        if code_block:
            lang = get_language_from_classes(code_block.get("class", []))
            code_text = code_block.get_text()
            md_lines.append(wrap_in_md_code_block(code_text, lang))
            md_lines.append("")
        else:
            md_lines.append(wrap_in_md_code_block(element.get_text()))
            md_lines.append("")
        return

    # Блоки предупреждений (admonitions)
    if element.name == "div" and "alert" in element.get("class", []):
        admonition = process_admonition(element, base_url)
        if admonition:  # Добавляем только если есть содержимое
            md_lines.append(admonition)
            md_lines.append("")
        return

    # Если элемент содержит дочерние элементы — обрабатываем их рекурсивно
    for child in element.find_all(recursive=False):
        process_element(
            child,
            base_url,
            md_lines,
            depth + 1,
            download_images,
            output_dir,
            session,
            page_name,
        )


def html_to_md(
    html_content: str,
    base_url: str,
    download_images: bool,
    output_dir: str,
    session,
    page_name: str,
) -> str:
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        # Пробуем разные селекторы
        content = (
            soup.find("div", id="mw-content-text")
            or soup.find("main")
            or soup.find("article")
            or soup.find("body")
            or soup
        )

        if not content:
            logger.warning("Контент не найден!")
            return ""

        logger.info(
            f"Контент найден: тип {type(content)}, дети {len(list(content.children))}"
        )
        logger.info(f"Текст начала контента: {content.get_text()[:200]!r}")

        content = remove_unwanted_elements(content)
        md_lines = []

        for element in content.find_all(recursive=False):
            process_element(
                element,
                base_url,
                md_lines,
                download_images=download_images,
                output_dir=output_dir,
                session=session,
                page_name=page_name,
            )

        return "\n".join(md_lines)

    except Exception as e:
        logger.error(f"Ошибка преобразования: {str(e)}")
        return ""


def process_urls_from_file(input_file: str, output_dir: str, download_images=False):
    """Обрабатывает URL из файла"""
    os.makedirs(output_dir, exist_ok=True)
    session = create_session()

    with open(input_file, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f.readlines() if line.strip()]

    for i, url in enumerate(urls):
        try:
            logger.info(f"Обработка URL {i+1}/{len(urls)}: {url}")
            response = session.get(url, timeout=10)
            response.raise_for_status()

            parsed_url = urlparse(url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

            # Генерируем имя страницы для изображений
            page_name = parsed_url.path.split("/")[-1] or "index"
            page_name = re.sub(r"[^\w\-_]", "_", page_name)

            # Конвертация в Markdown (передаем page_name)
            md_content = html_to_md(
                response.text,
                base_url,
                download_images,
                output_dir,
                session,
                page_name,  # Добавлен параметр
            )

            if not md_content.strip():
                logger.warning(f"Пустой результат для {url}")
                continue

            # Сохранение Markdown
            domain = parsed_url.netloc.replace("www.", "").replace(".", "_")
            filename = f"{domain}_{page_name}.md"
            filename = re.sub(r"[^\w\-_.]", "_", filename)
            filepath = os.path.join(output_dir, filename)

            with open(filepath, "w", encoding="utf-8") as f_out:
                f_out.write(md_content)
                logger.info(f"Сохранено в: {filepath}")

        except Exception as e:
            logger.error(f"Ошибка обработки URL '{url}': {str(e)}")

    logger.info(f"Обработка завершена! Результаты в {output_dir}")


# Глобальная переменная для базового URL
base_url1 = "https://dev.iridi.com/"

# Основной процесс обработки
if __name__ == "__main__":
    input_file = "urls.txt"
    output_dir = "markdown_pages"
    download_images = True

    process_urls_from_file(input_file, output_dir, download_images)
