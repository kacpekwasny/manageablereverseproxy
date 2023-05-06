from __future__ import annotations

import logging
import sys


# logging.basicConfig(level=100)


class InheritLogger:
    lvl = logging.DEBUG
    lgr: logging.Logger = logging.getLogger("mrp")
    h = logging.StreamHandler(sys.stdout)

    h.setLevel(lvl)
    lgr.addHandler(h)
    lgr.setLevel(lvl)
    
    @classmethod
    def set_logger_by_name(cls, lgr_name):
        """To overwrite the deafult logger"""
        cls.lgr = logging.getLogger(lgr_name)

    @classmethod
    def set_lgr_level(cls, lvl: int):
        for h in cls.lgr.handlers:
            h.setLevel(lvl)
        
        cls.lgr.setLevel(lvl)


