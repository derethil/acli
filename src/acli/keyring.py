import json
from datetime import datetime, timedelta

from keyring import get_password, set_password, delete_password
from arc.errors import ExecutionError

DEF_SERVICE = "aggietime"


# Login Interface


def get_login(*, service_name: str = DEF_SERVICE) -> tuple[str, str]:
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
    set_password(service_name, "username", username)
    set_password(service_name, username, password)


# Token Interface


def set_token(
    token: str,
    uri: str,
    pos_id: str,
    *,
    minutes: int = 15,
    service_name: str = DEF_SERVICE,
) -> None:

    expires_at = datetime.now() + timedelta(minutes=minutes)
    token_str = json.dumps(
        {
            "token": token,
            "uri": uri,
            "pos_id": pos_id,
            "expires_at": expires_at.isoformat(),
        }
    )

    set_password(service_name, "token", token_str)


def get_token(service_name: str = DEF_SERVICE) -> dict[str, str] | None:
    token_str = get_password(service_name, "token")

    if not token_str:
        return None

    try:
        return json.loads(token_str)

    except json.decoder.JSONDecodeError:
        raise ExecutionError("Keyring contains an invalid token structure")


def delete_token(service_name: str = DEF_SERVICE) -> None:
    delete_password(service_name, "token")
