from bs4 import BeautifulSoup


class ParseHTML:
    def __init__(self, html_content: bytes) -> None:
        self._soup = BeautifulSoup(html_content, "html5lib")

        self.s_token = self._parse_id("SYNCHRONIZER_TOKEN")
        self.s_uri = self._parse_id("SYNCHRONIZER_URI")
        self.pos_id = self._parse_id("posId")
        self.total_hours = self._parse_id("HoursThisWeek")
        self.entry_count = self._parse_id("entry-count")

        self.logged = self._parse_hours()

    def _parse_id(self, to_search: str) -> str:
        return self._soup.find(id=to_search).get("value")

    def _parse_hours(self):
        table = self._soup.find("table", id="pay-period").find_all("tbody")[0]

        hours_all = [hours.getText() for hours in table.find_all("td", class_="hours")]
        dates = [dates.getText() for dates in table.find_all("td", class_="date")]

        projects = [
            project.getText() for project in table.find_all("td", class_="projectName")
        ]

        return [
            [dates, hours, project]
            for hours, dates, project in zip(hours_all, dates, projects)
        ]
