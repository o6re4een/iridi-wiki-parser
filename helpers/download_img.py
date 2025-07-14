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
            file_name = sanitize_filename(img_src.split("/")[-1])
            # print(download_link)
            local_save_path = f"{SAVE_DIR_PATH}{page_name}/{file_name}"
            docus_save_path_dir = f"my-website/static/img/{page_name}"
            docus_save_path_file = f"my-website/static/img/{page_name}/{file_name}"

            is_downloaded = os.path.exists(local_save_path) and os.path.exists(
                docus_save_path_file
            )
            if is_downloaded:
                logger.info(f"Already downloaded: {file_name}")
                return f"![{123}]({DOCUS_IMAGE_BASE_PATH+page_name+'/'+file_name})\n\n"

            img = requests.get(download_link, timeout=2)

            logger.info(f"file_name: {file_name}")
            os.makedirs(f"{SAVE_DIR_PATH}{page_name}", exist_ok=True)

            with open(local_save_path, "wb") as f:
                f.write(img.content)
            os.makedirs(docus_save_path_dir, exist_ok=True)
            # Сохраниние в локальный проект docusaurus
            with open(docus_save_path_file, "wb") as f:
                f.write(img.content)

            return f"![{123}]({DOCUS_IMAGE_BASE_PATH+page_name+'/'+file_name})\n\n"
    return "Image Error"
