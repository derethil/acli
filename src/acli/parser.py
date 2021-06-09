from typing import Dict
from bs4 import BeautifulSoup


def parse_values(html_content: bytes, *args: str) -> Dict[str, str]:
    soup = BeautifulSoup(html_content, "html.parser")

    values: Dict[str, str] = {}

    for arg in args:
        values[arg] = soup.find(id=arg).get("value")

    return values
