


import requests

from flask import request, Blueprint, Response as fResponse

from datetime import datetime, timedelta, timezone
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, set_access_cookies, verify_jwt_in_request, unset_jwt_cookies
from flask_jwt_extended.jwt_manager import ExpiredSignatureError, NoAuthorizationError


from .app import app
from .config import SITE_NAME
from .wrapperclass import Request, Response
from .components import FIREWALL_IP, FIREWALL_IP_CONTROLLER
from .components import AUTHENTICATION, AUTHENTICATION_BP
from .components.component_base import ComponentBase

ALL_HTTP_METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']


COMP_CONTR_PAIRS: list[tuple[ComponentBase, Blueprint]] = [
    (FIREWALL_IP,       FIREWALL_IP_CONTROLLER,),
    (AUTHENTICATION,    AUTHENTICATION_BP),
]
"""Currently active `(Component, Controller)` pairs"""

CONTROLLERS: list[Blueprint]     = [contr for comp, contr in COMP_CONTR_PAIRS]
COMPONENTS:  list[ComponentBase] = [comp  for comp, contr in COMP_CONTR_PAIRS]


admin_panel = Blueprint("manageablereverseproxy", __name__, url_prefix="/mrp")

for contr in CONTROLLERS:
    admin_panel.register_blueprint(contr)

app.register_blueprint(admin_panel)


@app.before_request
def before_every_request():
    """
    Every request will be passed all the components.
    """
    r = Request(request) # ??? will this cause any issues
    print(f"{r.cookies=}")
    for component in COMPONENTS:
        r = component.process_request(r)
        print(r.user)

        if not isinstance(r, Request):
            # the component decided to [block / interacted with] the request, and thus returns a response.
            print("early return")
            return r
        # is instance of Request, so the component did not block it


# Using an `after_request` callback, we refresh any token that is within 30
# minutes of expiring. Change the timedeltas to match the needs of your application.
@app.after_request
def refresh_expiring_jwts(response):
    try:
        verify_jwt_in_request()
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError, ExpiredSignatureError, NoAuthorizationError) as e:
        print("unset")
        unset_jwt_cookies(response)
        # Case where there is not a valid JWT. Just return the original response
        return response


@app.route('/', defaults={'path': ''}, methods=ALL_HTTP_METHODS)
@app.route("/<path:path>", methods=ALL_HTTP_METHODS)
def proxy(path):

    r = requests.request(request.method,
                         f"{SITE_NAME}{path}",
                         params=request.values,
                         stream=False,
                         headers=request.headers,
                         allow_redirects=False,
                         data=request.data)

    # excluded_headers = ["content-encoding", "content-length", "transfer-encoding", "connection"]
    # headers = [(name, value) for (name, value) in r.raw.headers.items() if
    #                    name.lower() not in excluded_headers]


    return Response(fResponse(r.content, r.status_code, r.headers.items() ))





