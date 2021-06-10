#!/bin/python
from typing import Dict
from datetime import datetime

import requests

from arc import CLI
from arc import CommandType as ct
from arc.present import Table
from arc.color import fg

cli = CLI(name="acli", version="0.1.0")

from .login import login, login_to_session
from .parser import ParseHTML
from .config import BASE_URL

cli.install_command(login)


@cli.subcommand(command_type=ct.POSITIONAL)
def log(hours_to_log: str, project_name=None):
    """Submits a single time log to Aggietime based on current date."""
    session, login_response = login_to_session(requests.Session())
    login_res = ParseHTML(login_response.content)

    now = datetime.now()
    time_holder = now.strftime("%a, %d %b %Y")

    data: Dict[str, str] = {
        "SYNCHRONIZER_TOKEN": login_res.s_token,
        "SYNCHRONIZER_URI": login_res.s_uri,
        "posId": login_res.pos_id,
        "HoursThisWeek": login_res.total_hours,
        "entryCount": login_res.entry_count,
        "entries[0].timeHolder": time_holder,
        "entries[0].totalHours": hours_to_log,
        "entries[0].projectName": project_name,
    }

    start_date = "01" if now.day <= 16 else "16"
    post_res = session.post(
        url=f"{BASE_URL}/dashboard/shift/save?startDate={now.strftime('%a')}+{now.strftime('%b')}+{start_date}+00%3A00%3A00+MDT+{now.strftime('%Y')}",
        data=data,
    )

    parsed_post = ParseHTML(post_res.content)

    prev_total = float(login_res.total_hours) + float(hours_to_log)

    if float(parsed_post.total_hours) == prev_total:
        print(f"{fg.GREEN}\nSuccessfully logged {hours_to_log} hours to Aggietim!")
    else:
        print(f"{fg.RED}Log request to Aggieietime unsuccessful.")

    hours(parsed_post)


@cli.subcommand()
def hours(parsed=None):
    """Displays your submitted hours for the current pay period."""
    if parsed is None:
        session, response = login_to_session(requests.Session())
        parsed = ParseHTML(response.content)

    parsed.logged.extend([["", "", ""], ["Total", parsed.total_hours, ""]])

    print(Table(["Date", "Hours", "Project"], parsed.logged))


def main():
    cli()
