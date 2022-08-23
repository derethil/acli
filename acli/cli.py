#!/bin/python
from functools import reduce
from os import environ

import arc
from arc import prompt, Context, logging, namespace, configure
from arc.types import State

from arc.present.table import Table
from arc.present.table import Column
from arc.present.data import justifications
from arc.color import fg, colorize

from .session import ASession
from .parser import ParseHTML
from .config import BASE_URL
from .utils import format_time

configure(environment="production", brand_color=fg.WHITE)

from .login import login

cli = namespace(name="acli")

# Login command object
cli.add_command(login)


class ACLIState(State):
    session: ASession


# Login decorator
@arc.decorator()
def login_required(ctx: Context):
    session: ASession = ctx.state["session"]
    session.login()


@login_required
@cli.subcommand(("punch", "p"))
def punch(state: ACLIState, *, comment: str = "", project_name: str = ""):
    """Clock in or out of Aggietime
    # Arguments
    comment: Comment for your supervisor
    project_name: Project name for current punch
    """

    to_status = ParseHTML(state.session.content).find_by_id("toStatus")

    res = state.session.post(
        url=f"{BASE_URL}/dashboard/clock/punch",
        data={
            "toStatus": to_status,
            "comment": comment,
            "projectName": project_name,
        },
    )

    direction = "into" if to_status == "IN" else "out of"
    if res.status_code == 200:
        print(colorize(f"Successfully punched {direction} Aggietime!", fg.BRIGHT_CYAN))
    else:
        print(colorize("Something went wrong :(", fg.RED))


@login_required
@cli.subcommand()
def status(state: ACLIState):
    """Indicate whether you are clocked in or out of Aggietime"""

    parser = ParseHTML(state.session.content)

    to_status: str = parser.find_by_id("toStatus")

    if to_status == "OUT":
        hours = parser.current_shift_hours()
        print(
            colorize(
                f"You're clocked in with {format_time(hours)} logged.", fg.BRIGHT_CYAN
            )
        )
    else:
        print(colorize("You're clocked out.", fg.BRIGHT_CYAN))


@login_required
@cli.subcommand()
def shifts(ctx: Context, state: ACLIState):
    """Select a shift and delete it from Aggietime's records."""
    parser = ParseHTML(state.session.content)

    parsed = parser.get_logged_hours()

    if parsed == []:
        total = 0.0
    else:
        total = reduce(lambda x, y: x + y, [float(row["hours"]) for row in parsed])

    table = Table(["Date", "Time In/Out", {"name": "Hours", "justify": "right"}])
    for row in parsed:
        table.add_row(
            [
                row["in_d"],
                f'{row["in_t"]:>8s} - {row["out_t"]:8s}',
                format_time(float(row["hours"])),
            ]
        )

    table.add_row([])
    table.add_row(["", "", format_time(total)])

    print(table)


def main():
    cli(state={"session": ASession()})
