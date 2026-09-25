#!/usr/bin/env python3
"""Small dependency-free uRADMonitor EXP/DIDAP mock server.

Run:
    python3 urad_mock.py

ESP test credentials:
    X-User-id: test
    X-User-hash: test

Environment variables:
    MOCK_HOST=0.0.0.0
    MOCK_PORT=8080
    MOCK_DEVICE_ID=13ABC001
    MOCK_DELAY_MS=0
    MOCK_FAIL_EVERY_N=0
    MOCK_LOG_FILE=urad_mock.ndjson
"""

from __future__ import annotations

import json
import os
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock
from urllib.parse import urlparse

HOST = os.getenv("MOCK_HOST", "0.0.0.0")
PORT = int(os.getenv("MOCK_PORT", "8080"))
DEVICE_ID = os.getenv("MOCK_DEVICE_ID", "13ABC001").upper()
DELAY_MS = int(os.getenv("MOCK_DELAY_MS", "0"))
FAIL_EVERY_N = int(os.getenv("MOCK_FAIL_EVERY_N", "0"))
LOG_FILE = Path(os.getenv("MOCK_LOG_FILE", "urad_mock.ndjson"))
EXPECTED_USER = os.getenv("MOCK_USER_ID", "test")
EXPECTED_HASH = os.getenv("MOCK_USER_HASH", "test")

lock = Lock()
request_counter = 0
last_timestamp_by_device: dict[str, int] = {}
recent_events: list[dict] = []


def log_event(event: dict) -> None:
    event["server_time"] = int(time.time())
    line = json.dumps(event, separators=(",", ":"), ensure_ascii=False)
    with lock:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
        recent_events.append(event)
        if len(recent_events) > 100:
            del recent_events[:-100]
    print(line, flush=True)


def parse_exp(body: str) -> dict[str, str]:
    if not body:
        return {}
    parts = [p for p in body.strip().split("/") if p != ""]
    if len(parts) % 2:
        raise ValueError("EXP body must contain id/value pairs")
    return {parts[i].upper(): parts[i + 1] for i in range(0, len(parts), 2)}


class Handler(BaseHTTPRequestHandler):
    server_version = "uRADMock/1.0"

    def _json(self, status: int, obj: dict | list) -> None:
        raw = json.dumps(obj, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/status":
            with lock:
                snapshot = list(recent_events[-20:])
            self._json(200, {
                "service": "uRADMonitor mock",
                "device_id": DEVICE_ID,
                "requests": request_counter,
                "recent": snapshot,
            })
            return
        if path == "/health":
            self._json(200, {"ok": True})
            return
        self._json(404, {"error": "not found"})

    def do_POST(self) -> None:
        global request_counter

        path = urlparse(self.path).path
        if path != "/api/v1/upload/exp/":
            self._json(404, {"error": "wrong endpoint"})
            return

        request_counter += 1
        if DELAY_MS > 0:
            time.sleep(DELAY_MS / 1000.0)
        if FAIL_EVERY_N > 0 and request_counter % FAIL_EVERY_N == 0:
            log_event({"type": "forced_failure", "request": request_counter})
            self._json(503, {"error": "forced test failure"})
            return

        user_id = self.headers.get("X-User-id", "")
        user_hash = self.headers.get("X-User-hash", "")
        device_id = self.headers.get("X-Device-id", "").upper()

        if user_id != EXPECTED_USER or user_hash != EXPECTED_HASH:
            log_event({"type": "auth_failure", "user_id": user_id, "device_id": device_id})
            self._json(401, {"error": "authentication failed"})
            return

        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8", errors="replace")

        if device_id in {"", "0", "00000000", "FFFFFFFF", "13000000"}:
            log_event({"type": "register", "device_id": device_id})
            self._json(200, {"setid": DEVICE_ID})
            return

        if device_id != DEVICE_ID:
            log_event({"type": "wrong_device", "device_id": device_id})
            self._json(403, {"error": "device id not bound to this mock account"})
            return

        try:
            fields = parse_exp(body)
        except ValueError as exc:
            log_event({"type": "bad_payload", "device_id": device_id, "body": body})
            self._json(400, {"error": str(exc)})
            return

        if "01" not in fields:
            self._json(400, {"error": "field 01 timestamp is mandatory"})
            return
        try:
            timestamp = int(fields["01"])
        except ValueError:
            self._json(400, {"error": "field 01 must be an integer epoch timestamp"})
            return

        previous = last_timestamp_by_device.get(device_id)
        if previous is not None and timestamp <= previous:
            self._json(409, {"error": "timestamp must increase", "previous": previous})
            return
        last_timestamp_by_device[device_id] = timestamp

        if "0B" in fields:
            try:
                float(fields["0B"])
            except ValueError:
                self._json(400, {"error": "field 0B CPM must be numeric"})
                return

        log_event({
            "type": "upload",
            "device_id": device_id,
            "fields": fields,
        })
        self._json(200, {"success": "ok"})

    def log_message(self, format: str, *args) -> None:
        # Keep output focused on structured events above.
        return


if __name__ == "__main__":
    print(f"uRAD mock listening on http://{HOST}:{PORT}")
    print(f"Health: http://127.0.0.1:{PORT}/health")
    print(f"Status: http://127.0.0.1:{PORT}/status")
    print(f"Log: {LOG_FILE.resolve()}")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
