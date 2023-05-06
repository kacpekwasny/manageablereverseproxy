
import requests

from flask import request, Blueprint, Response as fResponse


from .app import app
from .config import SITE_NAME
from .wrapperclass import Request, Response
from .components import FIREWALL_IP, FIREWALL_IP_CONTROLLER
from .components.component_base import ComponentBase
from .components.controller_base import ControllerBase

ALL_HTTP_METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']


COMP_CONTR_PAIRS: list[tuple[ComponentBase, Blueprint]] = [
    (FIREWALL_IP, FIREWALL_IP_CONTROLLER,),
]
"""Currently active `(Component, Controller)` pairs"""

CONTROLLERS: list[Blueprint]     = [contr for comp, contr in COMP_CONTR_PAIRS]
COMPONENTS:  list[ComponentBase] = [comp  for comp, contr in COMP_CONTR_PAIRS]


for contr in CONTROLLERS:
    app.register_blueprint(contr)


@app.before_request
def before_every_request():
    """
    Every request will be passed all the components.
    """
    r = Request(request) # ??? will this cause any issues
    for component in COMPONENTS:
        r = component.process_request(r)

        if isinstance(r, Response):
            # the component decided to block the request, and thus returns a response.
            return r
        # is instance of Request, so the component did not block it



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




