import logging
import os
import re
import time
import requests

from transliterate import translit  # Импортируем библиотеку для транслитерации
from helpers.CONSTANTS import DOCUS_IMAGE_BASE_PATH, SAVE_DIR_PATH, SOURCE_URL
from .strs import sanitize_filename

logger = logging.getLogger(__name__)

# def download_img(img_src: str, page_name: str) -> str:
#     if img_src:
#         # download_link = (
#         #     f"{SOURCE_URL+img_src}" if not img_src.find("/images/") else None
#         # )
#         download_link = f"{SOURCE_URL+img_src}"
#         # logger.info(f"download_link: {download_link}")
#         if download_link:
#             file_name = sanitize_filename(img_src.split("/")[-1])
#             # print(download_link)
#             local_save_path = f"{SAVE_DIR_PATH}{page_name}/{file_name}"
#             docus_save_path_dir = f"my-website/static/img/{page_name}"
#             docus_save_path_file = f"my-website/static/img/{page_name}/{file_name}"

#             is_downloaded = os.path.exists(local_save_path) and os.path.exists(
#                 docus_save_path_file
#             )
#             if is_downloaded:
#                 logger.info(f"Already downloaded: {file_name}")
#                 return f"![{123}]({DOCUS_IMAGE_BASE_PATH+page_name+'/'+file_name})\n\n"

#             img = requests.get(download_link, timeout=2)

#             logger.info(f"file_name: {file_name}")
#             os.makedirs(f"{SAVE_DIR_PATH}{page_name}", exist_ok=True)

#             with open(local_save_path, "wb") as f:
#                 f.write(img.content)
#             os.makedirs(docus_save_path_dir, exist_ok=True)
#             # Сохраниние в локальный проект docusaurus
#             with open(docus_save_path_file, "wb") as f:
#                 f.write(img.content)
#             time.sleep(0.4)


#             return f"![{123}]({DOCUS_IMAGE_BASE_PATH+page_name+'/'+file_name})\n\n"
#     return "Image Error"
def safe_filename(name):
    # Транслитерируем кириллицу
    logger.info(f"Name before: {name}")
    name = translit(name, "ru", reversed=True)

    # Заменяем пробелы и специальные символы
    name = re.sub(r"\s+", "_", name)
    name = re.sub(r"[^a-zA-Z0-9_\.-]", "", name)
    logger.info(f"Name after: {name}")
    return name.lower()  # Для единообразия используем нижний регистр


def download_img(img_src: str, page_name: str) -> str:
    if not img_src:
        return "Image Error"

    try:
        # Генерируем безопасное имя файла

        # Получаем оригинальное имя файла
        original_name = img_src.split("/")[-1]
        # Создаем безопасное имя файла
        safe_name = safe_filename(original_name)

        # Формируем пути
        local_save_path = f"{SAVE_DIR_PATH}{page_name}/{safe_name}"
        docus_save_path_dir = f"my-website/static/img/{page_name}"
        docus_save_path_file = f"{docus_save_path_dir}/{safe_name}"

        # Проверяем, существует ли уже файл
        if os.path.exists(local_save_path) and os.path.exists(docus_save_path_file):
            logger.info(f"Already downloaded: {safe_name}")
            return f"![]({DOCUS_IMAGE_BASE_PATH}{page_name}/{safe_name})\n\n"

        # Скачиваем изображение
        download_link = f"{SOURCE_URL}{img_src}"
        img = requests.get(download_link, timeout=10)
        img.raise_for_status()  # Проверяем успешность запроса

        # Создаем директории
        os.makedirs(f"{SAVE_DIR_PATH}{page_name}", exist_ok=True)
        os.makedirs(docus_save_path_dir, exist_ok=True)

        # Сохраняем файл
        with open(local_save_path, "wb") as f:
            f.write(img.content)
        with open(docus_save_path_file, "wb") as f:
            f.write(img.content)

        logger.info(f"Downloaded and saved: {safe_name}")
        return f"![]({DOCUS_IMAGE_BASE_PATH}{page_name}/{safe_name})\n\n"

    except Exception as e:
        logger.error(f"Error downloading image {img_src}: {str(e)}")
        return "Image Error"
