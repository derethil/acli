from bs4 import BeautifulSoup
from datetime import datetime


class ParseHTML:
    def __init__(self, html_content: bytes) -> None:
        self._soup = BeautifulSoup(html_content, "html5lib")

    def get_logged_hours(self) -> list[dict[str, str]]:
        """Return all shift dates and times (not including the current shift)"""
        return self._parse_hours()

    def get_log_ids(self) -> list[int]:
        """Get shiftids for all logged shifts"""
        id_inputs = self._soup.find_all("input", attrs={"data-shiftid": True})
        return [int(item["data-shiftid"]) for item in id_inputs]

    def find_by_id(self, id: str) -> str:
        """Find any tag with an `id` and return its value"""
        return self._soup.find(id=id).get("value")

    def current_shift_hours(self) -> float:
        """Return the current shift length in hours"""
        current_row = self._soup.find("table", id="pay-period").find("tbody").find("tr")

        if current_row.find("span", class_="out-time bold"):
            raise RuntimeError("Can't get current shift length if clocked out")

        time_in = current_row.find("span", class_="in-time bold").get_text().strip()
        date_in = current_row.find("span", class_="in-date smaller").get_text().strip()

        datetime_in = datetime.strptime(f"{time_in} {date_in}", "%I:%M %p %m/%d/%y")
        now = datetime.now()

        current_shift_length = (now - datetime_in).total_seconds() / 60 / 60
        return current_shift_length

    def _parse_hours(self):
        """Prase the HTML to return shift dates and times"""
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

        shifts = [
            {"in_t": x[0], "out_t": x[1], "in_d": x[2], "out_d": x[3], "hours": x[4]}
            for x in zip(in_times, out_times, in_dates, out_dates, all_hours)
        ]

        if len(in_times) > len(out_times):
            shifts.append(
                {
                    "in_t": in_times[-1],
                    "out_t": "",
                    "in_d": in_dates[-1],
                    "out_d": "",
                    "hours": self.current_shift_hours(),
                }
            )

        return shifts
