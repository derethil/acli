import requests

from arc import command, Argument, Context

from arc.present.table import Table
from arc.types import Password

from .config import BASE_URL
from .keyring import get_login, set_login

# CLI Commands


@command()
def login(
    ctx: Context,
    username: str = Argument(prompt="Enter your ANumber:"),
    password: Password = Argument(prompt="Enter your Password:"),
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
    service_name: Name of service to use for keyring
    """
    username, password = get_login()

    if password == "" or password == None:
        show_login_info(service_name, username)
        return

    assert isinstance(password, str)
    login_success = check_login(username, password)

    show_login_info(service_name, username, login_success)


# Helper Functions


def check_login(username: str, password: str) -> bool:
    """Returns whether or not the saved login information is correct."""
    login_res = requests.post(
        url=f"{BASE_URL}/j_spring_security_check",
        data={"j_username": username, "j_password": password},
    )

    return login_res.url == f"{BASE_URL}/dashboard"


def show_login_info(service_name: str, username: str, success=bool):
    """Prints a table containing the stored login to Aggietime."""
    rows = [
        ["Service Name", service_name],
        ["Username", username],
        ["Successful Login", success],
    ]

    table = Table(["Key", "Value"])
    for row in rows:
        table.add_row(row)

    print(table)
