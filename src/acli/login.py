from typing import Optional, Tuple

import keyring
import requests

from requests import Session, Response
from arc import namespace, command, Argument, Option, Flag, Count, Context
from arc.present import Table
from arc.present.table import Column
from arc.present.data import justifications
from arc.color import fg
from arc.errors import ExecutionError

from .config import BASE_URL
from .keyring import get_login, set_login

# CLI Commands


@command()
def login(
    ctx: Context,
    username: str,
    password: str,
    *,
    service_name="aggietime",
):
    """Sets your password using a keyring backend of your choice.
    # Arguments
    username: username to log into aggietime
    password: password to log into aggietime
    service_name: name of service to use for keyring
    """
    set_login(username, password, service_name=service_name)
    ctx.execute(display, service_name=service_name)


@login.subcommand()
def display(*, service_name="aggietime"):
    """Displays and checks if your current login information is correct.
    # Arguments
    service_name: name of service to use for keyring
    """
    username, password = get_login()

    if password == "" or password == None:
        show_login_info(service_name, username, f"{fg.RED}No password set")
        return

    assert isinstance(password, str)
    login_success = check_login(username, password)

    show_login_info(service_name, username, password, login_success)


# Helper Functions


def check_login(username: str, password: str) -> bool:
    login_res = requests.post(
        url=f"{BASE_URL}/j_spring_security_check",
        data={"j_username": username, "j_password": password},
    )

    return login_res.url == f"{BASE_URL}/dashboard"


def show_login_info(service_name: str, username: str, password: str, success=bool):
    rows = [
        ["Service Name", service_name],
        ["Username", username],
        ["Password", password],
    ]

    if success is not None:
        check_color = fg.GREEN if success else fg.RED
        rows.append(["Successful Login", f"{check_color}{success}"])

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

    print(Table(["Key", "Value"], rows, format_cell=format_cell))


def login_to_session(session: requests.Session) -> Tuple[Session, Response]:
    username, password = get_login()

    login_response = session.post(
        url=f"{BASE_URL}/j_spring_security_check",
        data={"j_username": username, "j_password": password},
    )

    if not login_response.url == f"{BASE_URL}/dashboard":
        raise ExecutionError("Incorrect username or password to Aggietime")

    return session, login_response
