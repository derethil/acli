#!/bin/python
from typing import Dict
from datetime import datetime

import requests

from arc import CLI
from arc import CommandType as ct

from .login import login, login_to_session
from .parser import parse_values
from .config import BASE_URL

cli = CLI()
cli.install_command(login)


@cli.subcommand(command_type=ct.POSITIONAL)
def log(total_hours: str, project_name=None):
    """Submits a single time log to Aggietime based on current date."""
    session, login_response = login_to_session(requests.Session())

    parsed: Dict[str, str] = parse_values(
        login_response.content,
        "SYNCHRONIZER_TOKEN",
        "SYNCHRONIZER_URI",
        "posId",
        "HoursThisWeek",
        "entry-count",
    )

    now = datetime.now()
    time_holder = now.strftime("%a, %d %b %Y")

    data: Dict[str, str] = {
        "SYNCHRONIZER_TOKEN": parsed["SYNCHRONIZER_TOKEN"],
        "SYNCHRONIZER_URI": parsed["SYNCHRONIZER_URI"],
        "posId": parsed["posId"],
        "HoursThisWeek": parsed["HoursThisWeek"],
        "entryCount": parsed["entry-count"],
        "entries[0].timeHolder": time_holder,
        "entries[0].totalHours": total_hours,
        "entries[0].projectName": project_name,
    }

    start_date = "01" if now.day <= 16 else "16"

    post_res = session.post(
        url=f"{BASE_URL}/dashboard/shift/save?startDate={now.strftime('%a')}+{now.strftime('%b')}+{start_date}+00%3A00%3A00+MDT+{now.strftime('%Y')}",
        data=data,
    )


def main():
    cli()