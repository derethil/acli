from typing import Optional

import keyring
import requests
from arc import namespace
from arc.present import Table
from arc.present.table import Column
from arc.present.data import justifications
from arc.color import fg

from config import BASE_URL

login = namespace("login")


# CLI Commands


@login.subcommand()
def set(username: str, password: str, service_name="aggietime"):
    """Sets your password using a keyring backend of your choice."""
    keyring.set_password(service_name, username, password)
    get(username=username)


@login.subcommand()
def get(username: str, service_name="aggietime"):
    """Displays and checks if your current login information is correct."""
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
