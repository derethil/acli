from sys import base_prefix
from typing import Dict, List
from bs4 import BeautifulSoup
from arc.types import Alias


class ParseHTML:
    def __init__(self, html_content: bytes) -> None:
        self._soup = BeautifulSoup(html_content, "html5lib")

    def get_logged_hours(self) -> List[List[str]]:
        return self._parse_hours()

    def get_log_ids(self) -> List[int]:
        id_inputs = self._soup.find_all("input", attrs={"data-shiftid": True})
        return [int(item["data-shiftid"]) for item in id_inputs]

    def find_by_id(self, to_search: str) -> str:
        return self._soup.find(id=to_search).get("value")

    def _parse_hours(self):
        table = self._soup.find("table", id="pay-period").find("tbody")

        def get_el(class_: str, *, el: str = "span") -> list[str]:
            els = [el.getText().strip() for el in table.find_all(el, class_=class_)]
            els.reverse()
            return els

        in_times = get_el("in-time")
        out_times = get_el("out-time")
        in_dates = get_el("in-date")
        out_dates = get_el("out-date")

        all_hours = list(filter(None, get_el("hours", el="td")))

        return [
            {"in_t": x[0], "out_t": x[1], "in_d": x[2], "out_d": x[3], "hours": x[4]}
            for x in zip(in_times, out_times, in_dates, out_dates, all_hours)
        ]
