import logging
import os

import requests

logger = logging.getLogger(__name__)


from helpers.CONSTANTS import DOCUS_IMAGE_BASE_PATH, SAVE_DIR_PATH, SOURCE_URL
from .strs import sanitize_filename


def download_img(img_src: str, page_name: str) -> str:
    if img_src:
        # download_link = (
        #     f"{SOURCE_URL+img_src}" if not img_src.find("/images/") else None
        # )
        download_link = f"{SOURCE_URL+img_src}"
        # logger.info(f"download_link: {download_link}")
        if download_link:
            # print(download_link)
            img = requests.get(download_link, timeout=2)
            file_name = sanitize_filename(img_src.split("/")[-1])
            logger.info(f"file_name: {file_name}")
            os.makedirs(f"{SAVE_DIR_PATH}{page_name}", exist_ok=True)
            with open(f"{SAVE_DIR_PATH}{page_name}/{file_name}", "wb") as f:
                f.write(img.content)
            os.makedirs(f"my-website/static/img/{page_name}", exist_ok=True)
            # Сохраниние в локальный проект docusaurus
            with open(f"my-website/static/img/{page_name}/{file_name}", "wb") as f:
                if img:
                    f.write(img.content)

            return f"![{123}]({DOCUS_IMAGE_BASE_PATH+page_name+'/'+file_name})\n\n"
    return "Image Error"
