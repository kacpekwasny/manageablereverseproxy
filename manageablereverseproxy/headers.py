from enum import Enum

class HeadersPublic(Enum):
    # Private headers
    USER_ID    = "Mrp-User-Id"
    USER_TOKEN = "Mrp-User-Token"


class HeadersPrivate(Enum):
    # Private headers
    USERNAME  = "Priv-Mrp-Username"
    USER_ID   = "Priv-Mrp-User-Id"
    USER_ROLES = "Priv-Mrp-User-Role"