from keyring import get_password, set_password
from arc.errors import ExecutionError


def get_login(service_name: str = "aggietime") -> tuple[str, str]:
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


def set_login(service_name: str, username: str, password: str) -> None:
    set_password(service_name, "username", username)
    set_password(service_name, username, password)
