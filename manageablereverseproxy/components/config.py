import json
from json.decoder import JSONDecodeError

import os.path as op


class ConfigBase:

    def __init__(self, fp: str) -> None:
        self._filepath = fp
        self._d = {}
        if op.exists(fp):
            self._load_file()
    
    def _save(self):
        with open(self._filepath, "w", encoding="utf-8") as f:
            json.dump(self._to_dict(), f)

    def _load_file(self):
        with open(self._filepath, "r", encoding="utf-8") as f:
            self._d = json.load(f)
            self._from_dict()

    def _to_dict(self) -> dict:
        return {
            k: getattr(self, k) for k in dir(self) if k[0] != "_"
        }

    def _from_dict(self):
        for k, v in self._d.items():
            setattr(self, k, v)
    
