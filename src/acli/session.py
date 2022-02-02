from requests import Session

from .keyring import get_login_info


class ASession:
    def __init__(self):
        self.session = Session()

    def login(self):
        pass
