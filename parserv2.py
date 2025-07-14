from typing import List
import logging

logger = logging.getLogger(__name__)


class Parser:
    links: List[str]

    def __init__(self):
        with open("to_parse.txt", "r") as f:
            for line in f:
                link = line.strip()
                self.links.append(link)

    def parse_single(self, link):
        if link:
            headers = {
                "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
                "Content-Language": "ru",
            }
            cookies = {
                "irmob_wiki3language": "ru",
            }

    def parse_many(self):
        for link in self.links:
            logger.info(f"Parsing {link}")
            self.parse_single(link)
