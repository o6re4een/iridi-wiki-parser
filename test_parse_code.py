from bs4 import BeautifulSoup
from parser import convert_code_block

with open("code_sample.html", "r", encoding="utf-8") as f:
    html = f.read()

code = BeautifulSoup(html, "html.parser")
code_pre = code.find("pre")

md = convert_code_block(code_pre)
if md:
    with open("test_code_md.md", "w", encoding="utf-8") as f:
        f.write(md)
