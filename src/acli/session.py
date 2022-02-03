from datetime import datetime
from requests import Session, Response

from arc import ExecutionError

from .keyring import get_login, set_token, get_token, delete_token
from .config import BASE_URL
from .parser import ParseHTML


class ASession:
    def __init__(self):
        self._session = Session()
        self._token = None
        self._uri = None
        self._pos_id = None

        self._load_token()

    def login(self) -> bytes:
        username, password = get_login()

        res = self._session.post(
            url=f"{BASE_URL}/j_spring_security_check",
            data={"j_username": username, "j_password": password},
        )

        if not res.url == f"{BASE_URL}/dashboard":
            raise ExecutionError("Incorrect username or password to Aggietime")

        self._synchronize(res.content)

        return res.content

    def logged_in(self) -> bool:
        return self._token != None

    def _synchronize(self, content: bytes) -> None:
        parser = ParseHTML(content)

        self._token = parser.find_by_id("SYNCHRONIZER_TOKEN")
        self._uri = parser.find_by_id("SYNCHRONIZER_URI")
        self._pos_id = parser.find_by_id("posId")

        set_token(self._token, self._uri, self._pos_id)

    def _load_token(self) -> None:
        token = get_token()

        if not token:
            return

        expires_at = datetime.fromisoformat(token["expires_at"])

        if datetime.now() >= expires_at:
            delete_token()
            return

        self._token = token["token"]
        self._uri = token["uri"]
        self._pos_id = token["pos_id"]
