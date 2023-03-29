import logging


class RequiresHeaderSanitation:
    """
    Parent class for ProxyComponent children, that will assume a header is absent.
    """

    headers_for_removal: list[str]
    """headers that class implementing RequiresHeaderSanitation wants to be removed"""


class HeaderSanitizer:
    """
    Remove all headers in the incoming request that are used by other Children of ProxyComponent classes.
    """

    headers_for_removal: list[str]
    lgr: logging.Logger

    def sanitize_for(self, components: list[RequiresHeaderSanitation]):
        """
        Register all components that have requests to do something with certain headers.
        """
        for component in components:
            for header in component.headers_for_removal:
                if header in self.headers_for_removal:
                    self.lgr.debug("'%s' wants to add header '%s', but header is allready present", str(component), header)
                    continue
                self.headers_for_removal.append(header)

