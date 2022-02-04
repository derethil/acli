from sys import base_prefix
from typing import Dict, List
from bs4 import BeautifulSoup
from arc.types import Alias


class ParseHTML:
    def __init__(self, html_content: bytes) -> None:
        self._soup = BeautifulSoup(html_content, "html5lib")

    def get_post_data(self) -> Dict[str, str]:
        data_to_post: Dict[str, str] = {
            "s_token": self.find_by_id("SYNCHRONIZER_TOKEN"),
            "s_uri": self.find_by_id("SYNCHRONIZER_URI"),
            "pos_id": self.find_by_id("posId"),
            "entry_count": self.find_by_id("entry-count"),
            "total_hours": self.find_by_id("HoursThisWeek"),
        }

        return data_to_post

    def get_logged_hours(self) -> List[List[str]]:
        return self._parse_hours()

    def get_log_ids(self) -> List[int]:
        id_inputs = self._soup.find_all("input", attrs={"data-shiftid": True})
        return [int(item["data-shiftid"]) for item in id_inputs]

    def find_by_id(self, to_search: str) -> str:
        return self._soup.find(id=to_search).get("value")

    def _parse_hours(self) -> List[List[str]]:
        table = self._soup.find("table", id="pay-period").find_all("tbody")[0]

        hours_all = [hours.getText() for hours in table.find_all("td", class_="hours")]
        dates = [dates.getText() for dates in table.find_all("td", class_="date")]

        projects = [
            project.getText() for project in table.find_all("td", class_="projectName")
        ]

        log_ids = self.get_log_ids()
        reversed_log_ids = log_ids[::-1]

        return [
            [f"({reversed_log_ids.index(log_id) + 1}) {date}", hours, project]
            for hours, date, project, log_id in zip(hours_all, dates, projects, log_ids)
        ]
