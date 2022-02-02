from keyring import get_password, set_password


def get_login(service_name: str = "aggietime") -> tuple[str, str]:
    username = get_password(service_name, "username")

    if not username:
        raise ValueError("Keyring does not contain username for ${service_name}")

    password = get_password(service_name, username)

    if not password:
        raise ValueError(
            "Keyring does not contain password for ${service_name} with username ${username}"
        )

    return (username, password)


def set_login(service_name: str, username: str, password: str) -> None:
    set_password(service_name, "username", username)  # Set username
    set_password(service_name, username, password)  # Set password
