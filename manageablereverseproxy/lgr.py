import logging


logging.basicConfig(level=0)


class InheritLogger:
    """
    `self.lgr = Logger()`
    """

    lgr: logging.Logger = logging.getLogger("firewall")
    lgr.setLevel(logging.DEBUG)


