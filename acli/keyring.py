from datetime import datetime, timedelta

from keyring import get_password, set_password
from arc.errors import ExecutionError

DEF_SERVICE = "aggietime"


# Login Interface


def get_login(*, service_name: str = DEF_SERVICE) -> tuple[str, str]:
    """Return the username and password to Aggietime stored in the keyring"""
    username = get_password(service_name, "username")

    if not username:
        raise ExecutionError(
            f'Keyring does not contain username for service "{service_name}"'
        )

    password = get_password(service_name, username)

    if not password:
        raise ExecutionError(
            f'Keyring does not contain password for service "{service_name}" with username "{username}"'
        )

    return (username, password)


def set_login(username: str, password: str, *, service_name: str = DEF_SERVICE) -> None:
    """Set Aggietime login information in the keyring"""
    set_password(service_name, "username", username)
    set_password(service_name, username, password)
