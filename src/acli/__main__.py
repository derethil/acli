#!/bin/python
from typing import Dict
from datetime import datetime

from requests import Session, Response

from arc import CLI, State, callback, prompt, Context, logging
from arc.present import Table
from arc.color import fg, colorize
from arc.errors import ValidationError

from acli.session import ASession


from .login import login, login_to_session
from .parser import ParseHTML
from .config import BASE_URL


cli = CLI(
    name="acli",
    env="development",
    state={"session": ASession()},
)

# Login command object
cli.install_command(login)

# Login decorator
@callback.create()
def login_required(args, ctx: Context):
    session: ASession = ctx.state["session"]

    if not session.logged_in():
        print("Logging in...")
        session.login()

    try:
        yield
    finally:
        print("end")


@login_required
@cli.subcommand()
def log(hours_to_log: float, state: State, project_name=None):

    session: ASession = state["session"]

    print(session.logged_in())
    """Submits a single time log to Aggietime based on current date."""
    # session, login_response = login_to_session(Session())
    # data_to_post = ParseHTML(login_response.content).get_post_data()

    # now = datetime.now()
    # time_holder = now.strftime("%a, %d %b %Y")

    # data: Dict[str, str] = {
    #     "SYNCHRONIZER_TOKEN": data_to_post["s_token"],
    #     "SYNCHRONIZER_URI": data_to_post["s_uri"],
    #     "posId": data_to_post["pos_id"],
    #     "HoursThisWeek": data_to_post["total_hours"],
    #     "entryCount": data_to_post["entry_count"],
    #     "entries[0].timeHolder": time_holder,
    #     "entries[0].totalHours": str(hours_to_log),
    #     "entries[0].projectName": project_name,
    # }

    # start_date = "01" if now.day <= 16 else "16"
    # post_res = session.post(
    #     url=f"""{BASE_URL}/dashboard/shift/save?startDate=
    #             {now.strftime('%a')}+{now.strftime('%b')}+{start_date}+
    #             00%3A00%3A00+MDT+{now.strftime('%Y')}""",
    #     data=data,
    # )

    # post_parser = ParseHTML(post_res.content)
    # post_res_data = post_parser.get_post_data()

    # if (
    #     float(post_res_data["total_hours"])
    #     == float(data_to_post["total_hours"]) + hours_to_log
    # ):
    #     print(colorize("\nSuccessfully logged {hours_to_log} hours!", fg.GREEN))
    # else:
    #     print(colorize("Log request to Aggietime unsuccessful."), fg.RED)

    # hours(post_parser)


@cli.subcommand()
def hours():
    """Displays your submitted hours for the current pay period."""
    session, response = login_to_session(Session())
    parser = ParseHTML(response.content)

    logged_hours = parser.get_logged_hours()
    total_hours = parser.get_post_data()["total_hours"]

    logged_hours.reverse()
    logged_hours.extend([["", "", ""], ["Total", total_hours, ""]])

    print(Table(["    Date", "Hours", "Project"], logged_hours))


@cli.subcommand()
def delete(log_id: int):
    """Deletes a log entry from Aggietime."""
    session, login_response = login_to_session(Session())
    parser = ParseHTML(login_response.content)
    reversed_log_ids = parser.get_log_ids()[::-1]

    if log_id - 1 in range(len(reversed_log_ids)):
        log_id_to_delete = reversed_log_ids[log_id - 1]
    else:
        raise ValidationError("Requested log entry does not exist")

    post_response: Response = session.post(
        url=f"{BASE_URL}/dashboard/shift/delete", data={"id": log_id_to_delete}
    )

    if post_response.json().get("success") == "Shift successfully deleted":
        print(f"\n{fg.GREEN}Shift {log_id} successfully deleted!")
    else:
        print(f"{fg.RED}Shift deletion unsuccessful. An error occured")

    hours()


def main():
    cli()
