from __future__ import annotations

import json
from io import BytesIO

from apps.web import main


def _call_app(path: str) -> tuple[str, list[tuple[str, str]], bytes]:
    status_container: list[str] = []
    headers_container: list[list[tuple[str, str]]] = []

    def start_response(status: str, headers: list[tuple[str, str]]) -> None:
        status_container.append(status)
        headers_container.append(headers)

    environ = {
        "REQUEST_METHOD": "GET",
        "PATH_INFO": path,
        "SERVER_NAME": "test",
        "SERVER_PORT": "80",
        "wsgi.version": (1, 0),
        "wsgi.url_scheme": "http",
        "wsgi.input": BytesIO(),
        "wsgi.errors": BytesIO(),
        "wsgi.multithread": False,
        "wsgi.multiprocess": False,
        "wsgi.run_once": False,
    }
    body_chunks = list(main.application(environ, start_response))
    body = b"".join(body_chunks)
    return status_container[0], headers_container[0], body


def test_healthz_returns_ok() -> None:
    status, headers, body = _call_app("/healthz")
    assert status.startswith("200")
    payload = json.loads(body.decode())
    assert payload["status"] == "ok"
