"""Test doubles shared by unit tests and the screenshot harness."""
import threading

from wordduel.core import online


class FakeFirestore:
    """In-memory stand-in honouring updateMask and preconditions."""

    def __init__(self):
        self.docs = {}
        self.clock = 0
        self.lock = threading.RLock()

    def request(self, method, code, body=None, params=None):
        with self.lock:
            return self._request(method, code, body, params)

    def _request(self, method, code, body=None, params=None):
        params = params or []
        doc = self.docs.get(code)
        if method == "GET":
            return dict(doc) if doc else None
        p = dict((k, v) for k, v in params if not k.startswith("updateMask"))
        if p.get("currentDocument.exists") == "false" and doc:
            raise online.Conflict("exists")
        if "currentDocument.updateTime" in p and (not doc or doc["updateTime"] != p["currentDocument.updateTime"]):
            raise online.Conflict("stale")
        mask = [v for k, v in params if k == "updateMask.fieldPaths"]
        fields = dict(doc["fields"]) if doc else {}
        for k in mask:
            fields[k] = body["fields"][k]
        self.clock += 1
        self.docs[code] = {"fields": fields, "updateTime": f"t{self.clock}"}
        return dict(self.docs[code])
