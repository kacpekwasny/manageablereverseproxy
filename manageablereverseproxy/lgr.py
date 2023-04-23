import logging


logging.basicConfig(level=0)


class InheritLogger:

    lgr: logging.Logger = logging.getLogger("firewall")
    lgr.setLevel(logging.DEBUG)


