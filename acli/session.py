from datetime import datetime
from requests import Session, Response

from arc import ExecutionError

from .keyring import get_login
from .config import BASE_URL
from .parser import ParseHTML


class ASession:
    def __init__(self):
        self._session = Session()
        self._token = None
        self._uri = None
        self._pos_id = None

        self._login_res_url = None
        self.content = None

    def login(self) -> bytes:
        """Log in to Aggietime & store the main page"""
        username, password = get_login()

        res = self._session.post(
            url=f"{BASE_URL}/j_spring_security_check",
            data={"j_username": username, "j_password": password},
        )

        if not res.url == f"{BASE_URL}/dashboard":
            raise ExecutionError("Incorrect username or password to Aggietime")

        self._synchronize(res)
        self.content = res.content

        return res.content

    def logged_in(self) -> bool:
        return self._token != None

    def post(self, *, url, data) -> Response:
        """Make a post request to Aggietime"""
        data.update(self._construct_token_body())

        return self._session.post(
            url=url, data=data, headers=self._construct_headers(data)
        )

    def get(self, *, url) -> Response:
        """Make a get request to Aggietime"""
        data = self._construct_token_body()

        return self._session.get(
            url=url,
            headers=self._construct_headers(data),
            data=data,
        )

    def _synchronize(self, res: Response) -> None:
        parser = ParseHTML(res.content)

        self._token = parser.find_by_id("SYNCHRONIZER_TOKEN")
        self._uri = parser.find_by_id("SYNCHRONIZER_URI")
        self._pos_id = parser.find_by_id("posId")

        self._login_res_url = res.request.url

    def _construct_headers(self, data: dict[str, str]) -> dict[str, str]:
        return {
            "HOST": "aggietime.usu.edu",
            "CONTENT_TYPE": "application/x-www-form-urlencoded",
            "ORIGIN": "https://aggietime.usu.edu",
            "ACCEPT_ENCODING": "gzip, deflate, br",
            "CONNECTION": "keep-alive",
            "ACCEPT": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "USER_AGENT": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.55 Safari/537.36 Edg/98.0.1108.27",
            "REFERER": f"{self._login_res_url}",
            "ACCEPT_LANGUAGE": "en-us",
            "CONTENT_LENGTH": f"{len(str(data))}",
        }

    def _construct_token_body(self):
        return {
            "SYNCHRONIZER_TOKEN": self._token,
            "SYNCHRONIZER_URI": self._uri,
            "posId": self._pos_id,
        }
