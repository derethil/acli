import requests
from bs4 import BeautifulSoup

BASE_URL = "https://aggietime.usu.edu"

session = requests.Session()

login_res = session.post(
    url=f"{BASE_URL}/j_spring_security_check",
    data={"j_username": "", "j_password": ""},
)

soup = BeautifulSoup(login_res.content, "html.parser")

post_res = session.post(
    url=f"https://aggietime.usu.edu/dashboard/shift/save?startDate=Tue+Jun+01+00%3A00%3A00+MDT+2021",
    data={
        "SYNCHRONIZER_TOKEN": soup.find(id="SYNCHRONIZER_TOKEN").get("value"),
        "SYNCHRONIZER_URI": soup.find(id="SYNCHRONIZER_URI").get("value"),
        "posId": soup.find(id="posId").get("value"),
        "HoursThisWeek": soup.find(id="HoursThisWeek").get("value"),
        "entryCount": soup.find(id="entry-count").get("value"),
        "entries[0].timeHolder": "Tue, 08 Jun 2021",
        "entries[0].totalHours": 8,
        "entries[0].projectName": "test",
    },
)
