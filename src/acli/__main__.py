#!/bin/python
from typing import Dict
from datetime import datetime

from requests import Session, Response

from arc import CLI, State, callback, prompt, Context, logging
from arc.present import Table
from arc.color import fg, colorize
from arc.errors import ValidationError

from acli.session import ASession


from .login import login
from .parser import ParseHTML
from .config import BASE_URL


cli = CLI(
    name="acli",
    env="production",
    state={"session": ASession()},
)

# Login command object
cli.install_command(login)

# Login decorator
@callback.create()
def login_required(args, ctx: Context):
    session: ASession = ctx.state["session"]
    session.login()

    try:
        yield
    finally:
        pass


@login_required
@cli.subcommand()
def punch(state: State, comment: str = "", project_name: str = ""):
    """Clock in or out of Aggietime"""
    session: ASession = state["session"]
    to_status = ParseHTML(session.content).find_by_id("toStatus")

    res = session.post(
        url=f"{BASE_URL}/dashboard/clock/punch",
        data={
            "toStatus": to_status,
            "comment": comment,
            "projectName": project_name,
        },
    )

    match to_status:
        case "IN":
            direction = "into"
        case "OUT":
            direction = "out of"

    if res.status_code == 200:
        print(colorize(f"Successfully punched {direction} Aggietime!", fg.BRIGHT_CYAN))
    else:
        print(colorize("Something went wrong :(", fg.RED))


@login_required
@cli.subcommand()
def status(state: State):
    """Indicate whether you are clocked in or out of Aggietime"""
    session: ASession = state["session"]
    to_status = ParseHTML(session.content).find_by_id("toStatus")

    if to_status == "OUT":
        print(colorize("You're clocked in.", fg.BRIGHT_CYAN))
    else:
        print(colorize("You're clocked out.", fg.BRIGHT_CYAN))


def main():
    cli()
