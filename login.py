from typing import Optional, Tuple

import keyring
import requests
from requests import Session, Response
from arc import namespace
from arc.present import Table
from arc.present.table import Column
from arc.present.data import justifications
from arc.color import fg
from arc.errors import ExecutionError

from config import BASE_URL

login = namespace("login")


# CLI Commands


@login.subcommand()
def set(username: str, password: str, service_name="aggietime"):
    """Sets your password using a keyring backend of your choice."""
    keyring.set_password(service_name, "username", username)  # Set username
    keyring.set_password(service_name, username, password)  # Set password
    display()


@login.subcommand()
def display(service_name="aggietime"):
    """Displays and checks if your current login information is correct."""
    username = keyring.get_password(service_name, "username")
    password: Optional[str] = keyring.get_password(service_name, username)

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


def show_login_info(
    service_name: str, username: str, password: str, checked: Optional[bool] = None
):
    rows = [
        ["Service Name", service_name],
        ["Username", username],
        ["Password", password],
    ]

    if checked is not None:
        check_color = fg.GREEN if checked else fg.RED
        rows.append(["Successful Login", f"{check_color}{checked}"])

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


def get_login_info(service_name="aggietime"):
    username: Optional[str] = keyring.get_password(service_name, "username")
    password: Optional[str] = keyring.get_password(service_name, username)

    return (username, password)


def login_to_session(session: requests.Session) -> Tuple[Session, Response]:
    usernmame, password = get_login_info()
    login_success = check_login(usernmame, password)

    if not login_success:
        raise ExecutionError("Could not log in to Aggietime successfully")

    login_response = session.post(
        url=f"{BASE_URL}/j_spring_security_check",
        data={"j_username": usernmame, "j_password": password},
    )

    return session, login_response
