#!/bin/python
from arc import CLI, State, callback, prompt, Context, logging
from arc.present import Table
from arc.present.table import Column
from arc.present.data import justifications
from arc.color import fg, colorize

from .session import ASession
from .login import login
from .parser import ParseHTML
from .config import BASE_URL
from .utils import format_time


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
    session.login()

    try:
        yield
    finally:
        pass


@login_required
@cli.subcommand()
def punch(state: State, *, comment: str = "", project_name: str = ""):
    """Clock in or out of Aggietime
    # Arguments
    comment: Comment for your supervisor
    project_name: Project name for current punch
    """

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

    direction = "into" if to_status == "IN" else "out of"
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


@login_required
@cli.subcommand()
def list(state: State):
    """Select a shift and delete it from Aggietime's records."""

    session: ASession = state["session"]
    parser = ParseHTML(session.content)

    parsed = parser.get_logged_hours()

    rows = [
        [
            row["in_d"],
            f'{row["in_t"]} - {row["out_t"]}',
            format_time(float(row["hours"])),
        ]
        for row in parsed
    ]

    def format_cell(content, column: Column, row_idx, column_idx):
        return (
            Table.formatter(
                string=content,
                width=column["width"],
                align=justifications[column["justify"]],
                tcolor=f"{fg.WHITE}",
            )
            + " "
        )

    print(Table(["Date", "Time In/Out", "Hours"], rows=rows, format_cell=format_cell))
