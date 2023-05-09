
from flask import Response


class MyResponse(Response):
    logout: bool = False
    """This is a logout response (it has headers to unset cookies) do not refresh cookies."""

    def logout_flag(self) -> None:
        self.logout = True

